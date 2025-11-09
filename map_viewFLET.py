import flet as ft

COLORS = {
    'bg': '#0f1724',
    'card': '#0b1220',
    'accent': '#60a5fa',
    'muted': '#9aa7bf',
    'ok': '#16a34a',
    'bad': '#ef4444',
    'glass': '#19202d',
    'room_bg': '#11222f',
    'text': '#e6eef8',
    'door_closed': '#ef4444',
    'door_open': '#16a34a',
}

DEVICE_ICONS = {
    'dht': '🌡',
    'ldr': '💡',
    'mq2': '🔥',
    'mq135': '🌫',
    'leds': '🔆',
    'motor': '⚙',
    'fan': '🌀',
    'esp32': '🖧',
    'cam': '📷'
}

def main(page: ft.Page):
    page.title = "Planta Comisaría (Simulador)"
    page.bgcolor = COLORS['bg']
    page.padding = 18
    page.window_width = 1400
    page.window_height = 900

    def action_feedback(e):
        page.snack_bar = ft.SnackBar(ft.Text("Acción realizada"), open=True)
        page.update()

    # Main row: left and right
    left_column = ft.Column(spacing=12, expand=True)
    right_column = ft.Container(
        width=380,
        bgcolor=COLORS['card'],
        padding=14,
        expand=True,
        # <--- RECOMENDADO: Añadir scroll a la columna derecha por si el contenido no cabe
        content=ft.Column(spacing=12, expand=True, scroll=ft.ScrollMode.ADAPTIVE)
    )
    main_row = ft.Row([left_column, right_column], spacing=18, expand=True)
    page.add(main_row)

    # Topbar
    title = ft.Text("Planta Comisaría", size=18, weight=ft.FontWeight.BOLD, color=COLORS['text'])
    legend = ft.Text("🟢 Puerta abierta 🔴 Puerta cerrada", size=10, color=COLORS['muted'])
    left_side = ft.Row([title, legend])

    user_label = ft.Container(
        content=ft.Text("Invitado", size=10, weight=ft.FontWeight.BOLD, color=COLORS['text']),
        bgcolor=COLORS['glass'],
        padding=10
    )
    login_btn = ft.ElevatedButton("Iniciar sesión", bgcolor=COLORS['accent'], color='#06203a', on_click=action_feedback)
    logout_btn = ft.ElevatedButton("Cerrar sesión", bgcolor=COLORS['bg'], color=COLORS['accent'], on_click=action_feedback, visible=False)
    right_side = ft.Row([user_label, login_btn, logout_btn])

    topbar = ft.Row([left_side, ft.Container(expand=True), right_side])
    left_column.controls.append(topbar)

    # Map section
    map_card = ft.Container(bgcolor=COLORS['card'], border=ft.border.all(2), expand=True, padding=14)
    map_stack = ft.Stack(expand=True)

    # <--- MODIFICADO: Quitamos 'clip_behavior' para permitir el scroll
    map_content = ft.Container(width=1000, height=700) 
    inner_stack = ft.Stack(expand=True)

    # Rooms
    rooms = [
        {"name": "Recepción", "left": 40, "top": 40, "width": 420, "height": 300},
        {"name": "Sala de Vigilancia", "left": 520, "top": 40, "width": 420, "height": 300},
        {"name": "Despacho", "left": 40, "top": 380, "width": 420, "height": 260},
        {"name": "Celdas", "left": 520, "top": 380, "width": 420, "height": 260},
    ]
    for room in rooms:
        room_container = ft.Container(
            left=room["left"], top=room["top"], width=room["width"], height=room["height"],
            bgcolor=COLORS['room_bg'], border=ft.border.all(2, '#5a7a9e'),
            content=ft.Container(
                content=ft.Text(room["name"], color='#cfe7ff', size=16, text_align=ft.TextAlign.CENTER),
                alignment=ft.alignment.top_center, padding=ft.padding.only(top=20)
            )
        )
        inner_stack.controls.append(room_container)

    # Doors
    doors_config = [
        {"id": "door-1", "left": 460, "top": 160, "width": 40, "height": 20, "label": "P1"},
        {"id": "door-2", "left": 460, "top": 100, "width": 40, "height": 20, "label": "P2"},
        {"id": "door-3", "left": 460, "top": 420, "width": 40, "height": 20, "label": "P3"},
        {"id": "door-4", "left": 460, "top": 480, "width": 40, "height": 20, "label": "P4"},
    ]
    for door in doors_config:
        door_container = ft.Container(
            left=door["left"], top=door["top"], width=door["width"], height=door["height"],
            bgcolor=COLORS['door_closed'], border=ft.border.all(2, 'white'),
            on_click=action_feedback
        )
        inner_stack.controls.append(door_container)
        label_container = ft.Container(
            left=door["left"], top=door["top"] - 20, width=door["width"], height=20,
            content=ft.Text(door["label"], color='#cfe7ff', size=11, text_align=ft.TextAlign.CENTER)
        )
        inner_stack.controls.append(label_container)

    # Devices
    devices_config = [
        {"id": "dht", "left": 220, "top": 180, "label": "DHT", "color": "#fbbf24"},
        {"id": "ldr", "left": 640, "top": 120, "label": "LDR", "color": "#fde68a"},
        {"id": "mq2", "left": 220, "top": 470, "label": "MQ-2", "color": "#fb7185"},
        {"id": "mq135", "left": 640, "top": 470, "label": "MQ-135", "color": "#f472b6"},
        {"id": "leds", "left": 340, "top": 270, "label": "LEDs", "color": "#60a5fa"},
        {"id": "motor", "left": 820, "top": 270, "label": "Motor", "color": "#a78bfa"},
        {"id": "fan", "left": 820, "top": 540, "label": "Vent.", "color": "#34d399"},
        {"id": "esp32", "left": 100, "top": 120, "label": "ESP32", "color": "#60a5fa"},
        {"id": "cam", "left": 860, "top": 120, "label": "Cam", "color": "#fb7185"},
    ]
    for dev in devices_config:
        dev_container = ft.Container(
            left=dev["left"] - 10, top=dev["top"] - 10, width=20, height=20,
            border_radius=10, bgcolor=dev["color"], border=ft.border.all(2, 'white'),
            content=ft.Text(DEVICE_ICONS.get(dev["id"], '●'), text_align=ft.TextAlign.CENTER),
            alignment=ft.alignment.center,
            on_click=action_feedback
        )
        inner_stack.controls.append(dev_container)
        label_container = ft.Container(
            left=dev["left"] - 20, top=dev["top"] + 10, width=40, height=20,
            content=ft.Text(dev["label"], color='white', size=11, text_align=ft.TextAlign.CENTER)
        )
        inner_stack.controls.append(label_container)

    map_content.content = inner_stack

    # <--- AÑADIDO: Contenedor de Scroll 2D
    # 1. Creamos una Fila para el scroll horizontal
    map_scroll_horizontal = ft.Row(
        [map_content],
        scroll=ft.ScrollMode.ALWAYS
    )
    # 2. Creamos una Columna para el scroll vertical (que contiene la Fila anterior)
    map_scroll_container = ft.Column(
        [map_scroll_horizontal],
        scroll=ft.ScrollMode.ALWAYS,
        expand=True  # Hacemos que la Columna llene el espacio de la tarjeta
    )
    
    # 3. Añadimos el contenedor de scroll (NO el map_content) al Stack
    map_stack.controls.append(map_scroll_container)

    # Summary overlay
    summary_header = ft.Row([ft.Text("Estado general", size=9, color=COLORS['muted']), ft.ElevatedButton("Refrescar", on_click=action_feedback, style=ft.ButtonStyle(bgcolor=COLORS['bg'], color=COLORS['accent']))])
    summary_label = ft.Text("Cargando...", size=10, weight=ft.FontWeight.BOLD, color=COLORS['text'])
    overlay_content = ft.Column([summary_header, summary_label], spacing=5)
    
    # <--- MODIFICADO: Ajustada la posición del overlay para que se vea bien con el scroll
    overlay = ft.Container(content=overlay_content, width=320, height=70, bgcolor=COLORS['glass'], border=ft.border.all(1), padding=10, right=20, bottom=20) 
    map_stack.controls.append(overlay)

    map_card.content = map_stack
    left_column.controls.append(map_card)

    # Bottom info
    bottom_row = ft.Row(spacing=12, expand=False)

    # Prisoner card
    prisoner_card = ft.Container(bgcolor=COLORS['card'], border=ft.border.all(2), expand=True, padding=12)
    prisoner_header = ft.Row([ft.Text("Registros de presos", size=12, weight=ft.FontWeight.BOLD, color=COLORS['text']), ft.ElevatedButton("Nuevo preso", bgcolor=COLORS['accent'], color='#06203a', on_click=action_feedback)])
    prisoner_list = ft.ListView(expand=True)
    for i in range(3):
        prisoner_list.controls.append(ft.Text(f"Preso de ejemplo {i+1}", color=COLORS['text']))
    prisoner_list_container = ft.Container(content=prisoner_list, bgcolor=COLORS['glass'], height=100)
    prisoner_card.content = ft.Column([prisoner_header, prisoner_list_container])
    bottom_row.controls.append(prisoner_card)

    # User card
    user_card = ft.Container(width=320, bgcolor=COLORS['card'], border=ft.border.all(2), padding=12)
    user_header = ft.Text("Usuarios", size=12, weight=ft.FontWeight.BOLD, color=COLORS['text'])
    new_user_name = ft.TextField(value="usuario", bgcolor=COLORS['glass'], color=COLORS['text'], border_color=COLORS['glass'])
    new_user_pass = ft.TextField(value="contraseña", password=True, bgcolor=COLORS['glass'], color=COLORS['text'], border_color=COLORS['glass'])
    new_user_role = ft.Dropdown(value="policia", options=[ft.dropdown.Option("comisario"), ft.dropdown.Option("inspector"), ft.dropdown.Option("policia")], bgcolor=COLORS['glass'], color=COLORS['text'])
    create_btn = ft.ElevatedButton("Crear", bgcolor=COLORS['accent'], color='#06203a', on_click=action_feedback)
    create_form = ft.Row([new_user_role, create_btn])
    user_form = ft.Column([new_user_name, new_user_pass, create_form])
    user_list = ft.ListView(expand=True)
    for i in range(3):
        user_list.controls.append(ft.Text(f"Usuario de ejemplo {i+1}", color=COLORS['text']))
    user_list_container = ft.Container(content=user_list, bgcolor=COLORS['glass'], height=100)
    user_card.content = ft.Column([user_header, user_form, user_list_container])
    bottom_row.controls.append(user_card)

    left_column.controls.append(bottom_row)

    # Right panel: Devices
    devices_header = ft.Text("Dispositivos & Sensores", size=12, weight=ft.FontWeight.BOLD, color=COLORS['text'])
    right_column.content.controls.append(devices_header)

    devices_list = ft.ListView(expand=True, spacing=4)
    dev_configs = [
        {'id': 'dht', 'name': 'Sensor DHT11/DHT22', 'desc': 'Temperatura / Humedad', 'icon': '🌡'},
        {'id': 'ldr', 'name': 'Fotorresistor (LDR)', 'desc': 'Iluminancia (lux)', 'icon': '💡'},
        {'id': 'mq2', 'name': 'Sensor de humo (MQ-2)', 'desc': 'PPM humo', 'icon': '🔥'},
        {'id': 'mq135', 'name': 'Sensor calidad aire (MQ-135)', 'desc': 'Índice calidad aire', 'icon': '🌫'},
        {'id': 'leds', 'name': 'Diodos LED (pack 100 uds)', 'desc': 'Pack LEDs', 'icon': '🔆'},
        {'id': 'motor', 'name': 'Motor DC 12V', 'desc': 'Pack 5 unidades', 'icon': '⚙'},
        {'id': 'fan', 'name': 'Ventilador 5V', 'desc': 'Ventilador', 'icon': '🌀'},
        {'id': 'esp32', 'name': 'Placa ESP32', 'desc': 'Controlador', 'icon': '🖧'},
        {'id': 'cam', 'name': 'Cámara para ESP32', 'desc': 'Cámara', 'icon': '📷'}
    ]
    for dev in dev_configs:
        card = ft.Container(bgcolor=COLORS['glass'], border=ft.border.all(1), padding=8)
        icon = ft.Text(dev['icon'], size=20)
        name = ft.Text(dev['name'], size=9, weight=ft.FontWeight.BOLD, color=COLORS['text'])
        desc = ft.Text(dev['desc'], size=8, color=COLORS['muted'])
        left = ft.Row([icon, ft.Column([name, desc], expand=True)])
        switch = ft.Switch(value=True, on_change=action_feedback)
        value = ft.Text("Valor ejemplo", size=9, weight=ft.FontWeight.BOLD, color=COLORS['text'], width=100)
        edit_btn = ft.ElevatedButton("Editar", bgcolor=COLORS['bg'], color=COLORS['accent'], on_click=action_feedback)
        right = ft.Row([switch, value, edit_btn])
        card.content = ft.Row([left, ft.Container(expand=True), right])
        devices_list.controls.append(card)
    right_column.content.controls.append(devices_list)

    # Doors section
    doors_section = ft.Container(bgcolor=COLORS['glass'], border=ft.border.all(1), padding=10)
    doors_header = ft.Text("Puertas", size=11, weight=ft.FontWeight.BOLD, color=COLORS['text'])
    doors_col = ft.Column(spacing=3)
    for door_id in ['door-1', 'door-2', 'door-3', 'door-4']:
        info = ft.Column([ft.Text(door_id.upper(), size=9, weight=ft.FontWeight.BOLD, color=COLORS['text']), ft.Text("Estado: Cerrada", size=8, color=COLORS['bad'])])
        toggle_btn = ft.ElevatedButton("Abrir", bgcolor=COLORS['bg'], color=COLORS['accent'], on_click=action_feedback)
        door_row = ft.Row([info, ft.Container(expand=True), toggle_btn])
        doors_col.controls.append(door_row)
    doors_section.content = ft.Column([doors_header, doors_col])
    right_column.content.controls.append(doors_section)

    # Actions section
    actions_section = ft.Container(bgcolor=COLORS['glass'], border=ft.border.all(1), padding=10)
    actions_header = ft.Text("Acciones rápidas", size=11, weight=ft.FontWeight.BOLD, color=COLORS['text'])
    actions_row = ft.Row([ft.ElevatedButton("Abrir todas", bgcolor=COLORS['bg'], color=COLORS['accent'], on_click=action_feedback),
                          ft.ElevatedButton("Cerrar todas", bgcolor=COLORS['bg'], color=COLORS['accent'], on_click=action_feedback),
                          ft.ElevatedButton("Reset", bgcolor=COLORS['accent'], color='#06203a', on_click=action_feedback)])
    note = ft.Text("Los cambios se guardan automáticamente.", size=8, color=COLORS['muted'])
    actions_section.content = ft.Column([actions_header, actions_row, note])
    right_column.content.controls.append(actions_section)

    page.update()

ft.app(target=main)