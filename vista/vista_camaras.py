import flet as ft
from vista.temas import COLORS
import modelo.manejador_datos as modelo  # Para obtener la IP


def crear_vista_camaras(on_refrescar_click, on_volver_dashboard, on_ver_video_click):
    # La cámara de los ESP32 suele emitir MJPEG en el puerto 81
    URL_CAMARA = f"http://{modelo.ESP32_IP}:81/stream"

    # Contenedor de la imagen (Monitor en vivo)
    monitor_screen = ft.Container(
        content=ft.Image(
            src=URL_CAMARA,
            fit=ft.ImageFit.CONTAIN,
            border_radius=10,
            # Si el ESP32 está apagado, mostrará este icono:
            error_content=ft.Column([
                ft.Icon(ft.Icons.VIDEOCAM_OFF, size=64, color=COLORS['muted']),
                ft.Text("Cámara Fuera de Línea", color=COLORS['muted'])
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ),
        bgcolor="black",
        border_radius=10,
        expand=True,
        width=800,
        alignment=ft.alignment.center
    )

    return ft.View(
        "/camaras",
        bgcolor=COLORS['bg'],
        appbar=ft.AppBar(
            title=ft.Text("Vigilancia CCTV"),
            bgcolor=COLORS['card'],
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=on_volver_dashboard)
        ),
        controls=[
            ft.Container(
                padding=20, expand=True,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CIRCLE, color="red", size=15),
                        ft.Text("EN VIVO (OV2640)", color="red", weight="bold"),
                    ]),
                    monitor_screen,
                    ft.Row([
                        ft.ElevatedButton("Ver Grabación (Simulada)", icon=ft.Icons.PLAY_CIRCLE_FILLED,
                                          bgcolor=COLORS['accent'], color=COLORS['bg'], on_click=on_ver_video_click),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
                ])
            )
        ]
    )