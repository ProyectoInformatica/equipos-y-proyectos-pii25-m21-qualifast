import flet as ft


def crear_vista_login(on_login_click_handler, db_config_actual, on_save_db_config):
    # --- UI ESTADO CONEXIÓN ---
    icono_estado = ft.Icon(ft.Icons.WIFI_OFF, color="red", size=20)
    texto_estado = ft.Text("Desconectado de BD", color="red", size=14, weight="bold")

    row_estado = ft.Row(
        [icono_estado, texto_estado],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=5
    )

    # Función que actualiza el estado (será llamada desde main.py periódicamente)
    def update_status(is_connected):
        if is_connected:
            icono_estado.name = ft.Icons.WIFI
            icono_estado.color = "#22c55e"  # verde
            texto_estado.value = "Conectado a BD"
            texto_estado.color = "#22c55e"
        else:
            icono_estado.name = ft.Icons.WIFI_OFF
            icono_estado.color = "red"
            texto_estado.value = "Desconectado de BD"
            texto_estado.color = "red"

        try:
            row_estado.update()
        except:
            pass

    # --- DIÁLOGO CONFIGURACIÓN BD ---
    txt_host = ft.TextField(label="Host / IP", value=db_config_actual.get("db_host", ""))
    txt_port = ft.TextField(label="Puerto", value=str(db_config_actual.get("db_port", "3306")))
    txt_user = ft.TextField(label="Usuario", value=db_config_actual.get("db_user", ""))
    txt_pass = ft.TextField(label="Contraseña", password=True, can_reveal_password=True,
                            value=db_config_actual.get("db_pass", ""))
    txt_name = ft.TextField(label="Nombre BD", value=db_config_actual.get("db_name", ""))

    def guardar_config_bd(e):
        nuevos_datos = {
            "db_host": txt_host.value,
            "db_port": txt_port.value,
            "db_user": txt_user.value,
            "db_pass": txt_pass.value,
            "db_name": txt_name.value
        }
        on_save_db_config(nuevos_datos)
        e.page.close(dlg_config)
        update_status(False)  # Se forzará actualización en el próximo tick del main

    dlg_config = ft.AlertDialog(
        title=ft.Text("Configuración Base de Datos"),
        content=ft.Column([txt_host, txt_port, txt_user, txt_pass, txt_name], tight=True),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: e.page.close(dlg_config)),
            ft.ElevatedButton("Guardar", bgcolor="#38bdf8", color="black", on_click=guardar_config_bd),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # --- CAMPOS LOGIN ---
    def trigger_login(e):
        on_login_click_handler(e, campo_usuario, campo_password, texto_error)

    # Se ha añadido autofocus=True
    campo_usuario = ft.TextField(
        label="> USUARIO_", prefix_text="┌─ ", width=380, height=60,
        border=ft.border.only(bottom=ft.border.BorderSide(3, "#38bdf8")),
        bgcolor="transparent", focused_border_color="#38bdf8",
        text_style=ft.TextStyle(color="#22c55e", size=16, font_family="Consolas"),
        label_style=ft.TextStyle(color="#38bdf8", size=16, weight="bold"),
        cursor_color="#38bdf8", content_padding=ft.padding.only(left=15, top=20),
        on_submit=trigger_login, autofocus=True
    )

    campo_password = ft.TextField(
        label="> CONTRASEÑA_", prefix_text="└─ ", password=True, can_reveal_password=True,
        width=380, height=60, border=ft.border.only(bottom=ft.border.BorderSide(3, "#38bdf8")),
        bgcolor="transparent", focused_border_color="#38bdf8",
        text_style=ft.TextStyle(color="#22c55e", size=16, font_family="Consolas"),
        label_style=ft.TextStyle(color="#38bdf8", size=16, weight="bold"),
        cursor_color="#38bdf8", content_padding=ft.padding.only(left=15, top=20),
        on_submit=trigger_login
    )

    texto_error = ft.Text("", color="#ef4444", size=15, weight="bold", italic=True, text_align="center")

    boton_entrar = ft.Container(
        content=ft.Row([ft.Icon(ft.Icons.SHIELD, color="#0f1724", size=26),
                        ft.Text("  INICIAR SESIÓN", color="#0f1724", weight="bold", size=16)], alignment="center"),
        width=380, height=60, bgcolor="#38bdf8", border_radius=12, alignment=ft.alignment.center,
        shadow=ft.BoxShadow(spread_radius=2, blur_radius=25, color="#38bdf8", offset=(0, 8)),
        on_click=trigger_login, animate_scale=ft.Animation(300, "easeOut"),
    )

    # --- BOTÓN AJUSTES FLOTANTE ---
    btn_ajustes = ft.IconButton(
        icon=ft.Icons.SETTINGS,
        icon_color="#94a3b8",
        tooltip="Configurar Conexión",
        on_click=lambda e: e.page.open(dlg_config)
    )

    # --- VISTA COMPLETA ---
    vista = ft.View(
        "/login",
        bgcolor="#0f1724",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=30,
        controls=[
            ft.Container(expand=True), # Empuja el login hacia el centro
            ft.Container(
                width=460,
                padding=40,
                content=ft.Column([
                    ft.Text("COMISARÍA CENTRAL", size=42, weight="bold", color="#38bdf8", text_align="center", font_family="Impact"),
                    ft.Container(height=30),

                    row_estado,
                    ft.Container(height=20),

                    ft.Text("ACCESO RESTRINGIDO", size=22, weight="bold", color="#22c55e", text_align="center"),
                    ft.Text("Identificación requerida", size=14, color="#94a3b8", text_align="center"),
                    ft.Container(height=40),

                    campo_usuario,
                    campo_password,
                    ft.Container(height=35),
                    boton_entrar,
                    ft.Container(height=20),
                    texto_error,

                ], horizontal_alignment="center", spacing=12)
            ),
            ft.Container(expand=True), # Empuja el botón de ajustes hacia abajo
            # El botón de ajustes pasa a la esquina inferior derecha para no alterar el tabulador
            ft.Row([ft.Container(expand=True), btn_ajustes], alignment=ft.MainAxisAlignment.END)
        ]
    )

    # Inyectamos el callback en la vista para que main.py pueda llamarlo
    vista.data = {"update_status_callback": update_status}
    return vista