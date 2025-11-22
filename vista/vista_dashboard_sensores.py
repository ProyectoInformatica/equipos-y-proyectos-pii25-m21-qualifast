import flet as ft
import vista.vista_gestion_presos
import vista.vista_gestion_usuarios
from vista.temas import COLORS, DEVICE_ICONS


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
        on_borrar_preso_click  # <--- Nuevo parámetro
):
    """
    Crea la vista principal del Dashboard.
    """
    # --- PERMISOS ---
    puede_controlar = (rol_usuario != 'policia')

    # --- TOPBAR ---
    title = ft.Text("Planta Comisaría", size=18, weight=ft.FontWeight.BOLD, color=COLORS['text'])
    legend = ft.Text("🟢 Puerta abierta 🔴 Puerta cerrada", size=10, color=COLORS['muted'])
    left_side = ft.Row([title, legend])

    user_label = ft.Container(
        content=ft.Text(f"Usuario: {rol_usuario.upper()}", size=10, weight=ft.FontWeight.BOLD, color=COLORS['text']),
        bgcolor=COLORS['glass'],
        padding=10,
        border_radius=5
    )
    logout_btn = ft.ElevatedButton("Cerrar sesión", bgcolor=COLORS['bg'], color=COLORS['accent'],
                                   on_click=on_logout_click)
    right_side = ft.Row([user_label, logout_btn])

    topbar = ft.Row([left_side, ft.Container(expand=True), right_side])

    # --- MAPA ---
    map_card = ft.Container(bgcolor=COLORS['card'], border=ft.border.all(2, COLORS['glass']), expand=True, padding=14)
    map_stack = ft.Stack(expand=True)
    map_content = ft.Container(width=1000, height=700)
    inner_stack = ft.Stack(expand=True)

    # Habitaciones
    rooms = [
        {"name": "Recepción", "left": 40, "top": 40, "width": 420, "height": 300},
        {"name": "Sala de Vigilancia", "left": 520, "top": 40, "width": 420, "height": 300},
        {"name": "Despacho", "left": 40, "top": 380, "width": 420, "height": 260},
        {"name": "Celdas", "left": 520, "top": 380, "width": 420, "height": 260},
    ]
    for room in rooms:
        inner_stack.controls.append(ft.Container(
            left=room["left"], top=room["top"], width=room["width"], height=room["height"],
            bgcolor=COLORS['room_bg'], border=ft.border.all(2, '#5a7a9e'),
            content=ft.Container(
                content=ft.Text(room["name"], color='#cfe7ff', size=16, text_align=ft.TextAlign.CENTER),
                alignment=ft.alignment.top_center, padding=ft.padding.only(top=20)
            )
        ))

    # Puertas
    doors_config = [
        {"id": "door-1", "left": 460, "top": 160, "width": 40, "height": 20},
        {"id": "door-2", "left": 460, "top": 100, "width": 40, "height": 20},
        {"id": "door-3", "left": 460, "top": 420, "width": 40, "height": 20},
        {"id": "door-4", "left": 460, "top": 480, "width": 40, "height": 20},
    ]
    for door in doors_config:
        door_id = door["id"]
        estado_actual = datos_actuadores.get(door_id, {}).get("estado", "cerrada")
        color_actual = COLORS['door_open'] if estado_actual == "abierta" else COLORS['door_closed']

        door_container = ft.Container(
            left=door["left"], top=door["top"], width=door["width"], height=door["height"],
            bgcolor=color_actual, border=ft.border.all(2, 'white'),
            on_click=lambda e, d_id=door_id, est=estado_actual: on_control_actuador_click(
                e, d_id, "cerrada" if est == "abierta" else "abierta"
            ),
            disabled=(not puede_controlar)
        )
        inner_stack.controls.append(door_container)

        label_container = ft.Container(
            left=door["left"], top=door["top"] - 20, width=door["width"], height=20,
            content=ft.Text(datos_actuadores.get(door_id, {}).get("label", "??"), color='#cfe7ff', size=11,
                            text_align=ft.TextAlign.CENTER)
        )
        inner_stack.controls.append(label_container)

    # Dispositivos
    devices_config = [
        {"id": "dht", "left": 220, "top": 180, "label": "DHT", "color": "#fbbf24"},
        {"id": "cam", "left": 860, "top": 120, "label": "Cam", "color": "#fb7185"},
    ]
    for dev in devices_config:
        inner_stack.controls.append(ft.Container(
            left=dev["left"] - 10, top=dev["top"] - 10, width=20, height=20,
            border_radius=10, bgcolor=dev["color"], border=ft.border.all(2, 'white'),
            content=ft.Text(DEVICE_ICONS.get(dev["id"], '●'), text_align=ft.TextAlign.CENTER),
            alignment=ft.alignment.center
        ))
        inner_stack.controls.append(ft.Container(
            left=dev["left"] - 20, top=dev["top"] + 10, width=40, height=20,
            content=ft.Text(dev["label"], color='white', size=11, text_align=ft.TextAlign.CENTER)
        ))

    map_content.content = inner_stack

    # Scroll 2D
    map_scroll_horizontal = ft.Row([map_content], scroll=ft.ScrollMode.ALWAYS)
    map_scroll_container = ft.Column([map_scroll_horizontal], scroll=ft.ScrollMode.ALWAYS, expand=True)
    map_stack.controls.append(map_scroll_container)

    # Overlay
    ultima_lectura_humo = "OK"
    if datos_sensores:
        ultima_lectura_humo = datos_sensores[-1].get("valor", "N/A")

    summary_header = ft.Row([
        ft.Text("Estado general", size=9, color=COLORS['muted']),
        ft.ElevatedButton("Refrescar", on_click=on_refrescar_click,
                          style=ft.ButtonStyle(bgcolor=COLORS['bg'], color=COLORS['accent']))
    ])
    summary_label = ft.Text(f"Humo: {ultima_lectura_humo} PPM", size=10, weight=ft.FontWeight.BOLD,
                            color=COLORS['text'])
    overlay_content = ft.Column([summary_header, summary_label], spacing=5)
    overlay = ft.Container(content=overlay_content, width=320, height=70, bgcolor=COLORS['glass'],
                           border=ft.border.all(1), padding=10, right=20, bottom=20)
    map_stack.controls.append(overlay)

    map_card.content = map_stack

    # --- BOTTOM ROW (Tarjetas de Presos y Usuarios) ---
    bottom_row = ft.Row(spacing=12, expand=False)

    # [CAMBIO AQUI] Se pasa el on_borrar_preso_click
    bottom_row.controls.append(
        vista.vista_gestion_presos.crear_vista_presos(
            lista_presos=datos_presos,
            on_crear_preso_handler=on_crear_preso_click,
            on_refrescar_handler=on_refrescar_click,
            on_borrar_preso_handler=on_borrar_preso_click  # <--- Pasamos la función
        )
    )

    bottom_row.controls.append(
        vista.vista_gestion_usuarios.crear_vista_usuarios(
            rol_actual=rol_usuario,
            lista_usuarios=datos_usuarios,
            on_crear_usuario_handler=on_crear_usuario_click
        )
    )

    # --- COLUMNA IZQUIERDA ---
    left_column = ft.Column(
        spacing=12,
        expand=True,
        controls=[topbar, map_card, bottom_row]
    )

    # --- RIGHT PANEL ---
    right_column = ft.Container(
        width=380,
        bgcolor=COLORS['card'],
        padding=14,
        expand=True,
        content=ft.Column(spacing=12, expand=True, scroll=ft.ScrollMode.ADAPTIVE)
    )
    right_column.content.controls.append(
        ft.Text("Panel de Control y Sensores", size=12, weight=ft.FontWeight.BOLD, color=COLORS['text'])
    )

    led_estado = datos_actuadores.get("leds", {}).get("estado", "off")
    fan_estado = datos_actuadores.get("fan", {}).get("estado", "off")

    control_leds = ft.Container(
        bgcolor=COLORS['glass'], padding=10, border_radius=5,
        content=ft.Row([
            ft.Text(f"{DEVICE_ICONS['leds']} Luces Generales", color=COLORS['text']),
            ft.Container(expand=True),
            ft.Switch(
                value=(led_estado == "on"),
                on_change=lambda e, est=led_estado: on_control_actuador_click(e, "leds",
                                                                              "off" if est == "on" else "on"),
                disabled=(not puede_controlar)
            )
        ])
    )

    control_fan = ft.Container(
        bgcolor=COLORS['glass'], padding=10, border_radius=5,
        content=ft.Row([
            ft.Text(f"{DEVICE_ICONS['fan']} Ventilación", color=COLORS['text']),
            ft.Container(expand=True),
            ft.Switch(
                value=(fan_estado == "on"),
                on_change=lambda e, est=fan_estado: on_control_actuador_click(e, "fan", "off" if est == "on" else "on"),
                disabled=(not puede_controlar)
            )
        ])
    )

    right_column.content.controls.append(control_leds)
    right_column.content.controls.append(control_fan)
    right_column.content.controls.append(ft.Divider(height=10))

    right_column.content.controls.append(ft.Text("Log de Sensores (Últimos 10)", size=10, color=COLORS['muted']))

    log_list = ft.ListView(expand=True, spacing=5)
    if not datos_sensores:
        log_list.controls.append(ft.Text("No hay datos de sensores.", color=COLORS['muted']))
    else:
        for log in reversed(datos_sensores[-10:]):
            log_list.controls.append(
                ft.Text(f"[{log['timestamp']}] {log['sensor']}: {log['valor']}", color=COLORS['text'], size=9)
            )

    right_column.content.controls.append(ft.Container(content=log_list, expand=True))

    main_row = ft.Row([left_column, right_column], spacing=18, expand=True)

    return ft.View(
        "/dashboard",
        controls=[main_row],
        bgcolor=COLORS['bg'],
        padding=18
    )