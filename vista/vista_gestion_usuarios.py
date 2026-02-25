import flet as ft
from vista.temas import COLORS
import modelo.manejador_datos as modelo


def crear_vista_usuarios(rol_actual, lista_usuarios, on_crear_usuario_handler):
    user_header = ft.Text("Gestión de Usuarios", size=12, weight=ft.FontWeight.BOLD, color=COLORS['text'])

    new_user_name = ft.TextField(label="Nuevo usuario", bgcolor=COLORS['glass'], color=COLORS['text'],
                                 border_color=COLORS['glass'], height=40, text_size=12, content_padding=10)
    new_user_pass = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, bgcolor=COLORS['glass'],
                                 color=COLORS['text'],
                                 border_color=COLORS['glass'], height=40, text_size=12, content_padding=10)
    new_user_role = ft.Dropdown(value="policia",
                                options=[ft.dropdown.Option("comisario"), ft.dropdown.Option("inspector"),
                                         ft.dropdown.Option("policia")],
                                bgcolor=COLORS['glass'], color=COLORS['text'], expand=True, text_size=12)
    create_btn = ft.ElevatedButton("Crear", bgcolor=COLORS['accent'], color='#06203a',
                                   on_click=lambda e: on_crear_usuario_handler(e, new_user_name, new_user_pass,
                                                                               new_user_role))

    create_form = ft.Row([new_user_role, create_btn])
    user_form = ft.Column([new_user_name, new_user_pass, create_form], spacing=10)

    # Restricción: Solo el comisario puede ver el formulario para crear usuarios
    if rol_actual != 'comisario':
        user_form.visible = False

    user_list = ft.ListView(expand=True, spacing=5)

    if not lista_usuarios:
        user_list.controls.append(ft.Text("No hay usuarios.", color=COLORS['muted']))
    else:
        for user in lista_usuarios:
            row_controls = [
                ft.Text(f"· {user['user']} ({user['rol']})", color=COLORS['text'], expand=True)
            ]

            # Restricción: Solo el comisario ve y puede usar los botones de edición y borrado
            if rol_actual == 'comisario':
                # --- Función local para editar ---
                def on_editar(e, u=user):
                    dialogo = crear_dialogo_usuario("Editar", u)
                    e.page.open(dialogo)

                # --- Función local para borrar ---
                def on_borrar(e, uid=user['id'], uname=user['user']):
                    # Evitar que el comisario se borre a sí mismo usando la info de la sesión
                    if e.page.session.get("user_name") == uname:
                        e.page.snack_bar = ft.SnackBar(ft.Text("Acción denegada: No puedes eliminar tu propia cuenta."),
                                                       bgcolor="red")
                        e.page.snack_bar.open = True
                        e.page.update()
                    else:
                        if modelo.delete_usuario(uid):
                            e.page.go("/temp")
                            e.page.go("/dashboard")

                btn_row = ft.Row(spacing=0)
                btn_row.controls.append(
                    ft.IconButton(icon=ft.Icons.EDIT, icon_color=COLORS['accent'], icon_size=16, on_click=on_editar)
                )
                btn_row.controls.append(
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=COLORS['bad'], icon_size=16,
                                  on_click=on_borrar)
                )
                row_controls.append(btn_row)

            item_container = ft.Container(
                bgcolor=COLORS['bg'], padding=5, border_radius=5,
                content=ft.Row(row_controls, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
            user_list.controls.append(item_container)

    user_list_container = ft.Container(content=user_list, bgcolor=COLORS['glass'], padding=10, border_radius=5,
                                       expand=True)

    user_card = ft.Container(
        bgcolor=COLORS['card'], border=ft.border.all(2, COLORS['glass']), padding=12, border_radius=10,
        expand=True,
        content=ft.Column([user_header, user_form, ft.Divider(color=COLORS['glass']), user_list_container])
    )
    return user_card


def crear_dialogo_usuario(titulo, usuario_actual):
    """
    Crea el modal emergente para editar los detalles del usuario.
    Es llamado directamente desde los botones de la lista generada.
    """
    val_user = usuario_actual.get("user", "")
    val_pass = usuario_actual.get("password", "")
    val_rol = usuario_actual.get("rol", "policia")

    txt_user = ft.TextField(label="Nombre de Usuario", value=val_user, bgcolor=COLORS['glass'],
                            border_color=COLORS['muted'])
    txt_pass = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, value=val_pass,
                            bgcolor=COLORS['glass'], border_color=COLORS['muted'])
    dd_rol = ft.Dropdown(
        label="Rol del Sistema",
        value=val_rol,
        bgcolor=COLORS['glass'],
        border_color=COLORS['muted'],
        options=[ft.dropdown.Option("comisario"), ft.dropdown.Option("inspector"), ft.dropdown.Option("policia")]
    )

    dialogo = ft.AlertDialog(
        title=ft.Text(f"{titulo} Usuario", color=COLORS['accent']),
        bgcolor=COLORS['card'],
        content=ft.Column([txt_user, txt_pass, dd_rol], tight=True, spacing=10)
    )

    def on_guardar(e):
        # Envía la actualización a la base de datos
        if modelo.update_usuario(usuario_actual['id'], txt_user.value, txt_pass.value, dd_rol.value):
            e.page.close(dialogo)
            e.page.go("/temp")
            e.page.go("/dashboard")
        else:
            e.page.snack_bar = ft.SnackBar(ft.Text("Error: El nombre de usuario ya está en uso."), bgcolor="red")
            e.page.snack_bar.open = True
            e.page.update()

    dialogo.actions = [
        ft.TextButton("Cancelar", on_click=lambda e: e.page.close(dialogo)),
        ft.ElevatedButton("Guardar", bgcolor=COLORS['good'], color="white", on_click=on_guardar)
    ]
    return dialogo