import flet as ft
import threading
import time
from vista.temas import COLORS, DEVICE_ICONS
import vista.vista_gestion_presos
import vista.vista_gestion_usuarios
import modelo.manejador_datos as modelo


def crear_dashboard_view(
        page: ft.Page,
        rol_usuario: str,
        datos_actuadores: dict,
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
        on_ver_historico_click
):
    puede_controlar = (rol_usuario != 'policia')

    # --- TOPBAR CON LOGO Y BRANDING ---
    # Asegúrate de que 'logo.png' existe en la carpeta assets, si no, Flet pondrá un icono de error (roto), pero funcionará.
    logo_img = ft.Image(src="logo.png", height=40, fit=ft.ImageFit.CONTAIN)

    # Texto con estilo "Qualifast"
    brand_text = ft.Column([
        ft.Text("QUALIFAST BUILDINGS", size=16, weight=ft.FontWeight.W_900, color=COLORS['text'],
                font_family="Verdana"),
        # CORRECCIÓN: Se ha eliminado 'letter_spacing=2' para evitar el error
        ft.Text("PLANTA COMISARÍA", size=10, weight=ft.FontWeight.BOLD, color=COLORS['accent'])
    ], spacing=0)

    legend = ft.Text("🟢 Abierta 🔴 Cerrada", size=10, color=COLORS['muted'])

    boton_camaras = ft.ElevatedButton("Ver Cámaras", icon=ft.Icons.CAMERA_ALT, bgcolor=COLORS['glass'],
                                      color=COLORS['text'], on_click=on_ver_camaras_click)
    user_label = ft.Container(
        content=ft.Text(f"Usuario: {rol_usuario.upper()}", size=10, weight="bold", color=COLORS['text']),
        bgcolor=COLORS['glass'], padding=10, border_radius=5)
    logout_btn = ft.ElevatedButton("Salir", bgcolor=COLORS['bg'], color=COLORS['bad'], on_click=on_logout_click)

    # Layout del Header
    topbar = ft.Container(
        content=ft.Row([
            logo_img,
            ft.Container(width=10),
            brand_text,
            ft.Container(width=20),
            legend,
            ft.Container(expand=True),
            boton_camaras,
            ft.Container(width=10),
            user_label,
            logout_btn
        ], alignment="center", vertical_alignment="center"),
        padding=ft.padding.symmetric(horizontal=5, vertical=5)
    )

    # --- MAPA INTERACTIVO (Sin Cambios) ---
    rooms_config = [
        {"name": "Recepción", "l": 20, "t": 20, "w": 300, "h": 120},
        {"name": "Vigilancia", "l": 340, "t": 20, "w": 300, "h": 120},
        {"name": "Despacho", "l": 20, "t": 160, "w": 300, "h": 120},
        {"name": "C1", "l": 340, "t": 160, "w": 150, "h": 60},
        {"name": "C2", "l": 490, "t": 160, "w": 150, "h": 60},
        {"name": "C3", "l": 340, "t": 220, "w": 150, "h": 60},
        {"name": "C4", "l": 490, "t": 220, "w": 150, "h": 60},
    ]

    map_controls = []
    for r in rooms_config:
        map_controls.append(
            ft.Container(left=r["l"], top=r["t"], width=r["w"], height=r["h"], bgcolor=COLORS['room_bg'],
                         border=ft.border.all(2, '#5a7a9e'),
                         content=ft.Text(r["name"], color='#cfe7ff', size=14, weight="bold"),
                         alignment=ft.alignment.center))

    doors_config = [
        {"id": "door-1", "l": 320, "t": 60, "w": 20, "h": 40, "label": "P1"},
        {"id": "door-2", "l": 320, "t": 200, "w": 20, "h": 40, "label": "P2"},
        {"id": "door-3", "l": 150, "t": 140, "w": 40, "h": 20, "label": "P3"},
        {"id": "door-4", "l": 470, "t": 140, "w": 40, "h": 20, "label": "P4"},
    ]

    for d in doors_config:
        pid = d["id"]
        estado_actual = datos_actuadores.get(pid, {}).get("estado", "cerrada")
        color_puerta = COLORS['door_open'] if estado_actual == "abierta" else COLORS['door_closed']

        door_cnt = ft.Container(
            left=d["l"], top=d["t"], width=d["w"], height=d["h"],
            bgcolor=color_puerta, border=ft.border.all(1, "white"),
            tooltip=f"Puerta {d['label']}",
            on_click=lambda e, p=pid: on_control_actuador_click(e, p, None),
            content=ft.Text(d["label"], size=8, color="white", weight="bold"),
            alignment=ft.alignment.center,
            key=f"{pid}_{estado_actual}"
        )
        map_controls.append(door_cnt)

    map_controls.append(ft.Container(left=580, top=30, width=30, height=30,
                                     content=ft.Icon(ft.Icons.VIDEOCAM, color="#fb7185", size=20), bgcolor="white",
                                     border_radius=15, on_click=on_ver_camaras_click, alignment=ft.alignment.center))
    map_controls.append(ft.Container(left=150, top=200, content=ft.Text(DEVICE_ICONS['ldr'], size=20), tooltip="LDR"))
    map_controls.append(ft.Container(left=325, top=100, content=ft.Text(DEVICE_ICONS['mq-2'], size=20), tooltip="MQ-2"))
    map_controls.append(
        ft.Container(left=400, top=80, content=ft.Text(DEVICE_ICONS['mq-135'], size=20), tooltip="MQ-135"))
    map_controls.append(
        ft.Container(left=350, top=180, content=ft.Text(DEVICE_ICONS['dht22'], size=16), tooltip="DHT22"))

    map_card = ft.Container(content=ft.Column([ft.Text("Plano Interactivo", color=COLORS['text'], size=16),
                                               ft.Row([ft.Stack(controls=map_controls, width=680, height=320)],
                                                      alignment="center")], alignment="center"), bgcolor=COLORS['card'],
                            border=ft.border.all(2, COLORS['glass']), padding=10, alignment=ft.alignment.center)

    # --- BOTTOM ROW (Presos/Usuarios) ---
    vista_presos = vista.vista_gestion_presos.crear_vista_presos(datos_presos, on_abrir_crear_preso,
                                                                 on_abrir_editar_preso, on_refrescar_click,
                                                                 on_borrar_preso_click)
    vista_usuarios = vista.vista_gestion_usuarios.crear_vista_usuarios(rol_usuario, datos_usuarios,
                                                                       on_crear_usuario_click)
    bottom_row = ft.Container(height=450, content=ft.Row(
        [ft.Container(content=vista_presos, expand=1), ft.Container(content=vista_usuarios, expand=1)], spacing=12,
        expand=True))
    left_column = ft.Column(spacing=12, expand=True, scroll=ft.ScrollMode.AUTO, controls=[topbar, map_card, bottom_row])

    # --- PANEL DERECHO (Control y Logs) ---
    right_content = ft.Column(spacing=12, expand=True)
    right_content.controls.append(
        ft.ElevatedButton("Ver Logs / Histórico", icon=ft.Icons.HISTORY, bgcolor=COLORS['accent'], color=COLORS['bg'],
                          width=280, on_click=on_ver_historico_click))
    right_content.controls.append(ft.Divider(color=COLORS['muted']))
    right_content.controls.append(ft.Text("Actuadores y Sistema", size=12, weight="bold", color=COLORS['text']))

    led_estado = datos_actuadores.get("leds", {}).get("estado", "off")
    fan_estado = datos_actuadores.get("fan", {}).get("estado", "off")

    right_content.controls.append(ft.Container(bgcolor=COLORS['glass'], padding=5, border_radius=5, content=ft.Row(
        [ft.Text(f"{DEVICE_ICONS['esp32']} ESP32 Controller", color=COLORS['text'], size=12), ft.Container(expand=True),
         ft.Text("ONLINE", color=COLORS['good'], size=10, weight="bold")])))
    right_content.controls.append(ft.Container(bgcolor=COLORS['glass'], padding=5, border_radius=5, content=ft.Row(
        [ft.Text(f"{DEVICE_ICONS['motor']} Motor DC (Puertas)", color=COLORS['text'], size=12),
         ft.Container(expand=True), ft.Text("AUTO", color=COLORS['accent'], size=10, weight="bold")])))

    right_content.controls.append(ft.Container(bgcolor=COLORS['glass'], padding=5, border_radius=5, content=ft.Row([
        ft.Text(f"{DEVICE_ICONS['leds']} Iluminación LED", color=COLORS['text'], size=12), ft.Container(expand=True),
        ft.Switch(value=(led_estado == "on"),
                  on_change=lambda e: on_control_actuador_click(e, "leds", "off" if led_estado == "on" else "on"),
                  disabled=(not puede_controlar))
    ])))
    right_content.controls.append(ft.Container(bgcolor=COLORS['glass'], padding=5, border_radius=5, content=ft.Row([
        ft.Text(f"{DEVICE_ICONS['fan']} Ventilador 5V", color=COLORS['text'], size=12), ft.Container(expand=True),
        ft.Switch(value=(fan_estado == "on"),
                  on_change=lambda e: on_control_actuador_click(e, "fan", "off" if fan_estado == "on" else "on"),
                  disabled=(not puede_controlar))
    ])))

    right_content.controls.extend([ft.Divider(height=10, color=COLORS['muted']),
                                   ft.Text("Monitor de Sensores (Tiempo Real)", size=12, weight="bold",
                                           color=COLORS['text'])])

    # --- NUEVA LÓGICA DE LOGS (ESTÁTICA) ---
    lista_sensores_fijos = [
        "DHT11 - Temperatura",
        "DHT11 - Humedad",
        "LDR - Luz",
        "MQ-2 - Humo",
        "MQ-135 - Aire"
    ]

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

        fila = ft.Container(
            content=ft.Row([
                ft.Text(icono, size=18),
                ft.Column([
                    ft.Text(nombre_sensor, size=11, weight="bold", color=COLORS['text']),
                    txt_hora
                ], spacing=0, expand=True),
                txt_valor
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=COLORS['glass'], padding=10, border_radius=8,
            border=ft.border.only(left=ft.border.BorderSide(4, COLORS['accent']))
        )
        columna_sensores_fijos.controls.append(fila)

    def renderizar_logs(datos):
        ultimos_valores = {}
        if datos:
            for log in datos:
                ultimos_valores[log['sensor']] = log

        for nombre_sensor, (ctrl_val, ctrl_hora) in mapa_controles_sensores.items():
            if nombre_sensor in ultimos_valores:
                dato = ultimos_valores[nombre_sensor]
                hora_str = dato['timestamp'].split(' ')[1]

                ctrl_val.value = dato['valor']
                ctrl_hora.value = f"Actualizado: {hora_str}"

                ctrl_val.color = COLORS['text']
                try:
                    # Ejemplo simple de alerta visual si el humo es alto
                    if "Humo" in nombre_sensor and float(str(dato['valor']).split(' ')[0]) > 50:
                        ctrl_val.color = COLORS['bad']
                except:
                    pass

        if columna_sensores_fijos.page:
            columna_sensores_fijos.update()

    renderizar_logs(datos_sensores_iniciales)

    def loop_refresh():
        while True:
            try:
                if not page.views or page.route != "/dashboard":
                    break
                nuevos_datos = modelo.get_log_sensores_filtrado(horas=24)
                renderizar_logs(nuevos_datos)
                time.sleep(2)
            except:
                break

    threading.Thread(target=loop_refresh, daemon=True).start()

    right_content.controls.append(ft.Container(content=columna_sensores_fijos, expand=True))
    right_column = ft.Container(width=320, bgcolor=COLORS['card'], padding=14, expand=False, content=right_content,
                                border=ft.border.all(1, COLORS['glass']))

    return ft.View("/dashboard", controls=[ft.Row([left_column, right_column], spacing=18, expand=True)],
                   bgcolor=COLORS['bg'], padding=18)