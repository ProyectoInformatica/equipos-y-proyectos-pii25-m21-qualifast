import flet as ft
import flet_video as fv
import threading
import time
import random
import requests
from datetime import datetime
import modelo.manejador_datos as modelo
from vista import vista_login, vista_dashboard_sensores, vista_camaras, vista_gestion_presos, vista_historico, \
    vista_configuracion, vista_consumo, vista_gestion_usuarios


def ejecutar_lectura_esp32():
    print(">>> INICIANDO CONEXIÓN WIFI CON ESP32 <<<")
    # Usa la IP que configuramos en manejador_datos
    url_sensores = f"http://{modelo.ESP32_IP}/sensores"

    while True:
        try:
            # Preguntamos al ESP32 por los datos
            respuesta = requests.get(url_sensores, timeout=3)

            if respuesta.status_code == 200:
                data = respuesta.json()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Traducimos el JSON del ESP32 al formato de nuestra Base de Datos
                datos = [
                    {"timestamp": timestamp, "sensor": "DHT11 - Temperatura", "valor": f"{data['temperatura']} °C"},
                    {"timestamp": timestamp, "sensor": "DHT11 - Humedad", "valor": f"{data['humedad']} %"},
                    {"timestamp": timestamp, "sensor": "LDR - Luz", "valor": f"{data['luz']} Lux"},
                    {"timestamp": timestamp, "sensor": "MQ-2 - Humo", "valor": f"{data['mq2']} ppm"}
                ]
                # Los guardamos en SQL (esto activa el modo automático si aplica)
                modelo.registrar_dato_sensor(datos)

        except Exception as e:
            print(f"Error leyendo hardware ESP32: {e}")

        time.sleep(5)  # Lee los sensores cada 5 segundos


# Cambia el hilo para que arranque la nueva función
hilo_hardware = threading.Thread(target=ejecutar_lectura_esp32, daemon=True)
hilo_hardware.start()

# --- HILO CONTROLADOR DE UI (MVC STRICT) ---
def loop_controlador_ui(page):
    while True:
        try:
            if not page.views or (page.route != "/dashboard" and page.route != "/consumo"):
                time.sleep(1)
                continue

            vista_actual = page.views[-1]

            if hasattr(vista_actual, 'data') and isinstance(vista_actual.data, dict):
                callback = vista_actual.data.get("update_callback")

                if callback:
                    if page.route == "/dashboard":
                        datos_sensores = modelo.get_ultimos_sensores_raw()
                        datos_actuadores = modelo.get_estado_actuadores()
                        callback(datos_sensores, datos_actuadores)

                    elif page.route == "/consumo":
                        datos_consumo = modelo.get_consumo_electrico()
                        callback(datos_consumo)

            time.sleep(0.5)

        except Exception as e:
            print(f"Error Loop Controlador: {e}")
            time.sleep(1)


# --- HANDLERS (CONTROLADOR) ---
def on_login_click(e, campo_usuario, campo_password, texto_error):
    page = e.page
    # Ahora validar_usuario devuelve el ROL y el ID NUMÉRICO (PK)
    rol, user_id = modelo.validar_usuario(campo_usuario.value, campo_password.value)

    if rol:
        page.session.set("user_rol", rol)
        page.session.set("user_name", campo_usuario.value)
        page.session.set("user_id", user_id)  # <--- GUARDAMOS EL ID PARA SQL
        texto_error.value = ""
        page.go("/dashboard")
    else:
        texto_error.value = "Datos incorrectos."
        page.update()


def on_logout_click(e):
    e.page.session.clear()
    e.page.go("/login")


def on_refrescar_click(e):
    if hasattr(e, 'page') and e.page:
        ruta = e.page.route
        e.page.go("/temp")
        e.page.go(ruta)


def on_control_actuador_click(e, actuador_id, valor_objetivo=None):
    page = e.page
    # Recuperamos el ID numérico en vez del nombre
    user_id = page.session.get("user_id")

    if page.session.get("user_rol") == "policia":
        page.snack_bar = ft.SnackBar(ft.Text("Permiso denegado."), bgcolor="red")
        page.snack_bar.open = True
        page.update()
        return

    # Enviamos el user_id para que encaje con la Foreign Key
    if "door" in actuador_id:
        modelo.toggle_actuador(actuador_id, user_id)
    else:
        modelo.set_estado_actuador(actuador_id, valor_objetivo, user_id)


def on_cambiar_modo_click(e, actuador_id):
    estados = modelo.get_estado_actuadores()
    modo_actual = estados.get(actuador_id, {}).get("mode", "manual")
    nuevo_modo = "manual" if modo_actual == "auto" else "auto"
    modelo.set_modo_actuador(actuador_id, nuevo_modo)
    e.page.snack_bar = ft.SnackBar(ft.Text(f"{actuador_id.upper()} cambiado a modo {nuevo_modo.upper()}"),
                                   bgcolor="blue")
    e.page.snack_bar.open = True
    e.page.update()


