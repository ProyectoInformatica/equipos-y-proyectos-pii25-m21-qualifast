import flet as ft
from vista.temas import COLORS
import re


def crear_vista_configuracion(config_actual, local_config, on_guardar_click, on_guardar_hardware_click):
    # 1. Recuperación de valores iniciales
    temp_actual = config_actual.get("temp_max", 28.0)
    luz_actual = config_actual.get("luz_min", 400.0)
    humo_actual = config_actual.get("humo_max", 800.0)
    ip_esp32_actual = local_config.get("esp32_ip", "")
    ip_camara_actual = local_config.get("esp32_cam_ip", "")

    # --- FUNCIÓN DE VALIDACIÓN DE IP ---
    def es_ip_valida(ip_str):
        # Comprobar formato X.X.X.X y que no tenga letras
        parts = ip_str.split(".")
        if len(parts) != 4:
            return False
        for p in parts:
            if not p.isdigit(): return False
            if not 0 <= int(p) <= 255: return False
        return True

    # --- ESTILOS Y CAMPOS DE TEXTO IP ---
    ip_text_style = ft.TextStyle(weight="bold", color="white", size=16)

    txt_ip_esp32 = ft.TextField(
        label="IP Chip ESP32",  # Nombre actualizado
        value=ip_esp32_actual,
        prefix_icon=ft.Icons.WIFI,
        border_color=COLORS['accent'],
        text_style=ip_text_style,
        expand=True,
        height=65,
        on_change=lambda e: validar_campos_envivo()
    )

    txt_ip_camara = ft.TextField(
        label="IP Cámara ESP32-CAM",
        value=ip_camara_actual,
        prefix_icon=ft.Icons.VIDEOCAM,
        border_color=COLORS['accent'],
        text_style=ip_text_style,
        expand=True,
        height=65,
        on_change=lambda e: validar_campos_envivo()
    )

    def validar_campos_envivo():
        # Feedback visual inmediato al escribir
        for field in [txt_ip_esp32, txt_ip_camara]:
            if not es_ip_valida(field.value):
                field.error_text = "Formato no válido"
                field.bgcolor = ft.colors.with_opacity(0.1, "red")
            else:
                field.error_text = None
                field.bgcolor = None

        # Resetear estado del botón si se estaba mostrando un error previo
        btn_guardar.text = "GUARDAR CAMBIOS"
        btn_guardar.bgcolor = COLORS['good']
        btn_guardar.update()
        txt_ip_esp32.update()
        txt_ip_camara.update()

    # --- COMPONENTE DE ESCALA DE REFERENCIA ---
    def crear_escala(min_v, max_v, unidad):
        # Calcula 4 puntos intermedios para la escala
        paso = (max_v - min_v) / 4
        return ft.Container(
            padding=ft.padding.only(left=10, right=10, top=2),
            content=ft.Row([
                ft.Text(f"{min_v}", size=10, color=COLORS['muted']),
                ft.Text(f"{min_v + paso:.0f}", size=10, color=COLORS['muted']),
                ft.Text(f"{min_v + 2 * paso:.0f}", size=10, color=COLORS['muted']),
                ft.Text(f"{min_v + 3 * paso:.0f}", size=10, color=COLORS['muted']),
                ft.Text(f"{max_v}{unidad}", size=10, color=COLORS['muted']),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

    # --- SLIDERS (Rendimiento optimizado) ---
    # Al no usar 'on_change', el slider se mueve de forma nativa y fluida
    slider_temp = ft.Slider(min=15.0, max=40.0, divisions=25, value=temp_actual, label="{value} °C", active_color="red")
    slider_luz = ft.Slider(min=0.0, max=1000.0, divisions=100, value=luz_actual, label="{value} Lux",
                           active_color="yellow")
    slider_humo = ft.Slider(min=0.0, max=1000.0, divisions=100, value=humo_actual, label="{value} ppm",
                            active_color="orange")

    # --- LÓGICA DE GUARDADO ---
    def accion_guardar(e):
        # 1. Validar IPs antes de procesar
        if not es_ip_valida(txt_ip_esp32.value) or not es_ip_valida(txt_ip_camara.value):
            btn_guardar.text = "FORMATO INVALIDO DE IP"
            btn_guardar.bgcolor = "red"
            btn_guardar.update()
            return

        # 2. Recopilar datos
        nuevas_ips = {"esp32_ip": txt_ip_esp32.value, "esp32_cam_ip": txt_ip_camara.value}
        nuevos_umbrales = {
            "temp_max": float(slider_temp.value),
            "luz_min": float(slider_luz.value),
            "humo_max": float(slider_humo.value)
        }

        # 3. Llamar a los manejadores (se quedan en la misma vista)
        on_guardar_hardware_click(nuevas_ips)
        on_guardar_click(e, nuevos_umbrales)

        # 4. Feedback de éxito sin cerrar
        btn_guardar.text = "CAMBIOS GUARDADOS ✅"
        btn_guardar.bgcolor = COLORS['good']
        btn_guardar.icon = ft.Icons.CHECK_CIRCLE
        btn_guardar.update()

    btn_guardar = ft.ElevatedButton(
        "GUARDAR CAMBIOS",
        icon=ft.Icons.SAVE,
        bgcolor=COLORS['good'],
        color=COLORS['bg'],
        height=45,
        on_click=accion_guardar
    )

    # --- DISEÑO FINAL ---
    return ft.Container(
        content=ft.Column([
            ft.Text("Configuración del Sistema", size=24, weight="bold", color=COLORS['accent']),
            ft.Divider(color=COLORS['glass']),

            # Bloque de Conexiones
            ft.Container(
                content=ft.Column([
                    ft.Text("🔗 Conexiones de Red (Hardware)", size=14, weight="bold", color=COLORS['accent']),
                    ft.Row([txt_ip_esp32, txt_ip_camara], spacing=15)
                ], spacing=10),
                bgcolor=COLORS['room_bg'], padding=15, border_radius=10, border=ft.border.all(1, COLORS['glass'])
            ),

            # Bloque de Umbrales con Escalas
            ft.Container(
                content=ft.Column([
                    ft.Text("⚙️ Umbrales de Automatización", size=14, weight="bold", color=COLORS['accent']),

                    ft.Text("🌡️ Temperatura (Activa Ventilador)", weight="bold", size=12, color=COLORS['text']),
                    slider_temp,
                    crear_escala(15, 40, "°C"),

                    ft.Container(height=10),
                    ft.Text("💡 Luz Mínima (Activa LEDs)", weight="bold", size=12, color=COLORS['text']),
                    slider_luz,
                    crear_escala(0, 1000, "Lux"),

                    ft.Container(height=10),
                    ft.Text("🔥 Alerta de Humo/Gas (Alarma)", weight="bold", size=12, color=COLORS['text']),
                    slider_humo,
                    crear_escala(0, 1000, "ppm"),

                ], spacing=0),
                bgcolor=COLORS['room_bg'], padding=15, border_radius=10, border=ft.border.all(1, COLORS['glass'])
            ),

            ft.Container(height=5),
            ft.Row([btn_guardar], alignment=ft.MainAxisAlignment.CENTER)
        ], spacing=10, scroll=ft.ScrollMode.AUTO),
        padding=30, expand=True, bgcolor=COLORS['card'], border_radius=10, border=ft.border.all(1, COLORS['glass']),
        alignment=ft.alignment.top_center
    )