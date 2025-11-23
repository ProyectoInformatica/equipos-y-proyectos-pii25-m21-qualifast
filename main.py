import flet as ft
import flet_webview  # <--- ¡AÑADE ESTA LÍNEA!
from pathlib import Path
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
    page.go(page.route) 

def on_control_actuador_click(e, actuador_id, nuevo_estado):
    """Maneja el clic en puertas, luces, ventilador, etc."""
    page = e.page
    rol = page.session.get("user_rol")
    
    if rol == "policia":
        print("Controlador: Permiso denegado (Policía).")
        page.snack_bar = ft.SnackBar(ft.Text("Permiso denegado.", color="white"), bgcolor=ft.Colors.RED_700)
        page.snack_bar.open = True
        page.update()
        return

    print(f"Controlador: Cambiando {actuador_id} a {nuevo_estado}")
    modelo.set_estado_actuador(actuador_id, nuevo_estado)
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
    
    print(f"Controlador: Añadiendo preso {nombre}")
    modelo.add_preso(nombre, "Delito pendiente")
    
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

def on_ver_camara_click(e):
    """
    Se ejecuta al pulsar 'Cam'. Navega a la nueva página de video.
    """
    page = e.page
    print("¡Click en cámara detectado! Navegando a /video")
    page.go("/video")

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
            page.views.append(
                vista_login.crear_vista_login(on_login_click)
            )
            
        elif page.route == "/dashboard":
            # 1. Obtenemos TODOS los datos del MODELO
            datos_act = modelo.get_estado_actuadores()
            datos_pres = modelo.get_presos()
            datos_user = modelo.get_usuarios()
            datos_sens = modelo.get_log_sensores()
            
            # 2. Creamos la VISTA y le pasamos todo
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
                    on_crear_usuario_click=on_crear_usuario_click,
                    on_ver_camara_click=on_ver_camara_click # <--- ¡LA LÍNEA QUE FALTABA!
                )
            )
        
        elif page.route == "/video":
            # --- ¡NUEVO! Obtenemos la ruta ABSOLUTA al video ---
            video_path = Path("assets/videoGato.mp4").resolve()
            video_url = video_path.as_uri() # <-- Esto la convierte en "file:///Users/..."
            
            print(f"Controlador: Cargando video desde {video_url}") # Para depurar

            page.views.append(
                ft.View(
                    route="/video",
                    bgcolor="#0f1724",
                    appbar=ft.AppBar(
                        title=ft.Text("Grabación - Sala de Vigilancia"),
                        bgcolor="#0f1724",
                        leading=ft.IconButton(
                            icon="arrow_back", # <-- Esto ya está arreglado
                            on_click=lambda e: page.go("/dashboard") 
                        )
                    ),
                    controls=[
                        flet_webview.WebView(
                            url=video_url, # <--- ¡ESTE ES EL ARREGLO FINAL!
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
    ft.app(target=main, assets_dir="assets") # <--- CRUCIAL: Añadir 'assets_dir'