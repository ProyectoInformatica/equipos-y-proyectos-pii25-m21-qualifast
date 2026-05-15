import flet as ft
import flet_video as fv
import threading
import random
import time
import os
import cv2
import numpy as np
import requests
import logging
from datetime import datetime
import modelo.manejador_datos as modelo
from vista import vista_login, vista_dashboard_sensores, vista_camaras, vista_gestion_presos, vista_historico, \
    vista_configuracion, vista_consumo, vista_gestion_usuarios, vista_chat

logging.getLogger('asyncio').setLevel(logging.CRITICAL)
logging.getLogger('flet_core').setLevel(logging.CRITICAL)


def leer_archivo_binario(ruta):
    if ruta and os.path.exists(ruta):
        try:
            with open(ruta, "rb") as f:
                file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
                img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            if img is not None:
                h, w = img.shape[:2]
                min_dim = min(h, w)
                start_x = (w // 2) - (min_dim // 2)
                start_y = (h // 2) - (min_dim // 2)
                cropped_img = img[start_y:start_y + min_dim, start_x:start_x + min_dim]
                img_resized = cv2.resize(cropped_img, (200, 200))
                ret, buffer = cv2.imencode('.jpg', img_resized, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if ret:
                    return buffer.tobytes()
        except Exception as e:
            print(f"[ERROR SISTEMA] Procesando imagen OpenCV: {e}")
        try:
            with open(ruta, "rb") as f:
                return f.read(1024 * 1024)
        except:
            pass
    return None


def loop_controlador_ui(page):
    while True:
        try:
            if not page.views:
                time.sleep(1)
                continue

            vista_actual = page.views[-1]

            if page.route == "/login":
                if hasattr(vista_actual, 'data') and isinstance(vista_actual.data, dict):
                    cb_status = vista_actual.data.get("update_status_callback")
                    if cb_status:
                        conectado = modelo.probar_conexion()
                        cb_status(conectado)
                time.sleep(3)
                continue

            if page.route == "/dashboard" or page.route == "/consumo":
                if hasattr(vista_actual, 'data') and isinstance(vista_actual.data, dict):
                    callback = vista_actual.data.get("update_callback")
                    if callback:
                        if page.route == "/dashboard":
                            # Ahora pasamos también si el ESP32 está ONLINE u OFFLINE
                            callback(
                                modelo.get_ultimos_sensores_raw(),
                                modelo.get_estado_actuadores(),
                                modelo.obtener_estado_esp32()
                            )
                        elif page.route == "/consumo":
                            callback(modelo.get_consumo_electrico())
            time.sleep(1)
        except Exception as e:
            print(f"[ERROR UI] Fallo en loop de fondo: {e}")
            time.sleep(1)


def on_login_click(e, campo_usuario, campo_password, texto_error):
    page = e.page
    rol, user_id, foto_b64 = modelo.validar_usuario(campo_usuario.value, campo_password.value)
    if rol:
        page.session.set("user_rol", rol)
        page.session.set("user_name", campo_usuario.value)
        page.session.set("user_id", user_id)
        page.session.set("user_foto", foto_b64)
        texto_error.value = ""
        page.go("/dashboard")
    else:
        if not modelo.probar_conexion():
            texto_error.value = "Error: Sin conexión a la Base de Datos."
        else:
            texto_error.value = "Credenciales incorrectas."
        page.update()


def on_logout_click(e):
    e.page.session.clear()
    e.page.go("/login")


def on_control_actuador_click(e, actuador_id, valor_objetivo=None):
    if e.page.session.get("user_rol") == "policia":
        e.page.snack_bar = ft.SnackBar(ft.Text("Permiso denegado."), bgcolor="red")
        e.page.snack_bar.open = True
        e.page.update()
        return
    user_id = e.page.session.get("user_id")
    if "door" in actuador_id:
        modelo.toggle_actuador(actuador_id, user_id)
    else:
        modelo.set_estado_actuador(actuador_id, valor_objetivo, user_id)


def on_refrescar_click(e):
    if hasattr(e, 'page') and e.page:
        ruta = e.page.route
        e.page.go("/temp")
        e.page.go(ruta)


def guardar_nuevo_preso(e, datos, dialogo, foto_ruta=None):
    foto_bytes = leer_archivo_binario(foto_ruta)
    if modelo.add_preso(datos.get("nombre"), datos.get("delito"), datos.get("celda"), foto_bytes):
        e.page.close(dialogo)
        on_refrescar_click(e)


def guardar_edicion_preso(e, datos, dialogo, foto_ruta=None):
    foto_bytes = leer_archivo_binario(foto_ruta)
    if modelo.update_preso(datos.get("id"), datos, foto_bytes):
        e.page.close(dialogo)
        on_refrescar_click(e)


def on_crear_usuario_click(e, u, p, r, foto_ruta=None):
    foto_bytes = leer_archivo_binario(foto_ruta)
    if modelo.add_usuario(u.value, p.value, r.value, foto_bytes):
        on_refrescar_click(e)


def on_editar_usuario_click(e, uid, txt_user, txt_pass, dd_rol, dialogo, foto_ruta=None):
    foto_bytes = leer_archivo_binario(foto_ruta)
    if modelo.update_usuario(uid, txt_user.value, txt_pass.value, dd_rol.value, foto_bytes):
        e.page.close(dialogo)
        if e.page.session.get("user_id") == uid and foto_bytes:
            import base64
            e.page.session.set("user_foto", base64.b64encode(foto_bytes).decode('utf-8'))
        on_refrescar_click(e)
    else:
        e.page.snack_bar = ft.SnackBar(ft.Text("Error al actualizar."), bgcolor="red")
        e.page.snack_bar.open = True
        e.page.update()


def get_nav_rail(page, current_route):
    rol = page.session.get("user_rol")
    nombre = page.session.get("user_name")
    foto = page.session.get("user_foto")

    rutas = ["/dashboard", "/presos", "/chat"]
    if rol == "comisario": rutas.append("/usuarios")
    rutas.extend(["/consumo", "/historico", "/config"])

    destinations = [
        ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Panel"),
        ft.NavigationRailDestination(icon=ft.Icons.LOCK_OUTLINE, selected_icon=ft.Icons.LOCK, label="Presos"),
        ft.NavigationRailDestination(icon=ft.Icons.CHAT_OUTLINED, selected_icon=ft.Icons.CHAT, label="Chat"),
    ]
    if rol == "comisario":
        destinations.append(
            ft.NavigationRailDestination(icon=ft.Icons.PEOPLE_OUTLINE, selected_icon=ft.Icons.PEOPLE, label="Personal"))
    destinations.extend([
        ft.NavigationRailDestination(icon=ft.Icons.BOLT_OUTLINED, selected_icon=ft.Icons.BOLT, label="Consumo"),
        ft.NavigationRailDestination(icon=ft.Icons.HISTORY_OUTLINED, selected_icon=ft.Icons.HISTORY, label="Histórico"),
        ft.NavigationRailDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="Ajustes"),
    ])

    avatar = ft.Container(
        width=40, height=40, border_radius=20, bgcolor="#374151", alignment=ft.alignment.center,
        content=ft.Image(src_base64=foto, fit=ft.ImageFit.COVER, border_radius=20, width=40,
                         height=40) if foto else ft.Icon(ft.Icons.PERSON, color="white")
    )

    return ft.NavigationRail(
        selected_index=rutas.index(current_route) if current_route in rutas else 0,
        label_type=ft.NavigationRailLabelType.ALL,
        destinations=destinations,
        on_change=lambda e: page.go(rutas[e.control.selected_index]),
        bgcolor="#1f2937",
        indicator_color="#38bdf8",
        leading=ft.Column([
            ft.Container(padding=10, content=avatar),
            ft.Text(nombre, size=10, weight="bold", color="white", text_align="center"),
            ft.Text(rol, size=8, color="#38bdf8", text_align="center"),
            ft.Divider(color="#374151")
        ], horizontal_alignment="center", spacing=2),
        trailing=ft.IconButton(ft.Icons.LOGOUT, icon_color="#ef4444", on_click=on_logout_click)
    )


def main(page: ft.Page):
    page.title = "Comisaría IoT"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    threading.Thread(target=loop_controlador_ui, args=(page,), daemon=True).start()

    def route_change(evt):
        try:
            page.views.clear()
            route = page.route
            if route == "/temp": return

            rol = page.session.get("user_rol")
            if not rol and route != "/login":
                page.go("/login")
                return

            if route == "/login":
                page.views.append(vista_login.crear_vista_login(
                    on_login_click,
                    modelo.LOCAL_CONFIG,
                    modelo.save_local_config
                ))

            elif route == "/dashboard":
                content = vista_dashboard_sensores.crear_dashboard_view(
                    page, rol, page.session.get("user_name"),
                    modelo.get_estado_actuadores(), modelo.get_ultimos_sensores_raw(),
                    on_refrescar_click, on_control_actuador_click, lambda e: page.go("/camaras"),
                    # Usamos la nueva función "toggle" para alternar Auto/Manual de forma sana
                    lambda e, a: modelo.toggle_modo_actuador(a)
                )
                v = ft.View("/dashboard", controls=[ft.Row([get_nav_rail(page, route), ft.VerticalDivider(width=1),
                                                            ft.Container(content=content, expand=True)], expand=True)])
                v.data = content.data
                page.views.append(v)

            elif route == "/presos":
                content = vista_gestion_presos.crear_vista_presos(
                    modelo.get_presos(),
                    lambda _: page.open(
                        vista_gestion_presos.crear_dialogo_preso("Nuevo", guardar_nuevo_preso, None, file_picker)),
                    lambda e, p: page.open(
                        vista_gestion_presos.crear_dialogo_preso("Editar", guardar_edicion_preso, p, file_picker)),
                    on_refrescar_click, lambda e, pid: modelo.delete_preso(pid) and on_refrescar_click(e)
                )
                page.views.append(ft.View("/presos", controls=[ft.Row(
                    [get_nav_rail(page, route), ft.VerticalDivider(width=1),
                     ft.Container(content=content, expand=True)], expand=True)]))

            elif route == "/chat":
                content = vista_chat.crear_vista_chat(page)
                page.views.append(ft.View("/chat", controls=[ft.Row(
                    [get_nav_rail(page, route), ft.VerticalDivider(width=1),
                     ft.Container(content=content, expand=True)], expand=True)]))

            elif route == "/usuarios":
                content = vista_gestion_usuarios.crear_vista_usuarios(
                    rol, modelo.get_usuarios(), on_crear_usuario_click, on_editar_usuario_click, file_picker
                )
                page.views.append(ft.View("/usuarios", controls=[ft.Row(
                    [get_nav_rail(page, route), ft.VerticalDivider(width=1),
                     ft.Container(content=content, expand=True)], expand=True)]))

            elif route == "/config":
                content = vista_configuracion.crear_vista_configuracion(
                    config_actual=modelo.get_configuracion(),
                    local_config=modelo.LOCAL_CONFIG,
                    on_guardar_click=lambda e, d: modelo.save_configuracion(d) and page.go("/dashboard"),
                    on_guardar_hardware_click=lambda d: modelo.save_local_config(d) and page.go("/dashboard")
                )
                page.views.append(ft.View("/config", controls=[ft.Row(
                    [get_nav_rail(page, route), ft.VerticalDivider(width=1),
                     ft.Container(content=content, expand=True)], expand=True)]))

            elif route == "/consumo":
                content = vista_consumo.crear_vista_consumo(lambda e: page.go("/dashboard"))
                v = ft.View("/consumo", controls=[ft.Row([get_nav_rail(page, route), ft.VerticalDivider(width=1),
                                                          ft.Container(content=content, expand=True)], expand=True)])
                v.data = {"update_callback": content.data.get("update_callback")} if hasattr(content,
                                                                                             'data') and isinstance(
                    content.data, dict) else None
                page.views.append(v)

            elif route == "/camaras":
                page.views.append(vista_camaras.crear_vista_camaras(on_refrescar_click, lambda e: page.go("/dashboard"),
                                                                    lambda e: page.go("/video")))

            elif route == "/historico":
                content = vista_historico.crear_vista_historico(
                    datos_promedio_sensores=modelo.get_promedio_sensores_por_hora(),
                    datos_log_actuadores=[],
                    on_volver_dashboard=lambda e: page.go("/dashboard")
                )
                page.views.append(ft.View("/historico", controls=[ft.Row(
                    [get_nav_rail(page, route), ft.VerticalDivider(width=1),
                     ft.Container(content=content, expand=True, padding=10)], expand=True)]))

            elif route == "/video":
                video_player = fv.Video(expand=True, playlist=[fv.VideoMedia("assets/videoGato.mp4")],
                                        playlist_mode=fv.PlaylistMode.LOOP, fill_color="#0f1724", aspect_ratio=16 / 9,
                                        volume=100, autoplay=True)
                page.views.append(ft.View("/video", appbar=ft.AppBar(title=ft.Text("Grabación"), bgcolor="#0f1724",
                                                                     leading=ft.IconButton(ft.Icons.ARROW_BACK,
                                                                                           on_click=lambda e: page.go(
                                                                                               "/camaras"))), controls=[
                    ft.Container(content=video_player, expand=True, alignment=ft.alignment.center, padding=20)]))

            page.update()

        except Exception as ex:
            print(f"[ERROR CRÍTICO] Excepción en router de vistas: {ex}")
            page.views.append(ft.View("/error", controls=[ft.Text(f"Error Crítico: {ex}", color="red", size=20)]))
            page.update()

    page.on_route_change = route_change
    page.go("/login")


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")