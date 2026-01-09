import flet as ft
import flet_video as fv
import threading
import time
import random
from datetime import datetime
import modelo.manejador_datos as modelo
from vista import vista_login, vista_dashboard_sensores, vista_camaras, vista_gestion_presos, vista_historico, \
    vista_configuracion, vista_consumo  # <--- Importar vista_consumo


# --- SIMULADOR IOT (Hilo de Background) ---
def ejecutar_simulador():
    sensores = ["DHT11 - Temperatura", "DHT11 - Humedad", "LDR - Luz", "MQ-2 - Humo", "MQ-135 - Aire"]
    print(">>> INICIANDO SIMULADOR IOT (2º Plano) <<<")
    while True:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            datos = []
            for s in sensores:
                val = ""
                if "Temperatura" in s:
                    val = f"{round(random.uniform(20, 35), 1)} °C"
                elif "Humedad" in s:
                    val = f"{random.randint(40, 60)} %"
                elif "Luz" in s:
                    val = f"{random.randint(100, 900)} Lux"
                elif "Humo" in s:
                    val = f"{random.randint(10, 30)} ppm"
                elif "Aire" in s:
                    val = f"{random.randint(400, 480)} ppm"
                datos.append({"timestamp": timestamp, "sensor": s, "valor": val})

            modelo.registrar_dato_sensor(datos)
            time.sleep(5)
        except Exception as e:
            print(f"Error simulador: {e}")
            time.sleep(5)


hilo_simulador = threading.Thread(target=ejecutar_simulador, daemon=True)
hilo_simulador.start()


# --- HILO CONTROLADOR DE UI (MVC STRICT) ---
def loop_controlador_ui(page):
    """
    Este hilo pertenece al CONTROLADOR.
    1. Obtiene datos del MODELO.
    2. Actualiza la VISTA activa si corresponde.
    """
    while True:
        try:
            # Solo trabajamos si hay vistas y estamos en dashboard o consumo
            if not page.views or (page.route != "/dashboard" and page.route != "/consumo"):
                time.sleep(1)
                continue

            # Obtenemos la vista actual
            vista_actual = page.views[-1]

            # Verificamos si la vista tiene el "puerto" de entrada de datos (callback)
            if hasattr(vista_actual, 'data') and isinstance(vista_actual.data, dict):
                callback = vista_actual.data.get("update_callback")

                if callback:
                    if page.route == "/dashboard":
                        # 1. PEDIR DATOS AL MODELO (RAM Cache = Rápido)
                        datos_sensores = modelo.get_ultimos_sensores_raw()
                        datos_actuadores = modelo.get_estado_actuadores()
                        # 2. INYECTAR DATOS A LA VISTA
                        callback(datos_sensores, datos_actuadores)

                    elif page.route == "/consumo":
                        # Obtener datos de consumo
                        datos_consumo = modelo.get_consumo_electrico()
                        callback(datos_consumo)

            time.sleep(0.5)  # Refresco controlado por el Controlador

        except Exception as e:
            print(f"Error Loop Controlador: {e}")
            time.sleep(1)


# --- HANDLERS (CONTROLADOR) ---
def on_login_click(e, campo_usuario, campo_password, texto_error):
    page = e.page
    rol = modelo.validar_usuario(campo_usuario.value, campo_password.value)
    if rol:
        page.session.set("user_rol", rol)
        page.session.set("user_name", campo_usuario.value)
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
    usuario = page.session.get("user_name") or "desconocido"
    if page.session.get("user_rol") == "policia":
        page.snack_bar = ft.SnackBar(ft.Text("Permiso denegado."), bgcolor="red")
        page.snack_bar.open = True
        page.update()
        return

    if "door" in actuador_id:
        modelo.toggle_actuador(actuador_id, usuario)
    else:
        modelo.set_estado_actuador(actuador_id, valor_objetivo, usuario)


def on_cambiar_modo_click(e, actuador_id):
    """Alterna entre Auto y Manual"""
    estados = modelo.get_estado_actuadores()
    modo_actual = estados.get(actuador_id, {}).get("mode", "manual")
    nuevo_modo = "manual" if modo_actual == "auto" else "auto"
    modelo.set_modo_actuador(actuador_id, nuevo_modo)

    e.page.snack_bar = ft.SnackBar(ft.Text(f"{actuador_id.upper()} cambiado a modo {nuevo_modo.upper()}"),
                                   bgcolor="blue")
    e.page.snack_bar.open = True
    e.page.update()


