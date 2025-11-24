import flet as ft
from vista.temas import COLORS


def crear_vista_camaras(on_refrescar_click, on_volver_dashboard):
    """
    Crea la vista de cámaras de seguridad reproduciendo video local.
    """

    # --- APP BAR (Barra superior) ---
    app_bar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            icon_color=COLORS['text'],
            on_click=on_volver_dashboard,
            tooltip="Volver al Dashboard"
        ),
        title=ft.Text("Cámara de Seguridad - Grabación", color=COLORS['text'], size=16),
        bgcolor=COLORS['card'],
        actions=[
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                icon_color=COLORS['accent'],
                on_click=on_refrescar_click,
                tooltip="Reiniciar video"
            ),
            ft.Container(width=10)  # Espaciador
        ]
    )

    # --- CONTENIDO PRINCIPAL ---

    # Reproductor de Video
    # Flet buscará "videoGato.mp4" dentro de la carpeta 'assets' automáticamente
    video_player = ft.Video(
        expand=True,
        playlist=[ft.VideoMedia("videoGato.mp4")],
        playlist_mode=ft.PlaylistMode.LOOP,
        fill_color=COLORS['bg'],
        aspect_ratio=16/9,
        volume=100,
        autoplay=True,
        filter_quality=ft.FilterQuality.HIGH
    )

    # Panel de estado
    status_panel = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.CIRCLE, color=COLORS['bad'], size=12),  # 'bad' es rojo (REC)
            ft.Text("REPRODUCIENDO GRABACIÓN", color=COLORS['bad'], weight=ft.FontWeight.BOLD),
            ft.Container(width=20),
            ft.Icon(ft.Icons.HD, color=COLORS['good'], size=16),  # 'good' es verde
            ft.Text("Calidad 1080p", color=COLORS['muted'])
        ], alignment=ft.MainAxisAlignment.CENTER),
        padding=10
    )

    return ft.View(
        "/camaras",
        controls=[
            app_bar,
            status_panel,
            ft.Container(content=video_player, expand=True, padding=20)
        ],
        bgcolor=COLORS['bg'],
        padding=0
    )