def on_ver_camaras_click(e): e.page.go("/camaras")


def on_volver_dashboard_click(e): e.page.go("/dashboard")


def on_ver_grabacion_video_click(e): e.page.go("/video")


def on_ver_historico_click(e): e.page.go("/historico")


def on_configuracion_click(e): e.page.go("/config")


def on_ver_consumo_click(e): e.page.go("/consumo")


def on_guardar_config_click(e, nuevos_datos):
    modelo.save_configuracion(nuevos_datos)
    e.page.snack_bar = ft.SnackBar(ft.Text("Configuración guardada correctamente"), bgcolor="green")
    e.page.snack_bar.open = True
    e.page.go("/dashboard")


def guardar_nuevo_preso(e, datos, dialogo):
    if modelo.add_preso(datos.get("nombre"), datos.get("delito"), datos.get("celda")):
        e.page.close(dialogo)
        on_refrescar_click(e)


def guardar_edicion_preso(e, datos, dialogo):
    if modelo.update_preso(datos.get("id"), datos):
        e.page.close(dialogo)
        on_refrescar_click(e)


def on_abrir_crear_preso(e): e.page.open(
    vista_gestion_presos.crear_dialogo_preso("Nuevo Registro", guardar_nuevo_preso))


def on_abrir_editar_preso(e, preso): e.page.open(
    vista_gestion_presos.crear_dialogo_preso("Editar Registro", guardar_edicion_preso, preso))


def on_borrar_preso_click(e, id_preso):
    if modelo.delete_preso(id_preso): on_refrescar_click(e)


def on_crear_usuario_click(e, u, p, r):
    if modelo.add_usuario(u.value, p.value, r.value): on_refrescar_click(e)


# --- SISTEMA DE MENÚ LATERAL (Navigation Rail) ---
def get_nav_rail(page, current_route):
    rol = page.session.get("user_rol")

    rutas_basicas = ["/dashboard", "/presos"]
    if rol == "comisario":
        rutas_basicas.append("/usuarios")

    rutas_basicas.extend(["/consumo", "/historico", "/config"])

    destinations = [
        ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Panel"),
        ft.NavigationRailDestination(icon=ft.Icons.LOCK_OUTLINE, selected_icon=ft.Icons.LOCK, label="Presos"),
    ]
    if rol == "comisario":
        destinations.append(
            ft.NavigationRailDestination(icon=ft.Icons.PEOPLE_OUTLINE, selected_icon=ft.Icons.PEOPLE, label="Personal"))

    destinations.extend([
        ft.NavigationRailDestination(icon=ft.Icons.BOLT_OUTLINED, selected_icon=ft.Icons.BOLT, label="Consumo"),
        ft.NavigationRailDestination(icon=ft.Icons.HISTORY_OUTLINED, selected_icon=ft.Icons.HISTORY, label="Histórico"),
        ft.NavigationRailDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="Ajustes"),
    ])

    try:
        selected_index = rutas_basicas.index(current_route)
    except ValueError:
        selected_index = None

    return ft.NavigationRail(
        selected_index=selected_index,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=80,
        destinations=destinations,
        on_change=lambda e: page.go(rutas_basicas[e.control.selected_index]),
        bgcolor="#1f2937",
        indicator_color="#38bdf8",
        selected_label_text_style=ft.TextStyle(color="#38bdf8", weight="bold"),
        unselected_label_text_style=ft.TextStyle(color="#9ca3af"),
        leading=ft.Container(content=ft.Image(src="logo.png", height=50), padding=ft.padding.only(top=15, bottom=20)),
        trailing=ft.Container(content=ft.IconButton(ft.Icons.LOGOUT, icon_color="#ef4444", tooltip="Cerrar Sesión",
                                                    on_click=on_logout_click), expand=True,
                              alignment=ft.alignment.bottom_center, padding=20)
    )


