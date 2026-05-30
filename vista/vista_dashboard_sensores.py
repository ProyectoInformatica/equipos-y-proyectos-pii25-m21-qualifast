import flet as ft
import flet.canvas as cv
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
        ft.Text("PLANO GEOMÉTRICO MAQUETA", size=12, weight=ft.FontWeight.BOLD, color=COLORS['accent'])
    ], spacing=0)

    legend_content = ft.Row([
        ft.Text("🟢 Abierta 🔴 Cerrada", size=12, color=COLORS['muted']),
        ft.Container(width=10, height=15, border=ft.border.only(left=ft.border.BorderSide(1, COLORS['muted']))),
        ft.Icon(ft.Icons.PERSON, size=14, color=COLORS['accent']),
        ft.Text(f"{nombre_usuario} ({rol_usuario.upper()})", size=13, weight=ft.FontWeight.BOLD, color=COLORS['text'])
    ], alignment=ft.MainAxisAlignment.CENTER)

    boton_camaras = ft.ElevatedButton("Ver Cámaras", icon=ft.Icons.CAMERA_ALT, bgcolor=COLORS['glass'],
                                      color=COLORS['text'], on_click=on_ver_camaras_click)

    topbar = ft.Container(
        content=ft.Row([
            brand_text, ft.Container(width=20),
            legend_content, ft.Container(expand=True),
            boton_camaras
        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.padding.symmetric(horizontal=5, vertical=10)
    )

    # =========================================================================
    # DIBUJO VECTORIAL (Hexágono ampliado al máximo)
    # =========================================================================
    # Parámetros geométricos para lienzo de 900x550
    p_ext = [(295, 6), (605, 6), (760, 275), (605, 544), (295, 544), (140, 275)]
    p_int = [(390, 171), (510, 171), (570, 275), (510, 379), (390, 379), (330, 275)]

    fondo_hexagono = cv.Canvas(
        shapes=[
            # 1. Relleno oscuro de fondo
            cv.Path(
                elements=[
                    cv.Path.MoveTo(p_ext[0][0], p_ext[0][1]), cv.Path.LineTo(p_ext[1][0], p_ext[1][1]),
                    cv.Path.LineTo(p_ext[2][0], p_ext[2][1]), cv.Path.LineTo(p_ext[3][0], p_ext[3][1]),
                    cv.Path.LineTo(p_ext[4][0], p_ext[4][1]), cv.Path.LineTo(p_ext[5][0], p_ext[5][1]), cv.Path.Close(),
                ],
                paint=ft.Paint(color="#0f172a", style=ft.PaintingStyle.FILL)
            ),
            # 2. Hexágono exterior
            cv.Path(
                elements=[
                    cv.Path.MoveTo(p_ext[0][0], p_ext[0][1]), cv.Path.LineTo(p_ext[1][0], p_ext[1][1]),
                    cv.Path.LineTo(p_ext[2][0], p_ext[2][1]), cv.Path.LineTo(p_ext[3][0], p_ext[3][1]),
                    cv.Path.LineTo(p_ext[4][0], p_ext[4][1]), cv.Path.LineTo(p_ext[5][0], p_ext[5][1]), cv.Path.Close(),
                ],
                paint=ft.Paint(color=COLORS['accent'], style=ft.PaintingStyle.STROKE, stroke_width=4)
            ),
            # 3. Hexágono central (Vigilancia)
            cv.Path(
                elements=[
                    cv.Path.MoveTo(p_int[0][0], p_int[0][1]), cv.Path.LineTo(p_int[1][0], p_int[1][1]),
                    cv.Path.LineTo(p_int[2][0], p_int[2][1]), cv.Path.LineTo(p_int[3][0], p_int[3][1]),
                    cv.Path.LineTo(p_int[4][0], p_int[4][1]), cv.Path.LineTo(p_int[5][0], p_int[5][1]), cv.Path.Close(),
                ],
                paint=ft.Paint(color=COLORS['accent'], style=ft.PaintingStyle.STROKE, stroke_width=2)
            ),
            # 4. Líneas divisorias
            cv.Path(
                elements=[
                    # Separa Celda 1 de Recepción
                    cv.Path.MoveTo(p_int[0][0], p_int[0][1]), cv.Path.LineTo(p_ext[0][0], p_ext[0][1]),
                    # Separa Celda 2 de Celda 1
                    cv.Path.MoveTo(p_int[5][0], p_int[5][1]), cv.Path.LineTo(p_ext[5][0], p_ext[5][1]),
                    # Separa Celda 3 de Celda 2
                    cv.Path.MoveTo(p_int[4][0], p_int[4][1]), cv.Path.LineTo(p_ext[4][0], p_ext[4][1]),
                    # Separa Celda 4 de Celda 3
                    cv.Path.MoveTo(p_int[3][0], p_int[3][1]), cv.Path.LineTo(p_ext[3][0], p_ext[3][1]),
                    # Separa Recepción de Celda 4
                    cv.Path.MoveTo(p_int[2][0], p_int[2][1]), cv.Path.LineTo(p_ext[2][0], p_ext[2][1]),
                ],
                paint=ft.Paint(color=COLORS['glass'], style=ft.PaintingStyle.STROKE, stroke_width=2)
            )
        ],
        width=900, height=550, left=0, top=0
    )

    map_stack_controls = [fondo_hexagono]

    # =========================================================================
    # TEXTOS FLOTANTES (Reajustados a la nueva escala)
    # =========================================================================
    labels_config = [
        # Administración
        ft.Container(left=520, top=100, content=ft.Text("RECEPCIÓN", size=18, weight=ft.FontWeight.BOLD, color="#cfe7ff")),
        ft.Container(left=400, top=265, content=ft.Text("VIGILANCIA", size=16, weight=ft.FontWeight.BOLD, color="#cfe7ff")),

        # Celdas (Textos reajustados para quedar centrados en sus trapecios)
        ft.Container(left=250, top=165, content=ft.Text("CELDA 1", size=19, weight=ft.FontWeight.W_900, color="#ef4444")),
        ft.Container(left=250, top=365, content=ft.Text("CELDA 2", size=19, weight=ft.FontWeight.W_900, color="#ef4444")),
        ft.Container(left=410, top=460, content=ft.Text("CELDA 3", size=19, weight=ft.FontWeight.W_900, color="#ef4444")),
        ft.Container(left=575, top=365, content=ft.Text("CELDA 4", size=19, weight=ft.FontWeight.W_900, color="#ef4444")),
    ]
    map_stack_controls.extend(labels_config)

    # =========================================================================
    # COMPONENTES INTERACTIVOS
    # =========================================================================
    # Puertas en las líneas interiores correspondientes
    doors_config = [
        {"id": "door-1", "l": 345, "t": 208, "w": 30, "h": 30, "label": "P1"},
        {"id": "door-2", "l": 345, "t": 312, "w": 30, "h": 30, "label": "P2"},
        {"id": "door-3", "l": 435, "t": 364, "w": 30, "h": 30, "label": "P3"},
        {"id": "door-4", "l": 525, "t": 312, "w": 30, "h": 30, "label": "P4"},
    ]

    # CORRECCIÓN: los actuadores del plano usan ft.Text (emoji), NO ft.Icon,
    # porque DEVICE_ICONS contiene strings emoji, no constantes ft.Icons.*
    # Se guardan referencias directas a los ft.Text para poder cambiar su color después.
    txt_fan_map = ft.Text(DEVICE_ICONS['fan'], size=26)
    txt_led_map = ft.Text(DEVICE_ICONS['leds'], size=26)

    icons_config = [
        # 0: Cámara — SIN CAMBIOS
        ft.Container(left=495, top=156, content=ft.Icon(ft.Icons.VIDEOCAM, color="#fb7185", size=26), bgcolor="white",
                     border_radius=15, on_click=on_ver_camaras_click),

        # 1: 💧 Humedad → Más arriba y a la derecha (para asentarse en la línea de Celda 1)
        ft.Container(left=310, top=9, content=ft.Text("💧", size=22), tooltip="DHT11 - Humedad"),

        # 2: LDR Luz → Un pelín más arriba y a la derecha (sobre la línea inclinada)
        ft.Container(left=380, top=145, content=ft.Text(DEVICE_ICONS['ldr'], size=22), tooltip="LDR - Luz"),

        # 3: MQ-2 Humo → Más a la izquierda y un par de píxeles abajo (en el borde de Celda 4)
        ft.Container(left=720, top=240, content=ft.Text(DEVICE_ICONS['mq-2'], size=22), tooltip="MQ-2 - Humo"),

        # 4: DHT11 Temp → A la altura del fuego, más a la izquierda (justo arriba/derecha de la intersección central)
        ft.Container(left=570, top=240, content=ft.Text(DEVICE_ICONS['dht11'], size=18), tooltip="DHT11 - Temperatura"),

        # 5: 🌬️ Calidad Aire → Un poco más arriba y un píxel a la izquierda (en la línea de Recepción)
        ft.Container(left=585, top=9, content=ft.Text("🌬️", size=22), tooltip="MQ-2 - Calidad Aire"),

        # 6: Actuador Fan → Ajustado en el eje X para quedar perfectamente centrado bajo la bombilla
        ft.Container(left=435, top=292, content=txt_fan_map, tooltip="Ventilación"),

        # 7: LEDs — SIN CAMBIOS
        ft.Container(left=440, top=220, content=txt_led_map, tooltip="Iluminación Central"),
    ]
    # =========================================================================

    controles_puertas = {}
    for d in doors_config:
        pid = d["id"]
        estado = datos_actuadores_iniciales.get(pid, {}).get("estado", "cerrada")
        color = COLORS['door_open'] if estado == "abierta" else COLORS['door_closed']

        cnt = ft.Container(
            left=d["l"], top=d["t"], width=d["w"], height=d["h"],
            bgcolor=color, border=ft.border.all(1, "white"), border_radius=5,
            on_click=lambda e, p=pid: on_control_actuador_click(e, p, None),
            content=ft.Text(d["label"], size=10, color="white", weight=ft.FontWeight.BOLD),
            alignment=ft.alignment.center,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        )
        controles_puertas[pid] = cnt
        map_stack_controls.append(cnt)

    # Referencias a los controles emoji del plano (ya son ft.Text, no ft.Icon)
    icon_fan_map = txt_fan_map
    icon_led_map = txt_led_map
    map_stack_controls.extend(icons_config)

    map_card = ft.Container(content=ft.Column([
        # Título corregido según indicaciones
        ft.Text("Plano Interactivo", color=COLORS['text'], size=18, weight=ft.FontWeight.BOLD),
        ft.Row([ft.Stack(controls=map_stack_controls, width=900, height=550)], alignment=ft.MainAxisAlignment.CENTER, expand=True)
    ], alignment=ft.MainAxisAlignment.CENTER), bgcolor=COLORS['card'], border=ft.border.all(2, COLORS['glass']), padding=15,
        alignment=ft.alignment.center, expand=True)

    left_column = ft.Column(spacing=15, expand=True, controls=[topbar, map_card])

    right_content = ft.Column(spacing=15, expand=True)

    switch_led = ft.Switch(value=False, disabled=(not puede_controlar),
                           on_change=lambda e: on_control_actuador_click(e, "leds", "on" if e.control.value else "off"))
    switch_fan = ft.Switch(value=False, disabled=(not puede_controlar),
                           on_change=lambda e: on_control_actuador_click(e, "fan", "on" if e.control.value else "off"))

    txt_auto_led = ft.Text("AUTO", size=10, weight=ft.FontWeight.BOLD, color="white")
    btn_auto_led = ft.Container(content=txt_auto_led, bgcolor=COLORS['muted'], padding=5, border_radius=4,
                                on_click=lambda e: on_cambiar_modo_click(e, "leds") if puede_controlar else None,
                                tooltip="Alternar modo Auto/Manual")

    txt_auto_fan = ft.Text("AUTO", size=10, weight=ft.FontWeight.BOLD, color="white")
    btn_auto_fan = ft.Container(content=txt_auto_fan, bgcolor=COLORS['muted'], padding=5, border_radius=4,
                                on_click=lambda e: on_cambiar_modo_click(e, "fan") if puede_controlar else None,
                                tooltip="Alternar modo Auto/Manual")

    txt_esp32_status = ft.Text("ESPERANDO", color=COLORS['muted'], size=11, weight=ft.FontWeight.BOLD)

    right_content.controls.extend([
        ft.Text("Estado de Actuadores", size=16, weight=ft.FontWeight.BOLD, color=COLORS['text']),

        ft.Container(bgcolor=COLORS['glass'], padding=8, border_radius=5, content=ft.Row(
            [ft.Text(f"{DEVICE_ICONS['esp32']} Controlador", color=COLORS['text'], size=13),
             ft.Container(expand=True), txt_esp32_status])),

        ft.Container(bgcolor=COLORS['glass'], padding=8, border_radius=5, content=ft.Row(
            [ft.Text(f"{DEVICE_ICONS['leds']} Iluminación", color=COLORS['text'], size=13),
             ft.Container(expand=True), btn_auto_led, ft.Container(width=5), switch_led])),

        ft.Container(bgcolor=COLORS['glass'], padding=8, border_radius=5, content=ft.Row(
            [ft.Text(f"{DEVICE_ICONS['fan']} Ventilación", color=COLORS['text'], size=13), ft.Container(expand=True),
             btn_auto_fan, ft.Container(width=5), switch_fan])),

        ft.Divider(height=10, color=COLORS['muted']),
        ft.Text("Monitoreo en Tiempo Real", size=16, weight=ft.FontWeight.BOLD, color=COLORS['text'])
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

        txt_valor = ft.Text("Esperando...", size=15, weight=ft.FontWeight.BOLD, color=COLORS['accent'])
        txt_hora = ft.Text("--:--:--", size=11, color=COLORS['muted'])

        mapa_controles_sensores[nombre_sensor] = (txt_valor, txt_hora)

        columna_sensores_fijos.controls.append(ft.Container(
            content=ft.Row([ft.Text(icono, size=22),
                            ft.Column([ft.Text(label_mostrar, size=13, weight=ft.FontWeight.BOLD, color=COLORS['text']), txt_hora],
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
            st_led, mode_led = d_led.get("estado", "off"), d_led.get("mode", "manual")

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
            st_fan, mode_fan = d_fan.get("estado", "off"), d_fan.get("mode", "manual")

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

            # CORRECCIÓN: icon_fan_map y icon_led_map son ft.Text (emoji),
            # no tienen atributo .color — se actualiza el valor del emoji si se quiere
            # indicar estado activo/inactivo se puede cambiar opacity del Container padre,
            # pero por ahora simplemente se deja sin cambio de color (no aplica a ft.Text).
            # Si se desea indicar estado, se puede hacer así:
            c_fan_opacity = 1.0 if st_fan == "on" else 0.4
            icons_config[6].opacity = c_fan_opacity
            if icons_config[6].page:
                icons_config[6].update()

            c_led_opacity = 1.0 if st_led == "on" else 0.4
            icons_config[7].opacity = c_led_opacity
            if icons_config[7].page:
                icons_config[7].update()

        except Exception:
            pass

    main_container = ft.Container(content=ft.Row([left_column, right_column], spacing=18, expand=True), expand=True)
    main_container.data = {"update_callback": actualizar_datos_ui}

    return main_container