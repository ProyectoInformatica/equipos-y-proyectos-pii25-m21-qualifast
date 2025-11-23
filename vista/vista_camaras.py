import flet as ft
import os
import glob
from vista.temas import COLORS


def crear_vista_camaras(on_refrescar_click, on_volver_dashboard, on_ver_video_click):
    """
    Muestra la última captura disponible en 'capturas_simuladas' y un botón para ver el video grabado.
    """

    # 1. Buscar la imagen más reciente
    carpeta_capturas = "capturas_simuladas"
    imagen_mostrada = None
    texto_estado = "Esperando señal..."

    try:
        lista_archivos = glob.glob(os.path.join(carpeta_capturas, "*.jpg"))
        if lista_archivos:
            archivo_mas_reciente = max(lista_archivos, key=os.path.getctime)
            # Flet necesita rutas absolutas o relativas limpias
            imagen_mostrada = archivo_mas_reciente
            texto_estado = f"Señal en vivo: {os.path.basename(archivo_mas_reciente)}"
    except Exception as e:
        texto_estado = f"Error leyendo señal: {e}"

    # Contenedor de la imagen (Monitor)
    monitor_screen = ft.Container(
        content=ft.Image(
            src=imagen_mostrada if imagen_mostrada else "https://via.placeholder.com/640x360?text=SIN+SEÑAL",
            fit=ft.ImageFit.CONTAIN,
            gapless_playback=True,  # Ayuda a que no parpadee al refrescar
        ),
        bgcolor="black",
        border=ft.border.all(10, "#374151"),  # Marco del monitor
        border_radius=10,
        alignment=ft.alignment.center,
        expand=True
    )

    return ft.View(
        "/camaras",
        bgcolor=COLORS['bg'],
        controls=[
            ft.AppBar(
                title=ft.Text("Sala de Vigilancia - CCTV"),
                bgcolor=COLORS['card'],
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=on_volver_dashboard)
            ),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CIRCLE, color="red", size=15),
                        ft.Text("REC", color="red", weight="bold"),
                        ft.Container(width=20),
                        ft.Text(texto_estado, color=COLORS['text'])
                    ]),

                    monitor_screen,

                    ft.Row([
                        ft.ElevatedButton(
                            "Actualizar Fotograma",
                            icon=ft.Icons.REFRESH,
                            on_click=on_refrescar_click
                        ),
                        ft.ElevatedButton(
                            "Ver Grabación (Video)",
                            icon=ft.Icons.PLAY_CIRCLE_FILLED,
                            bgcolor=COLORS['accent'],
                            color=COLORS['bg'],
                            on_click=on_ver_video_click  # Navega a /video
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
                ])
            )
        ]
    )
