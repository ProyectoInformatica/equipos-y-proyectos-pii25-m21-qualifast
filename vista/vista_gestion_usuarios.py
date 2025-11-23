import flet as ft
from vista.temas import COLORS


def crear_vista_usuarios(rol_actual, lista_usuarios, on_crear_usuario_handler):
    """
    Tarjeta de gestión de usuarios (solo Comisario).
    """

    user_header = ft.Text("Gestión de Usuarios", size=12, weight=ft.FontWeight.BOLD, color=COLORS['text'])

    # Inputs
    new_user_name = ft.TextField(
        label="Nuevo usuario",
        bgcolor=COLORS['glass'],
        color=COLORS['text'],
        border_color=COLORS['glass'],
        height=40,
        text_size=12,
        content_padding=10
    )
    new_user_pass = ft.TextField(
        label="Contraseña",
        password=True,
        bgcolor=COLORS['glass'],
        color=COLORS['text'],
        border_color=COLORS['glass'],
        height=40,
        text_size=12,
        content_padding=10
    )

    # Dropdown corregido
    new_user_role = ft.Dropdown(
        value="policia",
        options=[
            ft.dropdown.Option("inspector"),
            ft.dropdown.Option("policia")
        ],
        bgcolor=COLORS['glass'],
        color=COLORS['text'],
        expand=True,
        text_size=12,
        # height=40 (Eliminado por compatibilidad)
    )

    create_btn = ft.ElevatedButton(
        "Crear",
        bgcolor=COLORS['accent'],
        color='#06203a',
        on_click=lambda e: on_crear_usuario_handler(e, new_user_name, new_user_pass, new_user_role)
    )

    create_form = ft.Row([new_user_role, create_btn])
    user_form = ft.Column([new_user_name, new_user_pass, create_form], spacing=10)

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
        padding=10,
        border_radius=5,
        expand=True
    )

    # Tarjeta Principal (Expandida verticalmente)
    user_card = ft.Container(
        bgcolor=COLORS['card'],
        border=ft.border.all(2, COLORS['glass']),
        padding=12,
        visible=(rol_actual == 'comisario'),
        expand=True,
        content=ft.Column([
            user_header,
            user_form,
            ft.Divider(height=5, color="transparent"),
            user_list_container
        ])
    )

    return user_card