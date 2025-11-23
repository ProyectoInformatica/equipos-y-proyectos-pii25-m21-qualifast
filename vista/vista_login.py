import flet as ft


def crear_vista_login(on_login_click_handler):
    """
    Crea la ft.View para el login.
    Recibe la función del controlador que debe ejecutar al hacer clic.
    """

    campo_usuario = ft.TextField(
        label="Usuario",
        width=300,
        border_color="white"
    )

    campo_password = ft.TextField(
        label="Contraseña",
        password=True,
        width=300,
        border_color="white"
    )

    texto_error = ft.Text(value="", color=ft.Colors.RED)

    boton_entrar = ft.ElevatedButton(
        text="Entrar",
        on_click=lambda e: on_login_click_handler(
            e,  # El evento
            campo_usuario,  # Pasa el control de usuario
            campo_password,  # Pasa el control de password
            texto_error  # Pasa el control de error
        ),
        bgcolor=ft.Colors.BLUE_700,
        color="white",
        width=300
    )

    return ft.View(
        "/login",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("SISTEMA DE COMISARÍA", size=32, weight=ft.FontWeight.BOLD),
                        ft.Divider(height=20, color="transparent"),
                        campo_usuario,
                        campo_password,
                        ft.Divider(height=10, color="transparent"),
                        boton_entrar,
                        texto_error
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15
                ),
                expand=True,
                alignment=ft.alignment.center
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        bgcolor="#0f1724"
    )