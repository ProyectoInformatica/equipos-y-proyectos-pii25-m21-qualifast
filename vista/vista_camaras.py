import flet as ft
from vista.temas import COLORS
import modelo.manejador_datos as modelo
import base64
import threading
import urllib.request
import time


class VideoStream(ft.Stack):
    def __init__(self, url):
        super().__init__(expand=True)
        self.url = url
        self.running = False

        self.img = ft.Image(expand=True, fit=ft.ImageFit.CONTAIN, border_radius=10)

        # Mensaje de error mucho más limpio y profesional (sin la variable de excepción pura)
        self.error_text = ft.Text("ESTABLECIENDO ENLACE CON LA CÁMARA...", color="white", weight="bold", size=15,
                                  text_align="center")
        self.error_container = ft.Container(
            content=self.error_text,
            alignment=ft.alignment.center,
            bgcolor="#aa000000",
            expand=True,
            border_radius=10,
            padding=20
        )

        self.controls = [self.img, self.error_container]

    def did_mount(self):
        self.running = True
        threading.Thread(target=self.update_frames, daemon=True).start()

    def will_unmount(self):
        self.running = False

    def update_frames(self):
        while self.running:
            try:
                req = urllib.request.Request(self.url)
                stream = urllib.request.urlopen(req, timeout=3)
                bytes_data = b''

                if self.error_container.visible:
                    self.error_container.visible = False
                    try:
                        self.update()
                    except:
                        pass

                while self.running:
                    chunk = stream.read(8192)
                    if not chunk:
                        break

                    bytes_data += chunk
                    a = bytes_data.find(b'\xff\xd8')
                    b = bytes_data.find(b'\xff\xd9')

                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b + 2]
                        bytes_data = bytes_data[b + 2:]
                        self.img.src_base64 = base64.b64encode(jpg).decode('utf-8')
                        self.img.update()

                    if len(bytes_data) > 500000:
                        bytes_data = b''

            except Exception as e:
                # Traducción del error técnico a lenguaje entendible por el usuario
                error_str = str(e).lower()
                if "timed out" in error_str:
                    motivo = "El dispositivo tardó demasiado en responder."
                elif "connection refused" in error_str:
                    motivo = "Conexión rechazada por el dispositivo."
                else:
                    motivo = "El dispositivo no está accesible en la red."

                mensaje_ui = f"⚠️ SEÑAL DE VÍDEO PERDIDA\nBuscando conexión en {modelo.ESP32_CAM_IP}...\n\nMotivo: {motivo}"

                if not self.error_container.visible:
                    print(f"[Aviso] Cámara no disponible. {motivo}")

                self.error_text.value = mensaje_ui
                self.error_container.visible = True
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
                              bgcolor=COLORS['accent'], color="#000000", on_click=on_ver_video_click),
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
        controls=[ft.Container(padding=30, expand=True, alignment=ft.alignment.center, content=contenido_centrado)]
    )