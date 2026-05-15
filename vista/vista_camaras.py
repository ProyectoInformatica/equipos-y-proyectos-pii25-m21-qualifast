import flet as ft
from vista.temas import COLORS
import modelo.manejador_datos as modelo
import base64
import threading
import urllib.request
import time


class VideoStream(ft.Container):
    def __init__(self, url):
        super().__init__(
            expand=True,
            border_radius=10,
            alignment=ft.alignment.center,
            clip_behavior=ft.ClipBehavior.HARD_EDGE
        )
        self.url = url
        self.running = False

        # 1. Píxel transparente en base64 para evitar el error inicial de Flet
        pixel_transparente = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

        self.img_control = ft.Image(
            src_base64=pixel_transparente,
            expand=True,
            fit=ft.ImageFit.CONTAIN,
            visible=False  # Oculto hasta que haya señal
        )

        # 2. El recuadro translúcido de error/espera con nuestro mensaje controlado
        self.error_control = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.VIDEOCAM_OFF, size=50, color=COLORS['muted']),
                ft.Text("CONEXIÓN CON CÁMARA PERDIDA", weight="bold", color=COLORS['text'], size=16),
                ft.Text("Intentando reconectar o cámara apagada...", size=12, color=COLORS['muted'])
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            # SOLUCIÓN: Usamos código Hexadecimal ARGB en lugar de ft.colors (#0D = 5% opacidad)
            bgcolor="#0DFFFFFF",
            expand=True,
            alignment=ft.alignment.center
        )

        # Por defecto, el contenido del contenedor es el error
        self.content = self.error_control

    def did_mount(self):
        self.running = True
        threading.Thread(target=self.update_frames, daemon=True).start()

    def will_unmount(self):
        self.running = False

    def update_frames(self):
        while self.running:
            try:
                req = urllib.request.Request(self.url)
                stream = urllib.request.urlopen(req, timeout=5)
                bytes_data = b''

                # Si engancha la señal, cambiamos el contenido a la imagen
                self.content = self.img_control
                self.img_control.visible = True
                self.update()

                while self.running:
                    chunk = stream.read(8192)
                    if not chunk: break

                    bytes_data += chunk
                    a = bytes_data.find(b'\xff\xd8')
                    b = bytes_data.find(b'\xff\xd9')

                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b + 2]
                        bytes_data = bytes_data[b + 2:]
                        self.img_control.src_base64 = base64.b64encode(jpg).decode('utf-8')
                        self.update()

                    if len(bytes_data) > 500000: bytes_data = b''

            except Exception:
                # Si falla (no hay cámara), volvemos a mostrar el recuadro translúcido
                self.content = self.error_control
                self.img_control.visible = False
                try:
                    self.update()
                except:
                    pass
                time.sleep(2)


def crear_vista_camaras(on_refrescar_click, on_volver_dashboard, on_ver_video_click):
    URL_CAMARA = f"http://{modelo.ESP32_CAM_IP}:81/stream"

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
            ft.Container(padding=30, expand=True, alignment=ft.alignment.center, content=contenido_centrado)
        ]
    )