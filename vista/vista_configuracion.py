import flet as ft
from vista.temas import COLORS


def crear_vista_configuracion(config_actual, local_config, on_guardar_click, on_guardar_hardware_click):
    # 1. Recuperación de valores iniciales
    temp_actual = config_actual.get("temp_max", 28.0)
    luz_actual = config_actual.get("luz_min", 400.0)
    intervalo_actual = config_actual.get("intervalo_muestreo", 5.0)

    ip_esp32_actual = local_config.get("esp32_ip", "")
    ip_camara_actual = local_config.get("esp32_cam_ip", "")

    # --- FUNCIÓN DE VALIDACIÓN DE IP ---
    def es_ip_valida(ip_str):
        parts = ip_str.split(".")
        if len(parts) != 4: return False
        for p in parts:
            if not p.isdigit(): return False
            if not 0 <= int(p) <= 255: return False
        return True

    ip_text_style = ft.TextStyle(weight="bold", color="white", size=16)

    # --- BLOQUE 1: RED ---
    txt_ip_esp32 = ft.TextField(
        label="IP Chip ESP32",
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

    tarjeta_ips = ft.Container(
        content=ft.Column([
            ft.Text("🔗 Conexiones de Red (Hardware)", size=14, weight="bold", color=COLORS['accent']),
            ft.Row([txt_ip_esp32, txt_ip_camara], spacing=15)
        ], spacing=10),
        bgcolor=COLORS['room_bg'], padding=15, border_radius=10, border=ft.border.all(1, COLORS['glass'])
    )

    # --- FUNCIÓN DE ESCALAS ---
    def crear_escala(min_v, max_v, unidad, es_grande=False):
        paso = (max_v - min_v) / 4
        tamano_fuente = 12 if es_grande else 10

        def tick_marca(val, sufijo=""):
            return ft.Column([
                ft.Container(content=ft.Text("|", size=8, color=COLORS['muted'], weight="bold"), height=10,
                             alignment=ft.alignment.center),
                ft.Text(f"{val}{sufijo}", size=tamano_fuente, color=COLORS['muted'])
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        return ft.Container(
            padding=ft.padding.only(left=20, right=20, top=0),
            content=ft.Row([
                tick_marca(f"{min_v}"),
                tick_marca(f"{min_v + paso:.0f}"),
                tick_marca(f"{min_v + 2 * paso:.0f}"),
                tick_marca(f"{min_v + 3 * paso:.0f}"),
                tick_marca(f"{max_v}", unidad),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

    # --- BLOQUE 2: RENDIMIENTO (COMPACTADO) ---
    slider_intervalo = ft.Slider(min=1.0, max=30.0, divisions=29, value=intervalo_actual, label="{value} seg",
                                 active_color=COLORS['text'])

    tarjeta_rendimiento = ft.Container(
        content=ft.Column([
            ft.Text("⏱️ Rendimiento del Sistema", size=14, weight="bold", color=COLORS['accent']),
            ft.Text("Frecuencia de Lectura (Delay capturas ESP32)", weight="bold", size=12, color="white"),
            ft.Container(content=slider_intervalo, padding=ft.padding.symmetric(vertical=0)),  # Sin padding vertical
            crear_escala(1, 30, "s", es_grande=False),  # Escala pequeña
        ], spacing=2),  # Spacing mínimo
        bgcolor=COLORS['room_bg'], padding=12, border_radius=10, border=ft.border.all(1, COLORS['glass'])
        # Padding general reducido
    )

    # --- BLOQUE 3: UMBRALES (Lógicos) ---
    slider_temp = ft.Slider(min=15.0, max=35.0, divisions=20, value=temp_actual, label="{value} °C", active_color="red")
    slider_luz = ft.Slider(min=0.0, max=1000.0, divisions=100, value=luz_actual, label="{value} Lux",
                           active_color="yellow")

    tarjeta_umbrales = ft.Container(
        content=ft.Column([
            ft.Text("⚙️ Umbrales de Automatización", size=14, weight="bold", color=COLORS['accent']),

            ft.Text("🌡️ Temperatura (Activa Ventilador)", weight="bold", size=12, color=COLORS['text']),
            slider_temp,
            crear_escala(15, 35, "°C"),

            ft.Container(height=5),
            ft.Text("💡 Luz Mínima (Activa LEDs)", weight="bold", size=12, color=COLORS['text']),
            slider_luz,
            crear_escala(0, 1000, "Lux"),

        ], spacing=0),
        bgcolor=COLORS['room_bg'], padding=12, border_radius=10, border=ft.border.all(1, COLORS['glass'])
    )

    # --- LÓGICA GENERAL ---
    def validar_campos_envivo():
        for field in [txt_ip_esp32, txt_ip_camara]:
            if not es_ip_valida(field.value):
                field.error_text = "Formato no válido"
                field.bgcolor = ft.colors.with_opacity(0.1, "red")
            else:
                field.error_text = None
                field.bgcolor = None
        btn_guardar.text = "GUARDAR CAMBIOS"
        btn_guardar.bgcolor = COLORS['good']
        btn_guardar.update()
        txt_ip_esp32.update()
        txt_ip_camara.update()

    def accion_guardar(e):
        if not es_ip_valida(txt_ip_esp32.value) or not es_ip_valida(txt_ip_camara.value):
            btn_guardar.text = "FORMATO INVALIDO DE IP"
            btn_guardar.bgcolor = "red"
            btn_guardar.update()
            return

        nuevas_ips = {"esp32_ip": txt_ip_esp32.value, "esp32_cam_ip": txt_ip_camara.value}
        nuevos_umbrales = {
            "temp_max": float(slider_temp.value),
            "luz_min": float(slider_luz.value),
            "intervalo_muestreo": float(slider_intervalo.value)
        }

        on_guardar_hardware_click(nuevas_ips)
        on_guardar_click(e, nuevos_umbrales)

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

    # --- VISTA FINAL ENSAMBLADA ---
    return ft.Container(
        content=ft.Column([
            ft.Text("Configuración del Sistema", size=24, weight="bold", color=COLORS['accent']),
            ft.Divider(color=COLORS['glass']),

            tarjeta_ips,
            tarjeta_rendimiento,
            tarjeta_umbrales,

            ft.Container(height=5),
            ft.Row([btn_guardar], alignment=ft.MainAxisAlignment.CENTER)
        ], spacing=10, scroll=ft.ScrollMode.AUTO),
        padding=30, expand=True, bgcolor=COLORS['card'], border_radius=10, border=ft.border.all(1, COLORS['glass']),
        alignment=ft.alignment.top_center
    )