import flet as ft
from vista.temas import COLORS, DEVICE_ICONS
import vista.vista_gestion_presos
import vista.vista_gestion_usuarios


def crear_dashboard_view(
        page: ft.Page,
        rol_usuario: str,
        datos_actuadores: dict,
        datos_presos: list,
        datos_usuarios: list,
        datos_sensores: list,
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

    # --- TOPBAR (Botón Histórico quitado de aquí) ---
    title = ft.Text("Planta Comisaría - Panel Central", size=18, weight=ft.FontWeight.BOLD, color=COLORS['text'])
    legend = ft.Text("🟢 Abierta 🔴 Cerrada", size=10, color=COLORS['muted'])

    boton_camaras = ft.ElevatedButton(
        "Ver Cámaras",
        icon=ft.Icons.CAMERA_ALT,
        bgcolor=COLORS['glass'],
        color=COLORS['text'],
        on_click=on_ver_camaras_click
    )

    user_label = ft.Container(
        content=ft.Text(f"Usuario: {rol_usuario.upper()}", size=10, weight=ft.FontWeight.BOLD, color=COLORS['text']),
        bgcolor=COLORS['glass'],
        padding=10,
        border_radius=5
    )
    logout_btn = ft.ElevatedButton("Salir", bgcolor=COLORS['bg'], color=COLORS['bad'],
                                   on_click=on_logout_click)

    topbar = ft.Row([
        ft.Column([title, legend], spacing=2),
        ft.Container(expand=True),
        boton_camaras,
        ft.Container(width=10),
        user_label,
        logout_btn
    ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    # --- MAPA INTERACTIVO (Igual que antes) ---
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
            ft.Container(
                left=r["l"], top=r["t"], width=r["w"], height=r["h"],
                bgcolor=COLORS['room_bg'], border=ft.border.all(2, '#5a7a9e'),
                content=ft.Text(r["name"], color='#cfe7ff', size=14, weight="bold"),
                alignment=ft.alignment.center
            )
        )

    doors_config = [
        {"id": "door-1", "l": 320, "t": 60, "w": 20, "h": 40, "label": "P1"},
        {"id": "door-2", "l": 320, "t": 200, "w": 20, "h": 40, "label": "P2"},
        {"id": "door-3", "l": 150, "t": 140, "w": 40, "h": 20, "label": "P3"},
        {"id": "door-4", "l": 470, "t": 140, "w": 40, "h": 20, "label": "P4"},
    ]

    for d in doors_config:
        estado_actual = datos_actuadores.get(d["id"], {}).get("estado", "cerrada")
        color_puerta = COLORS['door_open'] if estado_actual == "abierta" else COLORS['door_closed']
        nuevo_estado = "cerrada" if estado_actual == "abierta" else "abierta"

        door_cnt = ft.Container(
            left=d["l"], top=d["t"], width=d["w"], height=d["h"],
            bgcolor=color_puerta,
            border=ft.border.all(1, "white"),
            tooltip=f"Puerta {d['label']} (Motor DC)",
            on_click=lambda e, did=d["id"], nes=nuevo_estado: on_control_actuador_click(e, did, nes),
            content=ft.Text(d["label"], size=8, color="white", weight="bold"),
            alignment=ft.alignment.center
        )
        map_controls.append(door_cnt)

    # Iconos mapa (Estáticos para ubicación)
    map_controls.append(ft.Container(left=580, top=30, width=30, height=30,
                                     content=ft.Icon(ft.Icons.VIDEOCAM, color="#fb7185", size=20), bgcolor="white",
                                     border_radius=15,
                                     tooltip="Camara OV2640", on_click=on_ver_camaras_click,
                                     alignment=ft.alignment.center))

    map_controls.append(
        ft.Container(left=150, top=200, content=ft.Text(DEVICE_ICONS['ldr'], size=20), tooltip="LDR (Luz)"))
    map_controls.append(
        ft.Container(left=325, top=100, content=ft.Text(DEVICE_ICONS['mq-2'], size=20), tooltip="MQ-2 (Humo)"))
    map_controls.append(
        ft.Container(left=400, top=80, content=ft.Text(DEVICE_ICONS['mq-135'], size=20), tooltip="MQ-135 (Aire)"))
    map_controls.append(ft.Container(left=350, top=180, content=ft.Text(DEVICE_ICONS['dht22'], size=16),
                                     tooltip="DHT22 (Temp Alta Precisión)"))

    map_stack = ft.Stack(controls=map_controls, width=680, height=320)

    map_card = ft.Container(
        content=ft.Column([
            ft.Text("Plano Interactivo", color=COLORS['text'], size=16),
            ft.Row([map_stack], alignment=ft.MainAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=COLORS['card'], border=ft.border.all(2, COLORS['glass']), expand=False, padding=10,
        alignment=ft.alignment.center
    )

    # --- BOTTOM ROW (GESTIÓN) ---
    vista_presos = vista.vista_gestion_presos.crear_vista_presos(
        lista_presos=datos_presos,
        on_abrir_crear_handler=on_abrir_crear_preso,
        on_abrir_editar_handler=on_abrir_editar_preso,
        on_refrescar_handler=on_refrescar_click,
        on_borrar_preso_handler=on_borrar_preso_click
    )

    vista_usuarios = vista.vista_gestion_usuarios.crear_vista_usuarios(
        rol_actual=rol_usuario,
        lista_usuarios=datos_usuarios,
        on_crear_usuario_handler=on_crear_usuario_click
    )

    bottom_row = ft.Container(
        height=450,
        content=ft.Row(
            controls=[ft.Container(content=vista_presos, expand=1), ft.Container(content=vista_usuarios, expand=1)],
            spacing=12, expand=True)
    )

    left_column = ft.Column(spacing=12, expand=True, scroll=ft.ScrollMode.AUTO, controls=[topbar, map_card, bottom_row])

    # --- PANEL DERECHO (MODIFICADO) ---
    right_content = ft.Column(spacing=12, expand=True)

    # 1. Botón Histórico (Movido aquí)
    boton_historico = ft.ElevatedButton(
        "Ver Logs / Histórico",
        icon=ft.Icons.HISTORY,
        bgcolor=COLORS['accent'],
        color=COLORS['bg'],
        width=280,
        on_click=on_ver_historico_click
    )

    right_content.controls.append(boton_historico)
    right_content.controls.append(ft.Divider(color=COLORS['muted']))
    right_content.controls.append(
        ft.Text("Actuadores y Sistema", size=12, weight=ft.FontWeight.BOLD, color=COLORS['text']))

    # Estado de Actuadores y Sistema
    led_estado = datos_actuadores.get("leds", {}).get("estado", "off")
    fan_estado = datos_actuadores.get("fan", {}).get("estado", "off")

    # Sistema (ESP32)
    right_content.controls.append(
        ft.Container(bgcolor=COLORS['glass'], padding=5, border_radius=5, content=ft.Row([
            ft.Text(f"{DEVICE_ICONS['esp32']} ESP32 Controller", color=COLORS['text'], size=12),
            ft.Container(expand=True),
            ft.Text("ONLINE", color=COLORS['good'], size=10, weight="bold")
        ]))
    )

    # Motor DC (Puertas)
    right_content.controls.append(
        ft.Container(bgcolor=COLORS['glass'], padding=5, border_radius=5, content=ft.Row([
            ft.Text(f"{DEVICE_ICONS['motor']} Motor DC (Puertas)", color=COLORS['text'], size=12),
            ft.Container(expand=True),
            ft.Text("AUTO", color=COLORS['accent'], size=10, weight="bold")
        ]))
    )

    # LEDs
    control_leds = ft.Container(
        bgcolor=COLORS['glass'], padding=5, border_radius=5,
        content=ft.Row([
            ft.Text(f"{DEVICE_ICONS['leds']} Iluminación LED", color=COLORS['text'], size=12),
            ft.Container(expand=True),
            ft.Switch(value=(led_estado == "on"),
                      on_change=lambda e, est=led_estado: on_control_actuador_click(e, "leds",
                                                                                    "off" if est == "on" else "on"),
                      disabled=(not puede_controlar))
        ])
    )

    # Ventilador 5V
    control_fan = ft.Container(
        bgcolor=COLORS['glass'], padding=5, border_radius=5,
        content=ft.Row([
            ft.Text(f"{DEVICE_ICONS['fan']} Ventilador 5V", color=COLORS['text'], size=12),
            ft.Container(expand=True),
            ft.Switch(value=(fan_estado == "on"),
                      on_change=lambda e, est=fan_estado: on_control_actuador_click(e, "fan",
                                                                                    "off" if est == "on" else "on"),
                      disabled=(not puede_controlar))
        ])
    )

    right_content.controls.extend([control_leds, control_fan, ft.Divider(height=10, color=COLORS['muted']),
                                   ft.Text("Últimas Lecturas (Sensores)", size=12, weight=ft.FontWeight.BOLD,
                                           color=COLORS['text'])])

    # LOG EN TIEMPO REAL CON ICONOS CORRECTOS
    log_list = ft.ListView(expand=True, spacing=5, padding=5)
    if datos_sensores:
        for log in reversed(datos_sensores[-15:]):
            s_name = log['sensor'].lower()

            # Asignar icono según nombre
            icono = "📝"
            if 'temp' in s_name or 'dht' in s_name:
                icono = DEVICE_ICONS['dht11']
            elif 'humedad' in s_name:
                icono = "💧"  # Icono extra para humedad
            elif 'luz' in s_name or 'ldr' in s_name:
                icono = DEVICE_ICONS['ldr']
            elif 'humo' in s_name or 'mq-2' in s_name:
                icono = DEVICE_ICONS['mq-2']
            elif 'aire' in s_name or 'mq-135' in s_name:
                icono = DEVICE_ICONS['mq-135']

            log_item = ft.Container(
                content=ft.Row([
                    ft.Text(f"{log['timestamp'].split(' ')[1]}", size=10, color=COLORS['muted']),
                    ft.Text(icono, size=14),
                    ft.Column([
                        ft.Text(f"{log['sensor']}", size=10, weight="bold", color=COLORS['accent']),
                        ft.Text(f"{log['valor']}", size=11, color=COLORS['text'])
                    ], spacing=0)
                ], spacing=10),
                bgcolor=COLORS['glass'], padding=5, border_radius=4
            )
            log_list.controls.append(log_item)
    else:
        log_list.controls.append(ft.Text("Esperando datos...", color=COLORS['muted'], size=10))

    right_content.controls.append(ft.Container(content=log_list, expand=True))

    right_column = ft.Container(width=320, bgcolor=COLORS['card'], padding=14, expand=False, content=right_content,
                                border=ft.border.all(1, COLORS['glass']))

    main_row = ft.Row([left_column, right_column], spacing=18, expand=True)

    return ft.View("/dashboard", controls=[main_row], bgcolor=COLORS['bg'], padding=18)