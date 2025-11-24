import flet as ft
import os
import glob
from vista.temas import COLORS

# AHORA ACEPTA 3 ARGUMENTOS (El último es para ir al video)
def crear_vista_camaras(on_refrescar_click, on_volver_dashboard, on_ver_video_click):
    """
    Muestra la última captura disponible en 'capturas_simuladas' y un botón para ver el video grabado.
    """

    # 1. Buscar la imagen más reciente en la carpeta simulada
    carpeta_capturas = "capturas_simuladas"
    imagen_mostrada = None
    texto_estado = "Esperando señal..."

    # Lógica para encontrar la última foto (simulando cámara en vivo)
    try:
        lista_archivos = glob.glob(os.path.join(carpeta_capturas, "*.jpg"))
        if lista_archivos:
            archivo_mas_reciente = max(lista_archivos, key=os.path.getctime)
            imagen_mostrada = archivo_mas_reciente
            texto_estado = f"Señal en vivo: {os.path.basename(archivo_mas_reciente)}"
    except Exception as e:
        texto_estado = f"Error leyendo señal: {e}"

    # 2. Contenedor de la imagen (El Monitor)
    monitor_screen = ft.Container(
        content=ft.Image(
            # Si hay imagen, la muestra. Si no, pone un placeholder
            src=imagen_mostrada if imagen_mostrada else "https://via.placeholder.com/640x360?text=SIN+SEÑAL",
            fit=ft.ImageFit.CONTAIN,
            gapless_playback=True,
        ),
        bgcolor="black",
        border=ft.border.all(10, "#374151"),
        border_radius=10,
        alignment=ft.alignment.center,
        expand=True
    )

    # 3. Estructura de la vista
    return ft.View(
        "/camaras",
        bgcolor=COLORS['bg'],
        controls=[
            # Barra superior
            ft.AppBar(
                title=ft.Text("Sala de Vigilancia - CCTV"),
                bgcolor=COLORS['card'],
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=on_volver_dashboard)
            ),
            # Contenido principal
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    # Indicadores LED
                    ft.Row([
                        ft.Icon(ft.Icons.CIRCLE, color="red", size=15),
                        ft.Text("REC", color="red", weight="bold"),
                        ft.Container(width=20),
                        ft.Text(texto_estado, color=COLORS['text'])
                    ]),

                    # Pantalla
                    monitor_screen,

                    # Botonera
                    ft.Row([
                        ft.ElevatedButton(
                            "Actualizar Fotograma",
                            icon=ft.Icons.REFRESH,
                            on_click=on_refrescar_click
                        ),
                        # ESTE BOTÓN USA EL TERCER ARGUMENTO
                        ft.ElevatedButton(
                            "Ver Grabación (Video)",
                            icon=ft.Icons.PLAY_CIRCLE_FILLED,
                            bgcolor=COLORS['accent'],
                            color=COLORS['bg'],
                            on_click=on_ver_video_click
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
                ])
            )
        ]
    )