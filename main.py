import flet as ft
import modelo.manejador_datos as modelo
from vista import vista_login, vista_dashboard_sensores


# --- FUNCIONES DEL CONTROLADOR ---

def on_login_click(e, campo_usuario, campo_password, texto_error):
    page = e.page
    usuario = campo_usuario.value
    password = campo_password.value
    rol = modelo.validar_usuario(usuario, password)

    if rol:
        page.session.set("user_rol", rol)
        page.session.set("user_name", usuario)
        texto_error.value = ""
        page.go("/dashboard")
    else:
        texto_error.value = "Usuario o contraseña incorrectos."
        page.update()


def on_logout_click(e):
    page = e.page
    page.session.clear()
    page.go("/login")


def on_refrescar_click(e):
    """Refresca la página forzando la recarga de la ruta actual."""
    print("Controlador: Refrescando página...")
    # Truco para forzar la recarga real: llamamos manualmente al evento de cambio de ruta
    if hasattr(e, 'page') and e.page:
        route = e.page.route
        e.page.on_route_change(ft.RouteChangeEvent(route))


def on_control_actuador_click(e, actuador_id, nuevo_estado):
    page = e.page
    rol = page.session.get("user_rol")
    if rol == "policia":
        page.snack_bar = ft.SnackBar(ft.Text("Permiso denegado.", color="white"), bgcolor=ft.Colors.RED_700)
        page.snack_bar.open = True
        page.update()
        return
    modelo.set_estado_actuador(actuador_id, nuevo_estado)
    on_refrescar_click(e)


def on_crear_preso_click(e, campo_nombre):
    page = e.page
    nombre = campo_nombre.value
    if not nombre:
        page.snack_bar = ft.SnackBar(ft.Text("El nombre es obligatorio.", color="white"), bgcolor=ft.Colors.RED_700)
        page.snack_bar.open = True
        page.update()
        return

    if modelo.add_preso(nombre, "Delito Pendiente"):
        campo_nombre.value = ""
        page.snack_bar = ft.SnackBar(ft.Text(f"Preso {nombre} añadido."), bgcolor=ft.Colors.GREEN_700)
        page.snack_bar.open = True
        on_refrescar_click(e)
    else:
        page.snack_bar = ft.SnackBar(ft.Text("Error al añadir preso."), bgcolor=ft.Colors.RED_700)
        page.snack_bar.open = True
        page.update()


def on_borrar_preso_click(e, id_preso):
    """Función para borrar presos."""
    page = e.page
    print(f"Controlador: Borrando preso {id_preso}")

    if modelo.delete_preso(id_preso):
        page.snack_bar = ft.SnackBar(ft.Text(f"Preso {id_preso} eliminado."), bgcolor=ft.Colors.GREEN_700)
        page.snack_bar.open = True
        on_refrescar_click(e)
    else:
        page.snack_bar = ft.SnackBar(ft.Text("Error al eliminar preso."), bgcolor=ft.Colors.RED_700)
        page.snack_bar.open = True
        page.update()


def on_crear_usuario_click(e, campo_user, campo_pass, dd_rol):
    page = e.page
    rol_actual = page.session.get("user_rol")
    if rol_actual != "comisario":
        return
    username = campo_user.value
    password = campo_pass.value
    rol_nuevo = dd_rol.value

    if modelo.add_usuario(username, password, rol_nuevo):
        page.snack_bar = ft.SnackBar(ft.Text(f"Usuario {username} creado."), bgcolor=ft.Colors.GREEN_700)
    else:
        page.snack_bar = ft.SnackBar(ft.Text("Error al crear usuario.", color="white"), bgcolor=ft.Colors.RED_700)

    page.snack_bar.open = True
    campo_user.value = ""
    campo_pass.value = ""
    on_refrescar_click(e)


# --- ROUTING PRINCIPAL ---

def main(page: ft.Page):
    page.title = "Sistema de Comisaría"
    page.window_width = 1600
    page.window_height = 900
    page.theme_mode = ft.ThemeMode.DARK

    def route_change(route_event):
        # Normalizar el evento de ruta
        route = route_event.route if isinstance(route_event, ft.RouteChangeEvent) else route_event

        print(f"Navegando a: {route}")
        page.views.clear()
        rol = page.session.get("user_rol")

        # Redirección si no hay sesión
        if not rol and route != "/login":
            page.go("/login")
            return

        if route == "/login":
            page.views.append(vista_login.crear_vista_login(on_login_click))

        elif route == "/dashboard":
            # 1. Obtener datos del MODELO
            datos_act = modelo.get_estado_actuadores()
            datos_presos = modelo.get_presos()
            datos_user = modelo.get_usuarios()

            # Obtener datos de sensores
            datos_sens = modelo.get_log_sensores()

            # 2. Crear la VISTA pasando datos y handlers
            page.views.append(
                vista_dashboard_sensores.crear_dashboard_view(
                    page=page,
                    rol_usuario=rol,
                    datos_actuadores=datos_act,
                    datos_presos=datos_presos,
                    datos_usuarios=datos_user,
                    # Pasar datos de sensores a la vista
                    datos_sensores=datos_sens,
                    on_logout_click=on_logout_click,
                    on_refrescar_click=on_refrescar_click,
                    on_control_actuador_click=on_control_actuador_click,
                    on_crear_preso_click=on_crear_preso_click,
                    on_crear_usuario_click=on_crear_usuario_click,

                )
            )
        else:
            page.go("/login")

        page.update()

    page.on_route_change = route_change
    page.go(page.route)


if __name__ == "__main__":
    ft.app(target=main)