# Navegación
def on_ver_camaras_click(e): e.page.go("/camaras")


def on_volver_dashboard_click(e): e.page.go("/dashboard")


def on_ver_grabacion_video_click(e): e.page.go("/video")


def on_ver_historico_click(e): e.page.go("/historico")


def on_configuracion_click(e): e.page.go("/config")


def on_ver_consumo_click(e): e.page.go("/consumo")  # Handler navegacion consumo


def on_guardar_config_click(e, nuevos_datos):
    modelo.save_configuracion(nuevos_datos)
    e.page.snack_bar = ft.SnackBar(ft.Text("Configuración guardada correctamente"), bgcolor="green")
    e.page.snack_bar.open = True
    e.page.go("/dashboard")


# Gestión Datos CRUD
def guardar_nuevo_preso(e, datos, dialogo):
    if modelo.add_preso(datos.get("nombre"), datos.get("delito"), datos.get("celda")):
        e.page.close(dialogo);
        on_refrescar_click(e)


def guardar_edicion_preso(e, datos, dialogo):
    if modelo.update_preso(datos.get("id"), datos):
        e.page.close(dialogo);
        on_refrescar_click(e)


def on_abrir_crear_preso(e): e.page.open(vista_gestion_presos.crear_dialogo_preso("Nuevo", guardar_nuevo_preso))


def on_abrir_editar_preso(e, preso): e.page.open(
    vista_gestion_presos.crear_dialogo_preso("Editar", guardar_edicion_preso, preso))


def on_borrar_preso_click(e, id_preso):
    if modelo.delete_preso(id_preso): on_refrescar_click(e)


def on_crear_usuario_click(e, u, p, r):
    if modelo.add_usuario(u.value, p.value, r.value): on_refrescar_click(e)


# --- ROUTER PRINCIPAL ---
def main(page: ft.Page):
    page.title = "Comisaría IoT"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    # Iniciamos el hilo Controlador de UI
    threading.Thread(target=loop_controlador_ui, args=(page,), daemon=True).start()

    def route_change(evt):
        route = evt.route
        if route == "/temp": return
        page.views.clear()

        rol = page.session.get("user_rol")
        user_name = page.session.get("user_name")

        if not rol and route != "/login":
            page.go("/login")
            return

        if route == "/login":
            page.views.append(vista_login.crear_vista_login(on_login_click))

        elif route == "/dashboard":
            # Pasamos datos iniciales, pero el hilo se encargará de refrescar
            logs_recientes = modelo.get_log_sensores_filtrado(horas=24)
            page.views.append(vista_dashboard_sensores.crear_dashboard_view(
                page, rol, user_name,
                modelo.get_estado_actuadores(),
                modelo.get_presos(),
                modelo.get_usuarios(),
                logs_recientes,
                on_logout_click, on_refrescar_click, on_control_actuador_click, on_crear_usuario_click,
                on_borrar_preso_click, on_ver_camaras_click,
                on_abrir_crear_preso, on_abrir_editar_preso,
                on_ver_historico_click,
                on_configuracion_click,
                on_cambiar_modo_click,
                on_ver_consumo_click  # Pasamos el handler nuevo
            ))

        elif route == "/config":
            page.views.append(vista_configuracion.crear_vista_configuracion(
                modelo.get_configuracion(),
                on_guardar_config_click,
                on_volver_dashboard_click
            ))

        elif route == "/consumo":
            page.views.append(vista_consumo.crear_vista_consumo(
                on_volver_dashboard_click
            ))

        elif route == "/camaras":
            page.views.append(vista_camaras.crear_vista_camaras(on_refrescar_click, on_volver_dashboard_click,
                                                                on_ver_grabacion_video_click))

        elif route == "/historico":
            page.views.append(vista_historico.crear_vista_historico(
                datos_promedio_sensores=modelo.get_promedio_sensores_por_hora(),
                datos_log_actuadores=modelo.get_log_historico_completo(dias=7),
                on_volver_dashboard=on_volver_dashboard_click
            ))

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