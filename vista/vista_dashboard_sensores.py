import flet as ft

import vista.vista_gestion_presos
import vista.vista_gestion_usuarios
from vista.temas import COLORS, DEVICE_ICONS # Importamos los temas

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
    on_crear_preso_click,
    on_crear_usuario_click,
    on_ver_camara_click
):
    """
    Dashboard Ajustado:
    - Panel derecho: 460px (más ancho)
    - Mapa: 340px altura (más pequeño)
    - Tablas abajo: expand=True (más largas)
    """

    puede_controlar = (rol_usuario != 'policia')

    # --- TOPBAR ---
    title = ft.Text("Planta Comisaría", size=18, weight=ft.FontWeight.BOLD, color=COLORS['text'])
    legend = ft.Text("🟢 Puerta abierta 🔴 Puerta cerrada", size=10, color=COLORS['muted'])

    boton_camaras = ft.ElevatedButton(
        "Ver Cámaras",
        icon=ft.Icons.VIDEOCAM,
        bgcolor=COLORS['glass'],
        color=COLORS['text'],
        on_click=on_ver_camaras_click
    )

    user_label = ft.Container(
        content=ft.Text(f"Usuario: {rol_usuario.upper()}", size=10, weight=ft.FontWeight.BOLD, color=COLORS['text']),
        bgcolor=COLORS['glass'], padding=10, border_radius=5
    )
    logout_btn = ft.ElevatedButton("Cerrar sesión", bgcolor=COLORS['bg'], color=COLORS['accent'], on_click=on_logout_click)
    right_side = ft.Row([user_label, logout_btn])

    topbar = ft.Row([left_side, ft.Container(expand=True), right_side])

    # --- MAPA INTERACTIVO ---
    # Altura del lienzo reducida para hacer el mapa más compacto
    map_stack = ft.Stack(width=800, height=280)

    rooms = [
        {"name": "Recepción", "l": 20, "t": 20, "w": 350, "h": 110},
        {"name": "Vigilancia", "l": 390, "t": 20, "w": 350, "h": 110},
        {"name": "Despacho", "l": 20, "t": 150, "w": 350, "h": 110},
        {"name": "Celdas", "l": 390, "t": 150, "w": 350, "h": 110},
    ]
    for r in rooms:
        map_stack.controls.append(ft.Container(
            left=r["l"], top=r["t"], width=r["w"], height=r["h"],
            bgcolor=COLORS['room_bg'], border=ft.border.all(2, '#5a7a9e'),
            content=ft.Text(r["name"], color='#cfe7ff', size=16, weight="bold"),
            alignment=ft.alignment.center
        ))

    doors = [
        {"id": "door-1", "l": 370, "t": 50},
        {"id": "door-2", "l": 370, "t": 20},
        {"id": "door-3", "l": 370, "t": 180},
        {"id": "door-4", "l": 370, "t": 220}
    ]
    for d in doors:
        est = datos_actuadores.get(d["id"], {}).get("estado", "cerrada")
        col = COLORS['door_open'] if est == "abierta" else COLORS['door_closed']
        map_stack.controls.append(ft.Container(
            left=d["l"], top=d["t"], width=40, height=20, bgcolor=col, border=ft.border.all(1, "white"),
            on_click=lambda e, did=d["id"], s=est: on_control_actuador_click(e, did, "cerrada" if s == "abierta" else "abierta"),
            disabled=not puede_controlar, tooltip=f"Puerta {d['id']}"
        ))

    map_stack.controls.append(ft.Container(
        left=700, top=30, width=30, height=30,
        content=ft.Icon(ft.Icons.VIDEOCAM, color="red", size=20),
        bgcolor="white", border_radius=15,
        on_click=on_ver_camaras_click
    ))

    # Contenedor del Mapa
    map_card = ft.Container(
        content=ft.Column([
            ft.Text("Mapa de la comisaría", color=COLORS['text'], size=16),
            ft.Row([map_stack], scroll=ft.ScrollMode.AUTO, alignment=ft.MainAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=COLORS['card'],
        border=ft.border.all(2, COLORS['glass']),
        height=340, # ALTURA FIJA REDUCIDA (Da más espacio abajo)
        padding=10,
        alignment=ft.alignment.center
    )

    # --- BOTTOM ROW (Tablas) ---
    bottom_row = ft.Row(spacing=12, expand=True) # expand=True para que sean LARGAS

    bottom_row.controls.append(
        vista.vista_gestion_presos.crear_vista_presos(
            lista_presos=datos_presos,
            on_crear_preso_handler=on_crear_preso_click,
            on_refrescar_handler=on_refrescar_click
        )
    )

    if rol_usuario == "comisario":
        bottom_row.controls.append(
            vista.vista_gestion_usuarios.crear_vista_usuarios(
                rol_actual=rol_usuario,
                lista_usuarios=datos_usuarios,
                on_crear_usuario_handler=on_crear_usuario_click
            )
        )

    left_column = ft.Column(
        spacing=12, 
        expand=True,
        controls=[
            topbar,
            map_card,
            bottom_row
        ]
    )

    # --- PANEL DERECHO (MÁS ANCHO) ---
    right_content = ft.Column(spacing=12, expand=True)
    right_content.controls.append(ft.Text("Panel de Control y Sensores", size=12, weight=ft.FontWeight.BOLD, color=COLORS['text']))

    led_estado = datos_actuadores.get("leds", {}).get("estado", "off")
    fan_estado = datos_actuadores.get("fan", {}).get("estado", "off")
    
    control_leds = ft.Container(
        bgcolor=COLORS['glass'], padding=10, border_radius=5,
        content=ft.Row([
            ft.Text(f"{DEVICE_ICONS['leds']} Luces Generales", color=COLORS['text']),
            ft.Container(expand=True),
            ft.Switch(value=(led_estado == "on"), on_change=lambda e, est=led_estado: on_control_actuador_click(e, "leds", "off" if est == "on" else "on"), disabled=(not puede_controlar))
        ])
    )
    
    control_fan = ft.Container(
        bgcolor=COLORS['glass'], padding=10, border_radius=5,
        content=ft.Row([
            ft.Text(f"{DEVICE_ICONS['fan']} Ventilación", color=COLORS['text']),
            ft.Container(expand=True),
            ft.Switch(value=(fan_estado == "on"), on_change=lambda e, est=fan_estado: on_control_actuador_click(e, "fan", "off" if est == "on" else "on"), disabled=(not puede_controlar))
        ])
    )
    
    right_column.content.controls.append(control_leds)
    right_column.content.controls.append(control_fan)
    right_column.content.controls.append(ft.Divider(height=10))

    right_content.controls.append(control_leds)
    right_content.controls.append(control_fan)
    right_content.controls.append(ft.Divider(height=10, color=COLORS['muted']))
    right_content.controls.append(ft.Text("Log de Sensores (Últimos registros)", size=10, color=COLORS['muted']))

    log_list = ft.ListView(expand=True, spacing=5, padding=5)
    if not datos_sensores:
        log_list.controls.append(ft.Text("No hay datos de sensores.", color=COLORS['muted']))
    else:
        for log in reversed(datos_sensores[-15:]):
            icono = DEVICE_ICONS.get(log['sensor'].lower().replace("-", "") if log['sensor'] != 'DHT11' else 'dht', "📝")
            log_item = ft.Container(
                content=ft.Row([
                    ft.Text(f"{log.get('timestamp','').split(' ')[-1]}", size=9, color=COLORS['muted']),
                    ft.Text(icono, size=12),
                    ft.Text(f"{log['sensor']}:", size=10, weight=ft.FontWeight.BOLD, color=COLORS['accent']),
                    ft.Text(f"{log['valor']}", size=10, color=COLORS['text']),
                ], spacing=5),
                bgcolor=COLORS['glass'], padding=5, border_radius=4
            )
            
    right_column.content.controls.append(ft.Container(content=log_list, expand=True))

    right_content.controls.append(ft.Container(content=log_list, expand=True))

    right_column = ft.Container(
        width=460,  # AUMENTADO EL ANCHO (Antes 420)
        bgcolor=COLORS['card'],
        padding=14,
        expand=False,
        content=right_content,
        border=ft.border.all(1, COLORS['glass'])
    )

    main_row = ft.Row([left_column, right_column], spacing=18, expand=True)

    return ft.View(
        "/dashboard",
        controls=[
            main_row
        ],
        bgcolor=COLORS['bg'],
        padding=18
    )