# --- ROUTER PRINCIPAL ---
def main(page: ft.Page):
    page.title = "Comisaría IoT"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    threading.Thread(target=loop_controlador_ui, args=(page,), daemon=True).start()

    def route_change(evt):
        page.views.clear()
        route = evt.route
        if route == "/temp": return
        page.views.clear()

        rol = page.session.get("user_rol")
        user_name = page.session.get("user_name")

        if not rol and route != "/login":
            page.go("/login")
            return

        if route == "/usuarios" and rol != "comisario":
            page.go("/dashboard")
            return

        if route == "/login":
            page.views.append(vista_login.crear_vista_login(on_login_click))

        elif route == "/dashboard":
            logs_recientes = modelo.get_log_sensores_filtrado(horas=24)
            dashboard_content = vista_dashboard_sensores.crear_dashboard_view(
                page,
                rol,
                user_name,
                modelo.get_estado_actuadores(),
                logs_recientes,
                on_refrescar_click,
                on_control_actuador_click,
                on_ver_camaras_click,
                on_cambiar_modo_click
            )
            rail = get_nav_rail(page, "/dashboard")
            v = ft.View("/dashboard", bgcolor="#0f1724", padding=0,
                        controls=[ft.Row([rail, ft.VerticalDivider(width=1, color="#374151"),
                                          ft.Container(content=dashboard_content, expand=True, padding=20)],
                                         expand=True, spacing=0)])
            v.data = dashboard_content.data
            page.views.append(v)

        elif route == "/presos":
            content = vista_gestion_presos.crear_vista_presos(
                modelo.get_presos(), on_abrir_crear_preso, on_abrir_editar_preso,
                on_refrescar_click, on_borrar_preso_click
            )
            rail = get_nav_rail(page, "/presos")
            page.views.append(ft.View("/presos", bgcolor="#0f1724", padding=0,
                                      controls=[ft.Row([rail, ft.VerticalDivider(width=1, color="#374151"),
                                                        ft.Container(content=content, expand=True, padding=30)],
                                                       expand=True, spacing=0)]))

        elif route == "/usuarios":
            content = vista_gestion_usuarios.crear_vista_usuarios(
                rol, modelo.get_usuarios(), on_crear_usuario_click
            )
            rail = get_nav_rail(page, "/usuarios")
            page.views.append(ft.View("/usuarios", bgcolor="#0f1724", padding=0,
                                      controls=[ft.Row([rail, ft.VerticalDivider(width=1, color="#374151"),
                                                        ft.Container(content=content, expand=True, padding=30)],
                                                       expand=True, spacing=0)]))

        elif route == "/config":
            content = vista_configuracion.crear_vista_configuracion(
                modelo.get_configuracion(),
                on_guardar_config_click,
                on_volver_dashboard_click
            )
            rail = get_nav_rail(page, "/config")
            page.views.append(ft.View("/config", bgcolor="#0f1724", padding=0,
                                      controls=[ft.Row([rail, ft.VerticalDivider(width=1, color="#374151"),
                                                        ft.Container(content=content, expand=True, padding=30)],
                                                       expand=True, spacing=0)]))

        elif route == "/consumo":
            content = vista_consumo.crear_vista_consumo(on_volver_dashboard_click)
            rail = get_nav_rail(page, "/consumo")
            v = ft.View("/consumo", bgcolor="#0f1724", padding=0,
                        controls=[ft.Row([rail, ft.VerticalDivider(width=1, color="#374151"),
                                          ft.Container(content=content, expand=True, padding=30)], expand=True,
                                         spacing=0)])
            v.data = {"update_callback": content.data.get("update_callback")} if hasattr(content,
                                                                                         'data') and isinstance(
                content.data, dict) else None
            page.views.append(v)

        elif route == "/camaras":
            page.views.append(vista_camaras.crear_vista_camaras(on_refrescar_click, on_volver_dashboard_click,
                                                                on_ver_grabacion_video_click))

        elif route == "/historico":
            content = vista_historico.crear_vista_historico(
                datos_promedio_sensores=modelo.get_promedio_sensores_por_hora(),
                datos_log_actuadores=[],
                on_volver_dashboard=on_volver_dashboard_click
            )
            rail = get_nav_rail(page, "/historico")
            page.views.append(ft.View("/historico", bgcolor="#0f1724", padding=0,
                                      controls=[ft.Row([rail, ft.VerticalDivider(width=1, color="#374151"),
                                                        ft.Container(content=content, expand=True, padding=10)],
                                                       expand=True, spacing=0)]))


        elif route == "/video":
            video_player = fv.Video(expand=True, playlist=[fv.VideoMedia("assets/videoGato.mp4")],
                                    playlist_mode=fv.PlaylistMode.LOOP, fill_color="#0f1724", aspect_ratio=16 / 9,
                                    volume=100, autoplay=True)
            page.views.append(ft.View(route="/video", bgcolor="#0f1724", padding=0,
                                      appbar=ft.AppBar(title=ft.Text("Grabación"), bgcolor="#0f1724",
                                                       leading=ft.IconButton(ft.Icons.ARROW_BACK,
                                                                             on_click=lambda e: page.go("/camaras"))),
                                      controls=[
                                          ft.Container(content=video_player, expand=True, alignment=ft.alignment.center,
                                                       padding=20)]))

        page.update()

    page.on_route_change = route_change
    page.go(page.route)


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")