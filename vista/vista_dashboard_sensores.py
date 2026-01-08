import flet as ft
from vista.temas import COLORS, DEVICE_ICONS
import vista.vista_gestion_presos
import vista.vista_gestion_usuarios


# NOTA: Ya no importamos 'modelo' ni 'threading'. Cumplimos MVC.

def crear_dashboard_view(
        page: ft.Page,
        rol_usuario: str,
        nombre_usuario: str,
        datos_actuadores_iniciales: dict,
        datos_presos: list,
        datos_usuarios: list,
        datos_sensores_iniciales: list,
        on_logout_click,
        on_refrescar_click,
        on_control_actuador_click,
        on_crear_usuario_click,
        on_borrar_preso_click,
        on_ver_camaras_click,
        on_abrir_crear_preso,
        on_abrir_editar_preso,
        on_ver_historico_click,
        on_configuracion_click,
        on_cambiar_modo_click,
        on_ver_consumo_click=None  # Nuevo parametro
):
    puede_controlar = (rol_usuario != 'policia')
    es_admin = (rol_usuario in ['comisario', 'inspector'])

    # --- HEADER ---
    logo_img = ft.Image(src="logo.png", height=40, fit=ft.ImageFit.CONTAIN)
    brand_text = ft.Column([
        ft.Text("QUALIFAST BUILDINGS", size=16, weight=ft.FontWeight.W_900, color=COLORS['text'],
                font_family="Verdana"),
        ft.Text("PLANTA COMISARÍA", size=10, weight=ft.FontWeight.BOLD, color=COLORS['accent'])
    ], spacing=0)

    legend_content = ft.Row([
        ft.Text("🟢 Abierta 🔴 Cerrada", size=10, color=COLORS['muted']),
        ft.Container(width=10, height=15, border=ft.border.only(left=ft.border.BorderSide(1, COLORS['muted']))),
        ft.Icon(ft.Icons.PERSON, size=12, color=COLORS['accent']),
        ft.Text(f"{nombre_usuario} ({rol_usuario.upper()})", size=11, weight="bold", color=COLORS['text'])
    ], alignment="center")

    boton_camaras = ft.ElevatedButton("Ver Cámaras", icon=ft.Icons.CAMERA_ALT, bgcolor=COLORS['glass'],
                                      color=COLORS['text'], on_click=on_ver_camaras_click)
    logout_btn = ft.ElevatedButton("Salir", bgcolor=COLORS['bg'], color=COLORS['bad'], on_click=on_logout_click)

    topbar = ft.Container(
        content=ft.Row([
            logo_img, ft.Container(width=10), brand_text, ft.Container(width=20),
            legend_content, ft.Container(expand=True),
            boton_camaras, ft.Container(width=10), logout_btn
        ], alignment="center", vertical_alignment="center"),
        padding=ft.padding.symmetric(horizontal=5, vertical=5)
    )

    # --- MAPA INTERACTIVO ---
    rooms_config = [
        {"name": "Recepción", "l": 20, "t": 20, "w": 300, "h": 120},
        {"name": "Vigilancia", "l": 340, "t": 20, "w": 300, "h": 120},
        {"name": "Despacho", "l": 20, "t": 160, "w": 300, "h": 120},
        {"name": "C1", "l": 340, "t": 160, "w": 150, "h": 60},
        {"name": "C2", "l": 490, "t": 160, "w": 150, "h": 60},
        {"name": "C3", "l": 340, "t": 220, "w": 150, "h": 60},
        {"name": "C4", "l": 490, "t": 220, "w": 150, "h": 60},
    ]

    map_stack_controls = []
    for r in rooms_config:
        map_stack_controls.append(ft.Container(
            left=r["l"], top=r["t"], width=r["w"], height=r["h"],
            bgcolor=COLORS['room_bg'], border=ft.border.all(2, '#5a7a9e'),
            content=ft.Text(r["name"], color='#cfe7ff', size=14, weight="bold"),
            alignment=ft.alignment.center
        ))

    # Puertas
    doors_config = [
        {"id": "door-1", "l": 320, "t": 60, "w": 20, "h": 40, "label": "P1"},
        {"id": "door-2", "l": 320, "t": 200, "w": 20, "h": 40, "label": "P2"},
        {"id": "door-3", "l": 150, "t": 140, "w": 40, "h": 20, "label": "P3"},
        {"id": "door-4", "l": 470, "t": 140, "w": 40, "h": 20, "label": "P4"},
    ]

    controles_puertas = {}
    for d in doors_config:
        pid = d["id"]
        estado = datos_actuadores_iniciales.get(pid, {}).get("estado", "cerrada")
        color = COLORS['door_open'] if estado == "abierta" else COLORS['door_closed']

        cnt = ft.Container(
            left=d["l"], top=d["t"], width=d["w"], height=d["h"],
            bgcolor=color, border=ft.border.all(1, "white"),
            on_click=lambda e, p=pid: on_control_actuador_click(e, p, None),
            content=ft.Text(d["label"], size=8, color="white", weight="bold"),
            alignment=ft.alignment.center,
            animate=ft.Animation(300, "easeOut")
        )
        controles_puertas[pid] = cnt
        map_stack_controls.append(cnt)

    # Iconos
    icon_fan_map = ft.Icon(DEVICE_ICONS['fan'], size=20, color=COLORS['muted'])
    icon_led_map = ft.Icon(DEVICE_ICONS['leds'], size=20, color=COLORS['muted'])

    map_stack_controls.extend([
        ft.Container(left=580, top=30, content=ft.Icon(ft.Icons.VIDEOCAM, color="#fb7185", size=20), bgcolor="white",
                     border_radius=15, on_click=on_ver_camaras_click),
        ft.Container(left=477, top=206, content=ft.Text(DEVICE_ICONS['ldr'], size=20), tooltip="LDR"),

        # Fuego (Referencia Vertical: 600)
        ft.Container(left=600, top=179, content=ft.Text(DEVICE_ICONS['mq-2'], size=20), tooltip="MQ-2"),

        # Aire (Referencia Horizontal: 245)
        ft.Container(left=345, top=245, content=ft.Text(DEVICE_ICONS['mq-135'], size=20), tooltip="MQ-135"),

        # --- NUEVO ICONO HUMEDAD (Intersección: Left 600, Top 245) ---
        ft.Container(left=600, top=245, content=ft.Text("💧", size=20), tooltip="Humedad"),
        # -------------------------------------------------------------

        ft.Container(left=345, top=180, content=ft.Text(DEVICE_ICONS['dht22'], size=16), tooltip="DHT22"),
        ft.Container(left=400, top=165, content=icon_fan_map, tooltip="Ventilación"),
        ft.Container(left=480, top=210, content=icon_led_map, tooltip="Iluminación Central"),
    ])

    map_card = ft.Container(content=ft.Column([
        ft.Text("Plano Interactivo", color=COLORS['text'], size=16),
        ft.Row([ft.Stack(controls=map_stack_controls, width=680, height=320)], alignment="center")
    ], alignment="center"), bgcolor=COLORS['card'], border=ft.border.all(2, COLORS['glass']), padding=10,
        alignment=ft.alignment.center)

    # --- BOTTOM ROW ---
    vista_presos = vista.vista_gestion_presos.crear_vista_presos(datos_presos, on_abrir_crear_preso,
                                                                 on_abrir_editar_preso, on_refrescar_click,
                                                                 on_borrar_preso_click)
    vista_usuarios = vista.vista_gestion_usuarios.crear_vista_usuarios(rol_usuario, datos_usuarios,
                                                                       on_crear_usuario_click)
    bottom_row = ft.Container(height=450, content=ft.Row(
        [ft.Container(content=vista_presos, expand=1), ft.Container(content=vista_usuarios, expand=1)], spacing=12,
        expand=True))
    left_column = ft.Column(spacing=12, expand=True, scroll=ft.ScrollMode.AUTO, controls=[topbar, map_card, bottom_row])

    # --- PANEL DERECHO ---
    right_content = ft.Column(spacing=12, expand=True)
    if es_admin:
        right_content.controls.append(
            ft.ElevatedButton("Config. Sensores/Actuadores", icon=ft.Icons.SETTINGS, bgcolor=COLORS['glass'],
                              color=COLORS['accent'], width=280, on_click=on_configuracion_click))
    right_content.controls.append(
        ft.ElevatedButton("Ver Logs / Histórico", icon=ft.Icons.HISTORY, bgcolor=COLORS['accent'], color=COLORS['bg'],
                          width=280, on_click=on_ver_historico_click))

    # --- NUEVO BOTÓN DE CONSUMO ---
    if on_ver_consumo_click:
        right_content.controls.append(
            ft.ElevatedButton("Consumo Eléctrico", icon=ft.Icons.BOLT, bgcolor="orange", color="black",
                              width=280, on_click=on_ver_consumo_click))
    # -------------------------------

    right_content.controls.append(ft.Divider(color=COLORS['muted']))

    switch_led = ft.Switch(value=False, disabled=(not puede_controlar),
                           on_change=lambda e: on_control_actuador_click(e, "leds", "on" if e.control.value else "off"))
    switch_fan = ft.Switch(value=False, disabled=(not puede_controlar),
                           on_change=lambda e: on_control_actuador_click(e, "fan", "on" if e.control.value else "off"))

    btn_auto_led = ft.Container(content=ft.Text("AUTO", size=10, weight="bold", color="white"), bgcolor=COLORS['muted'],
                                padding=5, border_radius=4,
                                on_click=lambda e: on_cambiar_modo_click(e, "leds") if puede_controlar else None,
                                tooltip="Click para alternar Auto/Manual")
    btn_auto_fan = ft.Container(content=ft.Text("AUTO", size=10, weight="bold", color="white"), bgcolor=COLORS['muted'],
                                padding=5, border_radius=4,
                                on_click=lambda e: on_cambiar_modo_click(e, "fan") if puede_controlar else None,
                                tooltip="Click para alternar Auto/Manual")

    right_content.controls.extend([
        ft.Text("Actuadores y Sistema", size=12, weight="bold", color=COLORS['text']),
        ft.Container(bgcolor=COLORS['glass'], padding=5, border_radius=5, content=ft.Row(
            [ft.Text(f"{DEVICE_ICONS['esp32']} ESP32 Controller", color=COLORS['text'], size=12),
             ft.Container(expand=True), ft.Text("ONLINE", color=COLORS['good'], size=10, weight="bold")])),
        ft.Container(bgcolor=COLORS['glass'], padding=5, border_radius=5, content=ft.Row(
            [ft.Text(f"{DEVICE_ICONS['motor']} Motor DC (Puertas)", color=COLORS['text'], size=12),
             ft.Container(expand=True), ft.Text("MANUAL", color=COLORS['accent'], size=10, weight="bold")])),
        ft.Container(bgcolor=COLORS['glass'], padding=5, border_radius=5, content=ft.Row(
            [ft.Text(f"{DEVICE_ICONS['leds']} Iluminación LED", color=COLORS['text'], size=12),
             ft.Container(expand=True), btn_auto_led, ft.Container(width=5), switch_led])),
        ft.Container(bgcolor=COLORS['glass'], padding=5, border_radius=5, content=ft.Row(
            [ft.Text(f"{DEVICE_ICONS['fan']} Ventilador 5V", color=COLORS['text'], size=12), ft.Container(expand=True),
             btn_auto_fan, ft.Container(width=5), switch_fan])),
        ft.Divider(height=10, color=COLORS['muted']),
        ft.Text("Monitor de Sensores (Tiempo Real)", size=12, weight="bold", color=COLORS['text'])
    ])

    lista_sensores_fijos = ["DHT11 - Temperatura", "DHT11 - Humedad", "LDR - Luz", "MQ-2 - Humo", "MQ-135 - Aire"]
    mapa_controles_sensores = {}
    columna_sensores_fijos = ft.Column(spacing=8)

    for nombre_sensor in lista_sensores_fijos:
        icono = "📝"
        if 'Temp' in nombre_sensor:
            icono = DEVICE_ICONS['dht11']
        elif 'Humedad' in nombre_sensor:
            icono = "💧"
        elif 'Luz' in nombre_sensor:
            icono = DEVICE_ICONS['ldr']
        elif 'Humo' in nombre_sensor:
            icono = DEVICE_ICONS['mq-2']
        elif 'Aire' in nombre_sensor:
            icono = DEVICE_ICONS['mq-135']

        txt_valor = ft.Text("Esperando...", size=13, weight="bold", color=COLORS['accent'])
        txt_hora = ft.Text("--:--:--", size=10, color=COLORS['muted'])
        mapa_controles_sensores[nombre_sensor] = (txt_valor, txt_hora)

        columna_sensores_fijos.controls.append(ft.Container(
            content=ft.Row([ft.Text(icono, size=18),
                            ft.Column([ft.Text(nombre_sensor, size=11, weight="bold", color=COLORS['text']), txt_hora],
                                      spacing=0, expand=True), txt_valor],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=COLORS['glass'], padding=10, border_radius=8,
            border=ft.border.only(left=ft.border.BorderSide(4, COLORS['accent']))
        ))

    right_content.controls.append(ft.Container(content=columna_sensores_fijos, expand=True))
    right_column = ft.Container(width=320, bgcolor=COLORS['card'], padding=14, expand=False, content=right_content,
                                border=ft.border.all(1, COLORS['glass']))

    # --- FUNCIÓN PÚBLICA DE ACTUALIZACIÓN (MVC STRICT) ---
    # Esta función NO llama al modelo. Recibe los datos ya procesados.
    def actualizar_datos_ui(datos_sensores_raw, estados_actuadores):
        if not left_column.page: return

        # 1. Actualizar Sensores
        try:
            ultimos = {l['sensor']: l for l in datos_sensores_raw} if datos_sensores_raw else {}
            for nombre, (ctrl_val, ctrl_hora) in mapa_controles_sensores.items():
                if nombre in ultimos:
                    d = ultimos[nombre]
                    if ctrl_val.value != str(d['valor']):
                        ctrl_val.value = str(d['valor'])
                        if ctrl_val.page: ctrl_val.update()

                    try:
                        hora_str = f"Actualizado: {d['timestamp'].split(' ')[1]}"
                        if ctrl_hora.value != hora_str:
                            ctrl_hora.value = hora_str
                            if ctrl_hora.page: ctrl_hora.update()
                    except:
                        pass

                    # Alertas
                    try:
                        val_num = float(str(d['valor']).split(' ')[0])
                        color_new = COLORS['text']
                        if "Humo" in nombre and val_num > 50:
                            color_new = COLORS['bad']
                        elif "Temperatura" in nombre and val_num > 30:
                            color_new = "orange"
                        if ctrl_val.color != color_new:
                            ctrl_val.color = color_new
                            if ctrl_val.page: ctrl_val.update()
                    except:
                        pass
        except Exception:
            pass

        # 2. Actualizar Actuadores
        try:
            # Puertas
            for pid, cnt in controles_puertas.items():
                st = estados_actuadores.get(pid, {}).get("estado", "cerrada")
                col = COLORS['door_open'] if st == "abierta" else COLORS['door_closed']
                if cnt.bgcolor != col:
                    cnt.bgcolor = col
                    if cnt.page: cnt.update()

            # LEDS
            d_led = estados_actuadores.get("leds", {})
            st_led = d_led.get("estado", "off")
            mode_led = d_led.get("mode", "manual")

            if switch_led.value != (st_led == "on"):
                switch_led.value = (st_led == "on")
                if switch_led.page: switch_led.update()

            c_mode_led = COLORS['good'] if mode_led == "auto" else COLORS['bad']
            if btn_auto_led.bgcolor != c_mode_led:
                btn_auto_led.bgcolor = c_mode_led
                if btn_auto_led.page: btn_auto_led.update()

            dis_led = (not puede_controlar) or (mode_led == "auto")
            if switch_led.disabled != dis_led:
                switch_led.disabled = dis_led
                if switch_led.page: switch_led.update()

            # FAN
            d_fan = estados_actuadores.get("fan", {})
            st_fan = d_fan.get("estado", "off")
            mode_fan = d_fan.get("mode", "manual")

            if switch_fan.value != (st_fan == "on"):
                switch_fan.value = (st_fan == "on")
                if switch_fan.page: switch_fan.update()

            c_mode_fan = COLORS['good'] if mode_fan == "auto" else COLORS['bad']
            if btn_auto_fan.bgcolor != c_mode_fan:
                btn_auto_fan.bgcolor = c_mode_fan
                if btn_auto_fan.page: btn_auto_fan.update()

            dis_fan = (not puede_controlar) or (mode_fan == "auto")
            if switch_fan.disabled != dis_fan:
                switch_fan.disabled = dis_fan
                if switch_fan.page: switch_fan.update()

            # Iconos
            c_fan = COLORS['accent'] if st_fan == "on" else COLORS['muted']
            if icon_fan_map.color != c_fan:
                icon_fan_map.color = c_fan
                if icon_fan_map.page: icon_fan_map.update()

            c_led = "yellow" if st_led == "on" else COLORS['muted']
            if icon_led_map.color != c_led:
                icon_led_map.color = c_led
                if icon_led_map.page: icon_led_map.update()

        except Exception:
            pass

    # Creamos la Vista y le adjuntamos el callback para el controlador
    view = ft.View("/dashboard", controls=[ft.Row([left_column, right_column], spacing=18, expand=True)],
                   bgcolor=COLORS['bg'], padding=18)
    view.data = {"update_callback": actualizar_datos_ui}

    return view