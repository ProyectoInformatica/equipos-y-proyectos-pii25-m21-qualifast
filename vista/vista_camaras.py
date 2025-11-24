import flet as ft
from vista.temas import COLORS


def crear_vista_camaras(on_refrescar_click, on_volver_dashboard):
    """
    Crea la vista de cámaras de seguridad.
    Muestra una imagen simulada y controles básicos.
    """

    # --- APP BAR (Barra superior) ---
    app_bar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            icon_color=COLORS['text'],
            on_click=on_volver_dashboard,
            tooltip="Volver al Dashboard"
        ),
        title=ft.Text("Cámara de Seguridad - Acceso Remoto", color=COLORS['text'], size=16),
        bgcolor=COLORS['card'],
        actions=[
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                icon_color=COLORS['accent'],
                on_click=on_refrescar_click,
                tooltip="Actualizar imagen"
            ),
            ft.Container(width=10)  # Espaciador
        ]
    )

    # --- CONTENIDO PRINCIPAL ---

    # Imagen de la cámara
    # NOTA: Asegúrate de que el archivo 'camara_sim.jpg' esté en la carpeta 'assets'
    # o en la raíz, dependiendo de cómo ejecutes flet.
    camara_display = ft.Container(
        content=ft.Image(
            src="camara_sim.jpg",
            width=800,
            height=500,
            fit=ft.ImageFit.CONTAIN,
            border_radius=10,
            error_content=ft.Text("No se encuentra la señal de video (falta imagen)", color="red")
        ),
        alignment=ft.alignment.center,
        expand=True
    )

    # Panel de estado (simulado)
    status_panel = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.CIRCLE, color=COLORS['bad'], size=12),  # 'bad' es rojo (REC)
            ft.Text("GRABANDO EN VIVO", color=COLORS['bad'], weight=ft.FontWeight.BOLD),
            ft.Container(width=20),
            # CORRECCIÓN AQUÍ: Usamos 'good' que sí existe en temas.py
            ft.Icon(ft.Icons.WIFI, color=COLORS['good'], size=16),
            ft.Text("Señal Estable", color=COLORS['muted'])
        ], alignment=ft.MainAxisAlignment.CENTER),
        padding=10
    )

    return ft.View(
        "/camaras",
        controls=[
            app_bar,
            status_panel,
            camara_display
        ],
        bgcolor=COLORS['bg'],
        padding=0
    )