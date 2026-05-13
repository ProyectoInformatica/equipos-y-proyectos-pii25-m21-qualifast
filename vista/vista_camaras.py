import flet as ft
from vista.temas import COLORS
import modelo.manejador_datos as modelo
import base64
import threading
import urllib.request
import time


class VideoStream(ft.Image):
    def __init__(self, url):
        # Componente de imagen nativo de Flet
        super().__init__(expand=True, fit=ft.ImageFit.CONTAIN, border_radius=10)
        self.url = url
        self.running = False

    def did_mount(self):
        # Al entrar en la pestaña, arrancamos el motor de captura
        self.running = True
        threading.Thread(target=self.update_frames, daemon=True).start()

    def will_unmount(self):
        # Al salir de la pestaña, detenemos la captura para no saturar el Wi-Fi
        self.running = False

    def update_frames(self):
        while self.running:
            try:
                # Nos conectamos a la cámara "en crudo"
                req = urllib.request.Request(self.url)
                stream = urllib.request.urlopen(req, timeout=5)
                bytes_data = b''

                while self.running:
                    # Leemos los datos a trozos
                    chunk = stream.read(8192)
                    if not chunk:
                        break  # Si la cámara se apaga, salimos

                    bytes_data += chunk

                    # Buscamos matemáticamente el inicio y fin de una foto JPEG pura
                    a = bytes_data.find(b'\xff\xd8')  # Inicio
                    b = bytes_data.find(b'\xff\xd9')  # Fin

                    if a != -1 and b != -1:
                        # ¡Hemos pescado un fotograma entero!
                        jpg = bytes_data[a:b + 2]
                        bytes_data = bytes_data[b + 2:]  # Limpiamos lo ya leído

                        # Inyectamos el fotograma directamente en la interfaz (sin OpenCV)
                        self.src_base64 = base64.b64encode(jpg).decode('utf-8')
                        self.update()

                    # Limpieza de seguridad por si el Wi-Fi da un tirón
                    if len(bytes_data) > 500000:
                        bytes_data = b''

            except Exception as e:
                # Si falla o se desconecta, no rompe la app, solo reintenta silenciosamente
                print(f"Cámara desconectada, buscando señal... ({e})")
                time.sleep(2)


def crear_vista_camaras(on_refrescar_click, on_volver_dashboard, on_ver_video_click):
    URL_CAMARA = f"http://{modelo.ESP32_CAM_IP}:81/stream"

    # --- PANTALLA PRINCIPAL ---
    monitor_screen = ft.Container(
        content=VideoStream(URL_CAMARA),
        bgcolor="#000000",
        border_radius=10,
        height=450,
        width=800,
        border=ft.border.all(2, COLORS['glass']),
        alignment=ft.alignment.center,
        clip_behavior=ft.ClipBehavior.HARD_EDGE
    )

    # Contenedor estético centrado
    contenido_centrado = ft.Column([
        ft.Row([
            ft.Icon(ft.Icons.CIRCLE, color="red", size=15),
            ft.Text("SEÑAL EN VIVO (OV2640)", color="red", weight="bold", size=16),
        ], alignment=ft.MainAxisAlignment.CENTER),

        ft.Container(height=10),

        monitor_screen,

        ft.Container(height=20),

        ft.Row([
            ft.ElevatedButton("Ver Grabación (Simulada)", icon=ft.Icons.PLAY_CIRCLE_FILLED,
                              bgcolor=COLORS['accent'], color=COLORS['bg'], on_click=on_ver_video_click),
        ], alignment=ft.MainAxisAlignment.CENTER)

    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

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
                padding=30,
                expand=True,
                alignment=ft.alignment.center,
                content=contenido_centrado
            )
        ]
    )