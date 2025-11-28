import flet as ft
import flet_video as fv
from pathlib import Path
import modelo.manejador_datos as modelo
from vista import vista_login, vista_dashboard_sensores, vista_camaras, vista_gestion_presos, \
    vista_historico  # Import nuevo


# --- FUNCIONES DEL CONTROLADOR ---

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


def on_control_actuador_click(e, actuador_id, nuevo_estado):
    page = e.page
    if page.session.get("user_rol") == "policia":
        page.snack_bar = ft.SnackBar(ft.Text("Permiso denegado."), bgcolor="red")
        page.snack_bar.open = True
        page.update()
        return
    modelo.set_estado_actuador(actuador_id, nuevo_estado)
    on_refrescar_click(e)


# --- NAVEGACIÓN ---
def on_ver_camaras_click(e): e.page.go("/camaras")


def on_volver_dashboard_click(e): e.page.go("/dashboard")


def on_ver_grabacion_video_click(e): e.page.go("/video")


def on_ver_historico_click(e): e.page.go("/historico")  # Nueva funcion nav


# --- GESTIÓN DATOS ---
def guardar_nuevo_preso(e, datos, dialogo):
    if modelo.add_preso(datos.get("nombre"), datos.get("delito"), datos.get("celda")):
        e.page.close(dialogo)
        on_refrescar_click(e)


def guardar_edicion_preso(e, datos, dialogo):
    if modelo.update_preso(datos.get("id"), datos):
        e.page.close(dialogo)
        on_refrescar_click(e)


def on_abrir_crear_preso(e):
    e.page.open(vista_gestion_presos.crear_dialogo_preso("Nuevo", guardar_nuevo_preso))


def on_abrir_editar_preso(e, preso):
    e.page.open(vista_gestion_presos.crear_dialogo_preso("Editar", guardar_edicion_preso, preso))


def on_borrar_preso_click(e, id_preso):
    if modelo.delete_preso(id_preso): on_refrescar_click(e)


def on_crear_usuario_click(e, u, p, r):
    if modelo.add_usuario(u.value, p.value, r.value): on_refrescar_click(e)


# --- ROUTER PRINCIPAL ---

def main(page: ft.Page):
    page.title = "Comisaría IoT"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    def route_change(evt):
        route = evt.route
        if route == "/temp": return
        page.views.clear()

        rol = page.session.get("user_rol")
        if not rol and route != "/login":
            page.go("/login")
            return

        if route == "/login":
            page.views.append(vista_login.crear_vista_login(on_login_click))

        elif route == "/dashboard":
            page.views.append(vista_dashboard_sensores.crear_dashboard_view(
                page, rol,
                modelo.get_estado_actuadores(), modelo.get_presos(), modelo.get_usuarios(), modelo.get_log_sensores(),
                on_logout_click, on_refrescar_click, on_control_actuador_click, on_crear_usuario_click,
                on_borrar_preso_click, on_ver_camaras_click,
                on_abrir_crear_preso, on_abrir_editar_preso,
                on_ver_historico_click  # Pasamos el handler
            ))

        elif route == "/camaras":
            page.views.append(vista_camaras.crear_vista_camaras(
                on_refrescar_click, on_volver_dashboard_click, on_ver_grabacion_video_click
            ))

        elif route == "/historico":
            page.views.append(vista_historico.crear_vista_historico(
                modelo.get_log_sensores(limite=200),  # Pasamos más datos para historial
                modelo.get_estado_actuadores(),
                on_volver_dashboard_click
            ))

        elif route == "/video":
            video_player = fv.Video(
                expand=True,
                playlist=[fv.VideoMedia("assets/videoGato.mp4")],
                playlist_mode=fv.PlaylistMode.LOOP,
                fill_color="#0f1724",
                aspect_ratio=16 / 9,
                volume=100,
                autoplay=True
            )

            page.views.append(
                ft.View(
                    route="/video",
                    bgcolor="#0f1724",
                    appbar=ft.AppBar(
                        title=ft.Text("Grabación - Sala de Vigilancia"),
                        bgcolor="#0f1724",
                        leading=ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda e: page.go("/camaras")
                        )
                    ),
                    controls=[
                        ft.Container(
                            content=video_player,
                            expand=True,
                            alignment=ft.alignment.center,
                            padding=20
                        )
                    ],
                    padding=0
                )
            )

        page.update()

    page.on_route_change = route_change
    page.go(page.route)


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")