import flet as ft
from vista.temas import COLORS # Importamos los colores

def crear_vista_usuarios(rol_actual, lista_usuarios, on_crear_usuario_handler):
    """
    Crea la tarjeta de gestión de usuarios.
    Solo es visible para el 'comisario'.
    """
    
    user_header = ft.Text("Gestión de Usuarios", size=12, weight=ft.FontWeight.BOLD, color=COLORS['text'])
    
    new_user_name = ft.TextField(
        label="Nuevo usuario", 
        bgcolor=COLORS['glass'], 
        color=COLORS['text'], 
        border_color=COLORS['glass']
    )
    new_user_pass = ft.TextField(
        label="Contraseña", 
        password=True, 
        bgcolor=COLORS['glass'], 
        color=COLORS['text'], 
        border_color=COLORS['glass']
    )
    new_user_role = ft.Dropdown(
        value="policia", 
        options=[
            ft.dropdown.Option("inspector"),
            ft.dropdown.Option("policia")
        ], 
        bgcolor=COLORS['glass'], 
        color=COLORS['text'],
        expand=True
    )
    
    create_btn = ft.ElevatedButton(
        "Crear", 
        bgcolor=COLORS['accent'], 
        color='#06203a',
        # Llama al handler del controlador pasando los campos
        on_click=lambda e: on_crear_usuario_handler(
            e, 
            new_user_name, 
            new_user_pass, 
            new_user_role
        )
    )
    create_form = ft.Row([new_user_role, create_btn])
    user_form = ft.Column([new_user_name, new_user_pass, create_form])

    # Lista de usuarios
    user_list = ft.ListView(expand=True, spacing=5)
    if not lista_usuarios:
        user_list.controls.append(ft.Text("No hay usuarios.", color=COLORS['muted']))
    else:
        for user in lista_usuarios:
            user_list.controls.append(
                ft.Text(f"· {user['user']} ({user['rol']})", color=COLORS['text'])
            )
            
    user_list_container = ft.Container(
        content=user_list, 
        bgcolor=COLORS['glass'], 
        height=100,
        padding=10
    )
    
    user_card = ft.Container(
        width=320, 
        bgcolor=COLORS['card'], 
        border=ft.border.all(2, COLORS['glass']), 
        padding=12,
        # ¡CONTROL DE PERMISOS!
        visible=(rol_actual == 'comisario'),
        content=ft.Column([
            user_header, 
            user_form, 
            ft.Divider(height=5, color="transparent"),
            user_list_container
        ])
    )
    
    return user_card