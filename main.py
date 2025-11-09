import flet as ft
import modelo.manejador_datos as modelo # Importa el Modelo
from vista import vista_login, vista_dashboard_sensores # Importa las Vistas

# --- FUNCIONES DEL CONTROLADOR (Lógica de botones) ---

def on_login_click(e, campo_usuario, campo_password, texto_error):
    """Se ejecuta al pulsar 'Entrar' en la vista de login."""
    page = e.page
    
    usuario = campo_usuario.value
    password = campo_password.value
    
    rol = modelo.validar_usuario(usuario, password)
    
    if rol:
        # ¡ÉXITO!
        print(f"Controlador: Login exitoso. Rol: {rol}")
        page.session.set("user_rol", rol) # Guarda el rol en la sesión
        page.session.set("user_name", usuario)
        texto_error.value = ""
        campo_usuario.value = ""
        campo_password.value = ""
        page.go("/dashboard") # Navega al dashboard
    else:
        # ¡FALLO!
        print("Controlador: Login fallido.")
        texto_error.value = "Usuario o contraseña incorrectos."
        page.update()

def on_logout_click(e):
    """Limpia la sesión y vuelve al login."""
    page = e.page
    page.session.clear()
    page.go("/login")

def on_refrescar_click(e):
    """Fuerza una actualización de la vista actual."""
    print("Controlador: Refrescando la página.")
    page = e.page
    # Vuelve a cargar la ruta actual, lo que fuerza a 'route_change'
    # a volver a cargar todos los datos del modelo
    page.go(page.route) 

def on_control_actuador_click(e, actuador_id, nuevo_estado):
    """Maneja el clic en puertas, luces, ventilador, etc."""
    page = e.page
    rol = page.session.get("user_rol")
    
    if rol == "policia":
        print("Controlador: Permiso denegado (Policía).")
        # Opcional: mostrar un snackbar de error
        page.snack_bar = ft.SnackBar(ft.Text("Permiso denegado.", color="white"), bgcolor=ft.Colors.RED_700)
        page.snack_bar.open = True
        page.update()
        return

    print(f"Controlador: Cambiando {actuador_id} a {nuevo_estado}")
    modelo.set_estado_actuador(actuador_id, nuevo_estado)
    # Refrescamos para que se vea el cambio
    on_refrescar_click(e)

def on_crear_preso_click(e, campo_nombre):
    """Añade un nuevo preso."""
    page = e.page
    nombre = campo_nombre.value
    
    if not nombre:
        page.snack_bar = ft.SnackBar(ft.Text("El nombre no puede estar vacío.", color="white"), bgcolor=ft.Colors.RED_700)
        page.snack_bar.open = True
        page.update()
        return
    
    # El rol no importa, todos pueden
    print(f"Controlador: Añadiendo preso {nombre}")
    # (En un proyecto real, pedirías más datos como 'delito' en un diálogo)
    modelo.add_preso(nombre, "Delito pendiente")
    
    # Limpia el campo y refresca
    campo_nombre.value = ""
    on_refrescar_click(e)

def on_crear_usuario_click(e, campo_user, campo_pass, dd_rol):
    """Añade un nuevo usuario (solo Comisario)."""
    page = e.page
    rol_actual = page.session.get("user_rol")

    if rol_actual != "comisario":
        print("Controlador: ¡Intento de crear usuario sin permisos!")
        return
        
    username = campo_user.value
    password = campo_pass.value
    rol_nuevo = dd_rol.value
    
    if modelo.add_usuario(username, password, rol_nuevo):
        print(f"Controlador: Usuario {username} creado.")
        page.snack_bar = ft.SnackBar(ft.Text(f"Usuario {username} creado."), bgcolor=ft.Colors.GREEN_700)
    else:
        print(f"Controlador: Error al crear usuario {username}.")
        page.snack_bar = ft.SnackBar(ft.Text("Error al crear usuario (quizás ya existe).", color="white"), bgcolor=ft.Colors.RED_700)
    
    page.snack_bar.open = True
    campo_user.value = ""
    campo_pass.value = ""
    on_refrescar_click(e)

# --- FUNCIÓN PRINCIPAL Y ROUTING ---

def main(page: ft.Page):
    page.title = "Sistema de Comisaría"
    page.window_width = 1600
    page.window_height = 900
    
    def route_change(route):
        """El Router principal. Decide qué vista mostrar."""
        print(f"Navegando a: {page.route}")
        page.views.clear()
        
        rol = page.session.get("user_rol")
        
        # Si NO está logueado, forzar /login
        if not rol and page.route != "/login":
            page.go("/login")
            return # Detiene la ejecución

        # --- RUTAS ---
        
        if page.route == "/login":
            # 1. Creamos la VISTA y...
            # 2. Le pasamos la FUNCIÓN DEL CONTROLADOR que debe ejecutar
            page.views.append(
                vista_login.crear_vista_login(on_login_click)
            )
            
        elif page.route == "/dashboard":
            # 1. Obtenemos TODOS los datos del MODELO
            datos_act = modelo.get_estado_actuadores()
            datos_pres = modelo.get_presos()
            datos_user = modelo.get_usuarios()
            datos_sens = modelo.get_log_sensores()
            
            # 2. Creamos la VISTA y...
            # 3. Le pasamos los DATOS y las FUNCIONES DEL CONTROLADOR
            page.views.append(
                vista_dashboard_sensores.crear_dashboard_view(
                    page=page,
                    rol_usuario=rol,
                    datos_actuadores=datos_act,
                    datos_presos=datos_pres,
                    datos_usuarios=datos_user,
                    datos_sensores=datos_sens,
                    on_logout_click=on_logout_click,
                    on_refrescar_click=on_refrescar_click,
                    on_control_actuador_click=on_control_actuador_click,
                    on_crear_preso_click=on_crear_preso_click,
                    on_crear_usuario_click=on_crear_usuario_click
                )
            )
        
        else:
            # Si la ruta no existe, ir al login
            page.go("/login")

        page.update()

    page.on_route_change = route_change
    page.go(page.route) # Carga la ruta inicial (o /login si no hay sesión)

# --- Iniciar la aplicación ---
if __name__ == "__main__":
    ft.app(target=main)