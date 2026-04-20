import flet as ft
from vista.temas import COLORS
import modelo.manejador_datos as modelo


def crear_vista_camaras(on_refrescar_click, on_volver_dashboard, on_ver_video_click):
    # La cámara de los ESP32 suele emitir MJPEG en el puerto 81
    URL_CAMARA = f"http://{modelo.ESP32_IP}:81/stream"

    # --- MENSAJE DE ERROR MEJORADO Y CENTRADO ---
    panel_error = ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.VIDEOCAM_OFF, size=64, color=COLORS['bad']),
            ft.Text("SISTEMA CCTV FUERA DE LÍNEA", color=COLORS['bad'], weight="bold", size=18),
            ft.Container(height=10),
            ft.Text("Diagnóstico de Conexión:", color=COLORS['accent'], weight="bold", size=14),
            ft.Text("• El módulo ESP32-CAM no tiene suministro eléctrico.", color=COLORS['muted'], size=12),
            ft.Text("• La IP del ESP32 ha cambiado o es incorrecta.", color=COLORS['muted'], size=12),
            ft.Text("• Hay problemas de saturación en la red Wi-Fi local.", color=COLORS['muted'], size=12)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        alignment=ft.alignment.center,
        expand=True
    )

    # --- MONITOR PRINCIPAL CENTRADO ---
    monitor_screen = ft.Container(
        content=ft.Image(
            src=URL_CAMARA,
            fit=ft.ImageFit.CONTAIN,
            border_radius=10,
            # Si el ESP32 está apagado, mostrará el panel de diagnóstico:
            error_content=panel_error
        ),
        bgcolor="#000000",
        border_radius=10,
        expand=True,
        width=800,
        border=ft.border.all(2, COLORS['glass']),
        alignment=ft.alignment.center
    )

    # Todo el contenido se envuelve en una columna centrada
    contenido_centrado = ft.Column([
        # Indicador Superior
        ft.Row([
            ft.Icon(ft.Icons.CIRCLE, color="red", size=15),
            ft.Text("SEÑAL EN VIVO (OV2640)", color="red", weight="bold", size=16),
        ], alignment=ft.MainAxisAlignment.CENTER),

        ft.Container(height=10),

        # Pantalla
        monitor_screen,

        ft.Container(height=20),

        # Botonera Inferior
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
                alignment=ft.alignment.center,  # Fuerza el centrado absoluto del contenedor
                content=contenido_centrado
            )
        ]
    )