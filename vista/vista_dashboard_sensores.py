import flet as ft
from vista.temas import COLORS, DEVICE_ICONS


def crear_dashboard_view(
        page: ft.Page,
        rol_usuario: str,
        nombre_usuario: str,
        datos_actuadores_iniciales: dict,
        datos_sensores_iniciales: list,
        on_refrescar_click,
        on_control_actuador_click,
        on_ver_camaras_click,
        on_cambiar_modo_click
):
    puede_controlar = (rol_usuario != 'policia')

    brand_text = ft.Column([
        ft.Text("CENTRO DE CONTROL", size=22, weight=ft.FontWeight.W_900, color=COLORS['text'], font_family="Verdana"),
        ft.Text("MONITORIZACIÓN EN TIEMPO REAL", size=12, weight=ft.FontWeight.BOLD, color=COLORS['accent'])
    ], spacing=0)

    legend_content = ft.Row([
        ft.Text("🟢 Abierta 🔴 Cerrada", size=12, color=COLORS['muted']),
        ft.Container(width=10, height=15, border=ft.border.only(left=ft.border.BorderSide(1, COLORS['muted']))),
        ft.Icon(ft.Icons.PERSON, size=14, color=COLORS['accent']),
        ft.Text(f"{nombre_usuario} ({rol_usuario.upper()})", size=13, weight="bold", color=COLORS['text'])
    ], alignment="center")

    boton_camaras = ft.ElevatedButton("Ver Cámaras", icon=ft.Icons.CAMERA_ALT, bgcolor=COLORS['glass'],
                                      color=COLORS['text'], on_click=on_ver_camaras_click)

    topbar = ft.Container(
        content=ft.Row([
            brand_text, ft.Container(width=20),
            legend_content, ft.Container(expand=True),
            boton_camaras
        ], alignment="center", vertical_alignment="center"),
        padding=ft.padding.symmetric(horizontal=5, vertical=10)
    )

    rooms_config = [
        {"name": "Recepción", "l": 30, "t": 30, "w": 450, "h": 180},
        {"name": "Vigilancia", "l": 510, "t": 30, "w": 450, "h": 180},
        {"name": "Despacho", "l": 30, "t": 240, "w": 450, "h": 180},
        {"name": "C1", "l": 510, "t": 240, "w": 225, "h": 90},
        {"name": "C2", "l": 735, "t": 240, "w": 225, "h": 90},
        {"name": "C3", "l": 510, "t": 330, "w": 225, "h": 90},
        {"name": "C4", "l": 735, "t": 330, "w": 225, "h": 90},
    ]

    map_stack_controls = []
    for r in rooms_config:
        map_stack_controls.append(ft.Container(
            left=r["l"], top=r["t"], width=r["w"], height=r["h"],
            bgcolor=COLORS['room_bg'], border=ft.border.all(2, '#5a7a9e'),
            content=ft.Text(r["name"], color='#cfe7ff', size=16, weight="bold"),
            alignment=ft.alignment.center
        ))

    doors_config = [
        {"id": "door-1", "l": 480, "t": 90, "w": 30, "h": 60, "label": "P1"},
        {"id": "door-2", "l": 480, "t": 300, "w": 30, "h": 60, "label": "P2"},
        {"id": "door-3", "l": 225, "t": 210, "w": 60, "h": 30, "label": "P3"},
        {"id": "door-4", "l": 705, "t": 210, "w": 60, "h": 30, "label": "P4"},
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
            content=ft.Text(d["label"], size=10, color="white", weight="bold"),
            alignment=ft.alignment.center,
            animate=ft.Animation(300, "easeOut")
        )
        controles_puertas[pid] = cnt
        map_stack_controls.append(cnt)

    icon_fan_map = ft.Icon(DEVICE_ICONS['fan'], size=26, color=COLORS['muted'])
    icon_led_map = ft.Icon(DEVICE_ICONS['leds'], size=26, color=COLORS['muted'])

    map_stack_controls.extend([
        ft.Container(left=870, top=45, content=ft.Icon(ft.Icons.VIDEOCAM, color="#fb7185", size=24), bgcolor="white",
                     border_radius=15, on_click=on_ver_camaras_click),

        ft.Container(left=715, top=309, content=ft.Text(DEVICE_ICONS['ldr'], size=24), tooltip="LDR - Luz"),
        ft.Container(left=900, top=268, content=ft.Text(DEVICE_ICONS['mq-2'], size=24), tooltip="MQ-2 - Humo"),
        ft.Container(left=900, top=367, content=ft.Text("💧", size=24), tooltip="DHT11 - Humedad"),
        ft.Container(left=517, top=270, content=ft.Text(DEVICE_ICONS['dht11'], size=20), tooltip="DHT11 - Temperatura"),

        # --- ICONO DE CALIDAD DE AIRE RESTAURADO ---
        # left=715 (Alineado con el LDR de arriba)
        # top=367 (Alineado con la Humedad de la derecha)
        ft.Container(left=517, top=367, content=ft.Text("🌬️", size=24), tooltip="MQ-2 - Calidad Aire"),

        ft.Container(left=600, top=247, content=icon_fan_map, tooltip="Ventilación"),
        ft.Container(left=720, top=315, content=icon_led_map, tooltip="Iluminación Central"),
    ])

    map_card = ft.Container(content=ft.Column([
        ft.Text("Plano Interactivo de la Comisaría", color=COLORS['text'], size=18, weight="bold"),
        ft.Row([ft.Stack(controls=map_stack_controls, width=1000, height=450)], alignment="center", expand=True)
    ], alignment="center"), bgcolor=COLORS['card'], border=ft.border.all(2, COLORS['glass']), padding=15,
        alignment=ft.alignment.center, expand=True)

    left_column = ft.Column(spacing=15, expand=True, controls=[topbar, map_card])

    right_content = ft.Column(spacing=15, expand=True)

    switch_led = ft.Switch(value=False, disabled=(not puede_controlar),
                           on_change=lambda e: on_control_actuador_click(e, "leds", "on" if e.control.value else "off"))
    switch_fan = ft.Switch(value=False, disabled=(not puede_controlar),
                           on_change=lambda e: on_control_actuador_click(e, "fan", "on" if e.control.value else "off"))

    txt_auto_led = ft.Text("AUTO", size=10, weight="bold", color="white")
    btn_auto_led = ft.Container(content=txt_auto_led, bgcolor=COLORS['muted'], padding=5, border_radius=4,
                                on_click=lambda e: on_cambiar_modo_click(e, "leds") if puede_controlar else None,
                                tooltip="Alternar modo Auto/Manual")

    txt_auto_fan = ft.Text("AUTO", size=10, weight="bold", color="white")
    btn_auto_fan = ft.Container(content=txt_auto_fan, bgcolor=COLORS['muted'], padding=5, border_radius=4,
                                on_click=lambda e: on_cambiar_modo_click(e, "fan") if puede_controlar else None,
                                tooltip="Alternar modo Auto/Manual")

    txt_esp32_status = ft.Text("ESPERANDO", color=COLORS['muted'], size=11, weight="bold")

    right_content.controls.extend([
        ft.Text("Estado de Actuadores", size=16, weight="bold", color=COLORS['text']),
        ft.Container(bgcolor=COLORS['glass'], padding=8, border_radius=5, content=ft.Row(
            [ft.Text(f"{DEVICE_ICONS['esp32']} Controlador", color=COLORS['text'], size=13),
             ft.Container(expand=True), txt_esp32_status])),

        ft.Container(bgcolor=COLORS['glass'], padding=8, border_radius=5, content=ft.Row(
            [ft.Text(f"{DEVICE_ICONS['motor']} Motores Puerta", color=COLORS['text'], size=13),
             ft.Container(expand=True), ft.Text("MANUAL", color=COLORS['accent'], size=11, weight="bold")])),

        ft.Container(bgcolor=COLORS['glass'], padding=8, border_radius=5, content=ft.Row(
            [ft.Text(f"{DEVICE_ICONS['leds']} Iluminación", color=COLORS['text'], size=13),
             ft.Container(expand=True), btn_auto_led, ft.Container(width=5), switch_led])),

        ft.Container(bgcolor=COLORS['glass'], padding=8, border_radius=5, content=ft.Row(
            [ft.Text(f"{DEVICE_ICONS['fan']} Ventilación", color=COLORS['text'], size=13), ft.Container(expand=True),
             btn_auto_fan, ft.Container(width=5), switch_fan])),

        ft.Divider(height=10, color=COLORS['muted']),
        ft.Text("Monitoreo en Tiempo Real", size=16, weight="bold", color=COLORS['text'])
    ])

    lista_sensores_fijos = ["DHT11 - Temperatura", "DHT11 - Humedad", "LDR - Luz", "MQ-2 - Humo", "MQ-135 - Aire"]
    mapa_controles_sensores = {}
    columna_sensores_fijos = ft.Column(spacing=12)

    for nombre_sensor in lista_sensores_fijos:
        icono = "📝"
        label_mostrar = nombre_sensor

        if 'Temp' in nombre_sensor:
            icono = DEVICE_ICONS['dht11']
        elif 'Humedad' in nombre_sensor:
            icono = "💧"
        elif 'Luz' in nombre_sensor:
            icono = DEVICE_ICONS['ldr']
        elif 'Humo' in nombre_sensor:
            icono = DEVICE_ICONS['mq-2']
        elif 'Aire' in nombre_sensor:
            icono = "🌬️"
            label_mostrar = "MQ-2 - Calidad Aire"

        txt_valor = ft.Text("Esperando...", size=15, weight="bold", color=COLORS['accent'])
        txt_hora = ft.Text("--:--:--", size=11, color=COLORS['muted'])

        mapa_controles_sensores[nombre_sensor] = (txt_valor, txt_hora)

        columna_sensores_fijos.controls.append(ft.Container(
            content=ft.Row([ft.Text(icono, size=22),
                            ft.Column([ft.Text(label_mostrar, size=13, weight="bold", color=COLORS['text']), txt_hora],
                                      spacing=0, expand=True), txt_valor],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=COLORS['glass'], padding=12, border_radius=8,
            border=ft.border.only(left=ft.border.BorderSide(4, COLORS['accent']))
        ))

    right_content.controls.append(ft.Container(content=columna_sensores_fijos, expand=True))
    right_column = ft.Container(width=340, bgcolor=COLORS['card'], padding=18, expand=False, content=right_content,
                                border=ft.border.all(1, COLORS['glass']))

    def actualizar_datos_ui(datos_sensores_raw, estados_actuadores, esp32_online=True):
        if not left_column.page: return

        status_text = "ONLINE" if esp32_online else "OFFLINE"
        status_col = COLORS['good'] if esp32_online else COLORS['bad']
        if txt_esp32_status.value != status_text:
            txt_esp32_status.value = status_text
            txt_esp32_status.color = status_col
            try:
                txt_esp32_status.update()
            except:
                pass

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

        try:
            for pid, cnt in controles_puertas.items():
                st = estados_actuadores.get(pid, {}).get("estado", "cerrada")
                col = COLORS['door_open'] if st == "abierta" else COLORS['door_closed']
                if cnt.bgcolor != col:
                    cnt.bgcolor = col
                    if cnt.page: cnt.update()

            d_led = estados_actuadores.get("leds", {})
            st_led = d_led.get("estado", "off")
            mode_led = d_led.get("mode", "manual")

            if switch_led.value != (st_led == "on"):
                switch_led.value = (st_led == "on")
                if switch_led.page: switch_led.update()

            lbl_mode_led = "AUTO" if mode_led == "auto" else "MANUAL"
            if txt_auto_led.value != lbl_mode_led:
                txt_auto_led.value = lbl_mode_led
                if txt_auto_led.page: txt_auto_led.update()

            c_mode_led = COLORS['good'] if mode_led == "auto" else COLORS['accent']
            if btn_auto_led.bgcolor != c_mode_led:
                btn_auto_led.bgcolor = c_mode_led
                if btn_auto_led.page: btn_auto_led.update()

            dis_led = (not puede_controlar) or (mode_led == "auto")
            if switch_led.disabled != dis_led:
                switch_led.disabled = dis_led
                if switch_led.page: switch_led.update()

            d_fan = estados_actuadores.get("fan", {})
            st_fan = d_fan.get("estado", "off")
            mode_fan = d_fan.get("mode", "manual")

            if switch_fan.value != (st_fan == "on"):
                switch_fan.value = (st_fan == "on")
                if switch_fan.page: switch_fan.update()

            lbl_mode_fan = "AUTO" if mode_fan == "auto" else "MANUAL"
            if txt_auto_fan.value != lbl_mode_fan:
                txt_auto_fan.value = lbl_mode_fan
                if txt_auto_fan.page: txt_auto_fan.update()

            c_mode_fan = COLORS['good'] if mode_fan == "auto" else COLORS['accent']
            if btn_auto_fan.bgcolor != c_mode_fan:
                btn_auto_fan.bgcolor = c_mode_fan
                if btn_auto_fan.page: btn_auto_fan.update()

            dis_fan = (not puede_controlar) or (mode_fan == "auto")
            if switch_fan.disabled != dis_fan:
                switch_fan.disabled = dis_fan
                if switch_fan.page: switch_fan.update()

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

    main_container = ft.Container(
        content=ft.Row([left_column, right_column], spacing=18, expand=True),
        expand=True
    )
    main_container.data = {"update_callback": actualizar_datos_ui}

    return main_container