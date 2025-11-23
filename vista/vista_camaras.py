import flet as ft

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