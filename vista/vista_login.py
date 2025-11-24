# vista_login.py - VERSIÓN FINAL: COMISARÍA CENTRAL EN GRANDE + ESTILO CYBERPUNK
import flet as ft

def crear_vista_login(on_login_click_handler):
    # === CAMPOS ESTILO TERMINAL ===
    campo_usuario = ft.TextField(
        label="> USUARIO_",
        prefix_text="┌─ ",
        width=380,
        height=60,
        border=ft.border.only(bottom=ft.border.BorderSide(3, "#38bdf8")),
        bgcolor="transparent",
        focused_border_color="#38bdf8",
        text_style=ft.TextStyle(color="#22c55e", size=16, font_family="Consolas"),
        label_style=ft.TextStyle(color="#38bdf8", size=16, weight="bold"),
        cursor_color="#38bdf8",
        content_padding=ft.padding.only(left=15, top=20)
    )

    campo_password = ft.TextField(
        label="> CONTRASEÑA_",
        prefix_text="└─ ",
        password=True,
        can_reveal_password=True,
        width=380,
        height=60,
        border=ft.border.only(bottom=ft.border.BorderSide(3, "#38bdf8")),
        bgcolor="transparent",
        focused_border_color="#38bdf8",
        text_style=ft.TextStyle(color="#22c55e", size=16, font_family="Consolas"),
        label_style=ft.TextStyle(color="#38bdf8", size=16, weight="bold"),
        cursor_color="#38bdf8",
        content_padding=ft.padding.only(left=15, top=20)
    )

    texto_error = ft.Text(
        value="",
        color="#ef4444",
        size=15,
        weight="bold",
        italic=True,
        text_align="center"
    )

    boton_entrar = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.SHIELD, color="#0f1724", size=26),
            ft.Text("  INICIAR SESIÓN", color="#0f1724", weight="bold", size=16)
        ], alignment="center"),
        width=380,
        height=60,
        bgcolor="#38bdf8",
        border_radius=12,
        alignment=ft.alignment.center,
        shadow=ft.BoxShadow(spread_radius=2, blur_radius=25, color="#38bdf8", offset=(0, 8)),
        on_click=lambda e: on_login_click_handler(e, campo_usuario, campo_password, texto_error),
        animate_scale=ft.Animation(300, "easeOut"),
    )

    # === VISTA COMPLETA CON TÍTULO GRANDE ===
    return ft.View(
        "/login",
        bgcolor="#0f1724",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=30,
        controls=[
            ft.Container(
                width=460,
                padding=40,
                content=ft.Column([
                    # TÍTULO GRANDE Y POTENTE
                    ft.Container(height=40),
                    ft.Text(
                        "COMISARÍA CENTRAL",
                        size=42,
                        weight="bold",
                        color="#38bdf8",
                        text_align="center",
                        font_family="Impact"  # Opcional: más impacto
                    ),
                    ft.Container(height=50),

                    # ACCESO RESTRINGIDO
                    ft.Text(
                        "ACCESO RESTRINGIDO",
                        size=22,
                        weight="bold",
                        color="#22c55e",
                        text_align="center"
                    ),
                    ft.Text(
                        "Identificación requerida",
                        size=14,
                        color="#94a3b8",
                        text_align="center"
                    ),
                    ft.Container(height=60),

                    # FORMULARIO
                    campo_usuario,
                    campo_password,
                    ft.Container(height=35),
                    boton_entrar,
                    ft.Container(height=20),
                    texto_error,

                    ft.Container(expand=True),
                ],
                horizontal_alignment="center",
                spacing=12
                )
            )
        ]
    )