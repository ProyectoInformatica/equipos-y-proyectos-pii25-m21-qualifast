import flet as ft
from vista.temas import COLORS
import modelo.manejador_datosviejo as modelo


def crear_vista_usuarios(rol_actual, lista_usuarios, on_crear_usuario_handler, on_editar_usuario_handler, file_picker):
    user_header = ft.Text("Gestión de Personal Autorizado", size=24, weight=ft.FontWeight.BOLD, color=COLORS['accent'])

    new_user_name = ft.TextField(label="Nuevo usuario", bgcolor=COLORS['glass'], color=COLORS['text'],
                                 border_color=COLORS['glass'])
    new_user_pass = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, bgcolor=COLORS['glass'],
                                 color=COLORS['text'], border_color=COLORS['glass'])
    new_user_role = ft.Dropdown(value="policia",
                                options=[ft.dropdown.Option("comisario"), ft.dropdown.Option("inspector"),
                                         ft.dropdown.Option("policia")], bgcolor=COLORS['glass'], color=COLORS['text'])

    ruta_foto_nueva = [None]
    btn_foto_nueva = ft.ElevatedButton("📷 Añadir Foto", bgcolor=COLORS['glass'], color=COLORS['text'], height=50)

    def on_foto_nueva_picked(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            ruta_foto_nueva[0] = e.files[0].path
            btn_foto_nueva.text = "✅ Foto lista"
            btn_foto_nueva.bgcolor = COLORS['good']
        else:
            ruta_foto_nueva[0] = None
            btn_foto_nueva.text = "📷 Añadir Foto"
            btn_foto_nueva.bgcolor = COLORS['glass']
        btn_foto_nueva.update()

    def abrir_picker_nuevo(e):
        file_picker.on_result = on_foto_nueva_picked
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg"])

    btn_foto_nueva.on_click = abrir_picker_nuevo

    create_btn = ft.ElevatedButton("Crear Usuario", bgcolor=COLORS['good'], color='white', height=50,
                                   on_click=lambda e: on_crear_usuario_handler(e, new_user_name, new_user_pass,
                                                                               new_user_role, ruta_foto_nueva[0]))

    user_form = ft.Row([
        ft.Container(content=new_user_name, expand=2),
        ft.Container(content=new_user_pass, expand=2),
        ft.Container(content=new_user_role, expand=1),
        ft.Container(content=btn_foto_nueva, expand=1),
        create_btn
    ], spacing=10, alignment=ft.MainAxisAlignment.START)

    if rol_actual != 'comisario':
        user_form.visible = False

    user_list = ft.ListView(expand=True, spacing=10)

    if not lista_usuarios:
        user_list.controls.append(ft.Text("No hay usuarios registrados.", color=COLORS['muted']))
    else:
        for user in lista_usuarios:
            foto_b64 = user.get('foto')

            # --- SOLUCIÓN AVATAR (Contenedor Redondo con Image src_base64) ---
            avatar = ft.Container(
                width=40, height=40, border_radius=20, bgcolor=COLORS['glass'], alignment=ft.alignment.center,
                content=ft.Image(src_base64=foto_b64, fit=ft.ImageFit.COVER, border_radius=20, width=40,
                                 height=40) if foto_b64 else ft.Icon(ft.Icons.PERSON, color=COLORS['muted'])
            )

            row_controls = [
                avatar,
                ft.Container(width=10),
                ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS if user['rol'] == 'comisario' else ft.Icons.SECURITY,
                        color=COLORS['muted']),
                ft.Text(f"{user['user']}", size=16, weight="bold", color=COLORS['text'], expand=1),
                ft.Text(f"Rol: {user['rol'].upper()}", size=14, color=COLORS['accent'], expand=2)
            ]

            if rol_actual == 'comisario':
                def on_editar(e, u=user):
                    e.page.open(crear_dialogo_usuario("Editar", u, file_picker, on_editar_usuario_handler))

                def on_borrar(e, uid=user['id'], uname=user['user']):
                    if e.page.session.get("user_name") == uname:
                        e.page.snack_bar = ft.SnackBar(ft.Text("Acción denegada: No puedes eliminar tu propia cuenta."),
                                                       bgcolor="red")
                        e.page.snack_bar.open = True
                        e.page.update()
                    else:
                        if modelo.delete_usuario(uid):
                            e.page.go("/temp")
                            e.page.go("/usuarios")

                btn_row = ft.Row(spacing=5)
                btn_row.controls.append(ft.IconButton(icon=ft.Icons.EDIT, icon_color=COLORS['accent'], tooltip="Editar",
                                                      on_click=on_editar))
                btn_row.controls.append(
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=COLORS['bad'], tooltip="Eliminar",
                                  on_click=on_borrar))
                row_controls.append(btn_row)

            item_container = ft.Container(
                bgcolor=COLORS['room_bg'], padding=15, border_radius=8,
                content=ft.Row(row_controls, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
            user_list.controls.append(item_container)

    user_list_container = ft.Container(content=user_list, bgcolor=COLORS['glass'], padding=15, border_radius=8,
                                       expand=True)

    user_card = ft.Container(
        bgcolor=COLORS['card'], border=ft.border.all(2, COLORS['glass']), padding=25, border_radius=10, expand=True,
        content=ft.Column([user_header, user_form, ft.Divider(height=20, color=COLORS['glass']), user_list_container])
    )
    return user_card


def crear_dialogo_usuario(titulo, usuario_actual, file_picker, on_editar_usuario_handler):
    val_user = usuario_actual.get("user", "")
    val_pass = usuario_actual.get("password", "")
    val_rol = usuario_actual.get("rol", "policia")

    txt_user = ft.TextField(label="Nombre de Usuario", value=val_user, bgcolor=COLORS['glass'],
                            border_color=COLORS['muted'])
    txt_pass = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, value=val_pass,
                            bgcolor=COLORS['glass'], border_color=COLORS['muted'])
    dd_rol = ft.Dropdown(
        label="Rol del Sistema", value=val_rol, bgcolor=COLORS['glass'], border_color=COLORS['muted'],
        options=[ft.dropdown.Option("comisario"), ft.dropdown.Option("inspector"), ft.dropdown.Option("policia")]
    )

    ruta_foto_edit = [None]
    btn_foto_edit = ft.ElevatedButton("📷 Cambiar Foto", bgcolor=COLORS['glass'], color=COLORS['text'])

    def on_foto_edit_picked(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            ruta_foto_edit[0] = e.files[0].path
            btn_foto_edit.text = "✅ Nueva Foto"
            btn_foto_edit.bgcolor = COLORS['good']
        else:
            ruta_foto_edit[0] = None
            btn_foto_edit.text = "📷 Cambiar Foto"
            btn_foto_edit.bgcolor = COLORS['glass']
        btn_foto_edit.update()

    def abrir_picker_edit(e):
        file_picker.on_result = on_foto_edit_picked
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg"])

    btn_foto_edit.on_click = abrir_picker_edit

    dialogo = ft.AlertDialog(
        title=ft.Text(f"{titulo} Usuario", color=COLORS['accent']), bgcolor=COLORS['card'],
        content=ft.Column([txt_user, txt_pass, dd_rol, btn_foto_edit], tight=True, spacing=10)
    )

    def on_guardar(e):
        on_editar_usuario_handler(e, usuario_actual['id'], txt_user, txt_pass, dd_rol, dialogo, ruta_foto_edit[0])

    dialogo.actions = [
        ft.TextButton("Cancelar", on_click=lambda e: e.page.close(dialogo)),
        ft.ElevatedButton("Guardar", bgcolor=COLORS['good'], color="white", on_click=on_guardar)
    ]
    return dialogo