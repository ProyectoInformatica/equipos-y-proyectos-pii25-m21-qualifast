import flet as ft
import flet_webview
from pathlib import Path
import modelo.manejador_datos as modelo
from vista import vista_login, vista_dashboard_sensores, vista_camaras, vista_gestion_presos

# --- FUNCIONES DEL CONTROLADOR (Lógica de botones) ---

def on_login_click(e, campo_usuario, campo_password, texto_error):
    """Se ejecuta al pulsar 'Entrar' en la vista de login."""
    page = e.page
    rol = modelo.validar_usuario(campo_usuario.value, campo_password.value)
    if rol:
        page.session.set("user_rol", rol)
        page.session.set("user_name", campo_usuario.value)
        texto_error.value = ""
        campo_usuario.value = ""
        campo_password.value = ""
        page.go("/dashboard") # Navega al dashboard
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
    """Maneja el clic en puertas, luces, ventilador, etc."""
    page = e.page
    if page.session.get("user_rol") == "policia":
        page.snack_bar = ft.SnackBar(ft.Text("Permiso denegado."), bgcolor="red")
        page.snack_bar.open = True
        page.update()
        return

    print(f"Controlador: Cambiando {actuador_id} a {nuevo_estado}")
    modelo.set_estado_actuador(actuador_id, nuevo_estado)
    on_refrescar_click(e)


# --- NAVEGACIÓN ---
def on_ver_camaras_click(e): e.page.go("/camaras")


def on_volver_dashboard_click(e): e.page.go("/dashboard")


def on_ver_grabacion_video_click(e): e.page.go("/video")


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
            return # Detiene la ejecución

        elif route == "/dashboard":
            page.views.append(vista_dashboard_sensores.crear_dashboard_view(
                page, rol,
                modelo.get_estado_actuadores(), modelo.get_presos(), modelo.get_usuarios(), modelo.get_log_sensores(),
                on_logout_click, on_refrescar_click, on_control_actuador_click, on_crear_usuario_click,
                on_borrar_preso_click, on_ver_camaras_click, on_abrir_crear_preso, on_abrir_editar_preso
            ))

        elif route == "/camaras":
            page.views.append(vista_camaras.crear_vista_camaras(
                on_refrescar_click, on_volver_dashboard_click, on_ver_grabacion_video_click
            ))

        elif route == "/video":
            # --- VIDEO CON WEBVIEW (El rápido) ---
            video_path = Path("assets/videoGato.mp4").resolve()
            video_url = video_path.as_uri()

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
                        flet_webview.WebView(
                            url=video_url,
                            expand=True,
                        )
                    ],
                    padding=0
                )
            )

        page.update()

    page.on_route_change = route_change
    page.go(page.route) # Carga la ruta inicial (o /login si no hay sesión)

# --- Iniciar la aplicación ---
if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
