import flet as ft
from vista.temas import COLORS
import threading
import time


def crear_vista_configuracion(config_actual, local_config, on_guardar_click, on_guardar_hardware_click):
    # --- LÓGICA DE SENSORES ---
    val_temp = float(config_actual.get("temp_max", 28.0))
    val_luz = float(config_actual.get("luz_min", 400.0))

    # --- SLIDER DE RESPONSIVIDAD (NUEVO) ---
    # Permite ajustar el tiempo de espera del Heartbeat
    val_hb = float(local_config.get("heartbeat_timeout", 5))
    txt_hb_info = ft.Text(f"Sensibilidad de conexión: {int(val_hb)}s", color=COLORS['text'], size=14)

    def on_hb_change(e):
        txt_hb_info.value = f"Sensibilidad de conexión: {int(e.control.value)}s"
        txt_hb_info.update()

    slider_hb = ft.Slider(min=1, max=10, divisions=9, value=val_hb, label="{value}s",
                          active_color=COLORS['accent'], on_change=on_hb_change)

    # --- CAMPOS DE RED CON ETIQUETAS MEJORADAS ---
    def crear_campo_ip(label, valor):
        return ft.Column([
            ft.Text(label, size=12, color=COLORS['accent'], weight="bold"),
            ft.TextField(value=valor, width=320, bgcolor=COLORS['bg'], border_color=COLORS['glass'],
                         height=45, content_padding=10, text_size=14)
        ], spacing=5)

    txt_esp_ip = crear_campo_ip("IP PLACA BASE (ESP32)", local_config.get("esp32_ip", ""))
    txt_cam_ip = crear_campo_ip("IP CÁMARA DE SEGURIDAD", local_config.get("esp32_cam_ip", ""))

    # --- FEEDBACK DE APLICAR ---
    def animar_boton(btn):
        orig_text = btn.text
        btn.text = "¡APLICADO!"
        btn.bgcolor = COLORS['good']
        btn.update()

        def reset():
            time.sleep(2)
            btn.text = orig_text
            btn.bgcolor = COLORS['accent']
            try:
                btn.update()
            except:
                pass

        threading.Thread(target=reset, daemon=True).start()

    # --- TARJETA PRINCIPAL ---
    config_card = ft.Container(
        bgcolor=COLORS['card'], padding=40, border_radius=10, border=ft.border.all(1, COLORS['glass']),
        content=ft.Column([
            ft.Text("⚙️ Configuración de Automatización", size=24, weight="bold", color=COLORS['accent']),
            ft.Divider(color=COLORS['glass']),

            ft.Text("Control Ambiental (Ventilación)", weight="bold", size=16),
            ft.Slider(min=15, max=40, divisions=25, value=val_temp, active_color=COLORS['accent']),

            ft.Text("Control Iluminación (Luces)", weight="bold", size=16),
            ft.Slider(min=0, max=1000, divisions=50, value=val_luz, active_color=COLORS['accent']),

            ft.Divider(color=COLORS['glass'], height=40),

            ft.Text("📡 Configuración de Red (Hardware)", size=24, weight="bold", color=COLORS['accent']),
            ft.Divider(color=COLORS['glass']),

            ft.Row([
                txt_esp_ip,
                ft.ElevatedButton("Aplicar IP", bgcolor=COLORS['accent'], color="#000000",
                                  on_click=lambda e: [
                                      on_guardar_hardware_click({"esp32_ip": txt_esp_ip.controls[1].value}),
                                      animar_boton(e.control)])
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.END),

            ft.Row([
                txt_cam_ip,
                ft.ElevatedButton("Aplicar IP", bgcolor=COLORS['accent'], color="#000000",
                                  on_click=lambda e: [
                                      on_guardar_hardware_click({"esp32_cam_ip": txt_cam_ip.controls[1].value}),
                                      animar_boton(e.control)])
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.END),

            ft.Divider(color=COLORS['glass'], height=30),

            ft.Text("⏱️ Responsividad del Sistema", size=18, weight="bold", color=COLORS['accent']),
            ft.Text("Ajusta el margen de error para detectar si el controlador está Offline.", size=12,
                    color=COLORS['muted']),
            slider_hb,
            ft.Container(content=txt_hb_info, alignment=ft.alignment.center),

            ft.Container(height=20),
            ft.Row([
                ft.Container(expand=True),
                ft.ElevatedButton("Guardar Configuración Global", bgcolor=COLORS['good'], color="white", height=50,
                                  on_click=lambda e: on_guardar_click(e, {
                                      "temp_max": 28.0,
                                      "luz_min": 400.0,
                                      "heartbeat_timeout": slider_hb.value
                                  }))
            ], alignment=ft.MainAxisAlignment.END)
        ], tight=True)
    )

    return ft.Container(expand=True, content=config_card, alignment=ft.alignment.top_center)