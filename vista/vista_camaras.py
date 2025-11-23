import flet as ft
<<<<<<< HEAD

def crear_vista_camaras(on_logout_click, on_refrescar_click):
    """Define la vista de control de cámaras usando un componente de video."""
    
    vista = ft.View(
        route="/camaras",
        controls=[
            ft.AppBar(
                title=ft.Text("Vigilancia por Cámaras"),
                bgcolor=ft.colors.BLUE_GREY_900,
                actions=[
                    ft.IconButton(
                        icon=ft.icons.REFRESH,
                        on_click=on_refrescar_click,
                        tooltip="Refrescar vista"
                    ),
                    ft.IconButton(
                        icon=ft.icons.LOGOUT,
                        on_click=on_logout_click,
                        tooltip="Cerrar sesión"
                    ),
                ]
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Vista de Seguridad en Vivo (Video)", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                        ft.Divider(),
                        ft.Video(
                            # Asegúrate de que este archivo de video exista y sea accesible
                            src="camara_sim.mp4", 
                            # Propiedades opcionales del video
                            autoplay=True, 
                            loop=True,
                            width=800,
                            height=600,
                            fit=ft.ImageFit.CONTAIN
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                alignment=ft.alignment.center,
                expand=True
            )
        ]
    )
    return vista
=======
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
    camara_display = ft.Container(
        content=ft.Image(
            src="camara_sim.jpg",  # Asegúrate de tener esta imagen en la raíz o assets
            width=800,
            height=500,
            fit=ft.ImageFit.CONTAIN,
            border_radius=10,
        ),
        alignment=ft.alignment.center,
        expand=True
    )

    # Panel de estado (simulado)
    status_panel = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.CIRCLE, color=COLORS['bad'], size=12),  # 'bad' es rojo en tus temas (REC)
            ft.Text("GRABANDO EN VIVO", color=COLORS['bad'], weight=ft.FontWeight.BOLD),
            ft.Container(width=20),
            ft.Icon(ft.Icons.WIFI, color=COLORS['ok'], size=16),
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
>>>>>>> feature/Controlador_de_Camara_Fernando
