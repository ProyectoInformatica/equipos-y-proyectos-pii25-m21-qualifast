import flet as ft
from vista.temas import COLORS, DEVICE_ICONS


def crear_vista_historico(datos_promedio_sensores, datos_log_actuadores, on_volver_dashboard):
    """
    Vista histórica rediseñada:
    1. Puertas (7 días) -> Visualización de accesos.
    2. Actuadores -> Historial de cambios de estado (Tabla con tiempos).
    3. Sensores -> Tabla de promedios por hora.
    """

    tabs_list = []

    # --- PESTAÑA 1: PUERTAS (Accesos) ---
    logs_puertas = [log for log in datos_log_actuadores if "door" in log['id']]
    puertas_ids = ["door-1", "door-2", "door-3", "door-4"]
    columnas_puertas = []

    for pid in puertas_ids:
        logs_esta_puerta = [p for p in logs_puertas if p['id'] == pid]
        label_puerta = logs_esta_puerta[0]['label'] if logs_esta_puerta else pid.replace("door-", "P")

        eventos_list = ft.ListView(expand=True, spacing=10, padding=5)

        if not logs_esta_puerta:
            eventos_list.controls.append(ft.Text("Sin actividad", size=10, color=COLORS['muted'], italic=True))
        else:
            for evento in reversed(logs_esta_puerta):
                color_estado = COLORS['good'] if evento['accion'] == "abierta" else COLORS['bad']
                icon_estado = ft.Icons.LOCK_OPEN if evento['accion'] == "abierta" else ft.Icons.LOCK_OUTLINE

                card = ft.Container(
                    bgcolor=COLORS['glass'], padding=8, border_radius=5,
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(icon_estado, color=color_estado, size=14),
                            ft.Text(evento['accion'].upper(), color=color_estado, weight="bold", size=11)
                        ]),
                        ft.Text(f"👤 {evento.get('usuario', 'sistema')}", size=10, color=COLORS['text']),
                        ft.Text(f"🕒 {evento['timestamp']}", size=9, color=COLORS['muted']),
                    ], spacing=2)
                )
                eventos_list.controls.append(card)

        col_container = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text(f"PUERTA {label_puerta}", weight="bold", color=COLORS['accent'], size=12),
                    bgcolor=COLORS['room_bg'], padding=5, border_radius=5, alignment=ft.alignment.center
                ),
                eventos_list
            ], expand=True),
            expand=1,
            bgcolor=COLORS['card'], padding=5, border=ft.border.all(1, COLORS['glass']), border_radius=8
        )
        columnas_puertas.append(col_container)

    tab_puertas = ft.Tab(
        text="🚪 Puertas",
        content=ft.Container(
            content=ft.Row(controls=columnas_puertas, expand=True, spacing=5),
            padding=10
        )
    )
    tabs_list.append(tab_puertas)

    # --- PESTAÑA 2: ACTUADORES (Historial en Tabla) ---
    logs_otros_actuadores = [log for log in datos_log_actuadores if "door" not in log['id']]

    filas_actuadores = []

    # --- CORRECCIÓN DEL ERROR ---
    if not logs_otros_actuadores:
        # Si no hay datos, debemos rellenar 4 celdas para cumplir con las 4 columnas
        filas_actuadores.append(ft.DataRow(cells=[
            ft.DataCell(ft.Text("Sin registros recientes", italic=True, color=COLORS['muted'])),
            ft.DataCell(ft.Text("")),  # Celda vacía obligatoria
            ft.DataCell(ft.Text("")),  # Celda vacía obligatoria
            ft.DataCell(ft.Text("")),  # Celda vacía obligatoria
        ]))
    else:
        for log in reversed(logs_otros_actuadores):
            icon_str = ft.Icons.SETTINGS
            if "led" in log['id']:
                icon_str = ft.Icons.LIGHTBULB
            elif "fan" in log['id']:
                icon_str = ft.Icons.AIR

            color_st = COLORS['good'] if log['accion'] == "on" else COLORS['muted']

            filas_actuadores.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(log['timestamp'], size=12, color=COLORS['text'])),
                ft.DataCell(ft.Row([
                    ft.Icon(icon_str, size=16, color=COLORS['accent']),
                    ft.Text(log.get('label', log['id']), size=12, color=COLORS['text'])
                ])),
                ft.DataCell(ft.Container(
                    content=ft.Text(log['accion'].upper(), size=10, weight="bold", color="#000000"),
                    bgcolor=color_st, padding=5, border_radius=5
                )),
                ft.DataCell(ft.Text(f"👤 {log.get('usuario', 'sistema')}", size=12, color=COLORS['muted'])),
            ]))

    tabla_actuadores = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Fecha / Hora", weight="bold")),
            ft.DataColumn(ft.Text("Dispositivo", weight="bold")),
            ft.DataColumn(ft.Text("Estado", weight="bold")),
            ft.DataColumn(ft.Text("Usuario", weight="bold")),
        ],
        rows=filas_actuadores,
        border=ft.border.all(1, COLORS['glass']),
        heading_row_color=COLORS['glass'],
        column_spacing=20
    )

    tab_actuadores = ft.Tab(
        text="⚙️ Historial Actuadores",
        content=ft.Container(
            content=ft.Column([
                ft.Text("Registro de actividad (Luces, Ventilación, etc.)", size=16, weight="bold",
                        color=COLORS['text']),
                # Mantenemos la corrección de scroll de la respuesta anterior
                ft.Column([tabla_actuadores], scroll=ft.ScrollMode.AUTO, expand=True)
            ], expand=True),
            padding=10
        )
    )
    tabs_list.append(tab_actuadores)

    # --- PESTAÑA 3: SENSORES (Medias por Hora) ---
    controles_sensores = []

    if not datos_promedio_sensores:
        controles_sensores.append(
            ft.Text("No hay suficientes datos para calcular promedios.", italic=True, color=COLORS['muted']))
    else:
        for nombre_sensor, datos in datos_promedio_sensores.items():
            filas_sensor = []
            for d in datos:
                filas_sensor.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(d['hora'], color=COLORS['text'])),
                    ft.DataCell(ft.Text(d['valor'], color=COLORS['accent'], weight="bold")),
                ]))

            # Mantenemos la eliminación de los argumentos de altura
            tabla_sensor = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Hora", color=COLORS['muted'])),
                    ft.DataColumn(ft.Text("Promedio", color=COLORS['muted'])),
                ],
                rows=filas_sensor,
                border=ft.border.all(1, COLORS['glass']),
                heading_row_color=COLORS['glass']
            )

            icon_s = "📝"
            if "Temp" in nombre_sensor:
                icon_s = DEVICE_ICONS['dht11']
            elif "Humo" in nombre_sensor:
                icon_s = DEVICE_ICONS['mq-2']
            elif "Aire" in nombre_sensor:
                icon_s = DEVICE_ICONS['mq-135']
            elif "Luz" in nombre_sensor:
                icon_s = DEVICE_ICONS['ldr']

            card_sensor = ft.Container(
                bgcolor=COLORS['card'], padding=15, border_radius=10, border=ft.border.all(1, COLORS['glass']),
                content=ft.Column([
                    ft.Text(f"{icon_s} {nombre_sensor}", size=16, weight="bold", color=COLORS['accent']),
                    ft.Divider(color=COLORS['glass']),
                    ft.Column([tabla_sensor], scroll=ft.ScrollMode.AUTO, expand=True)
                ], expand=True)
            )
            controles_sensores.append(card_sensor)

    tab_sensores = ft.Tab(
        text="📈 Sensores (Medias)",
        content=ft.Container(
            content=ft.GridView(
                controls=controles_sensores,
                runs_count=2,
                max_extent=400,
                child_aspect_ratio=1.0,
                spacing=10,
                run_spacing=10,
            ),
            padding=20
        )
    )
    tabs_list.append(tab_sensores)

    tbs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=tabs_list,
        expand=True,
        divider_color=COLORS['glass'],
        indicator_color=COLORS['accent'],
        label_color=COLORS['accent'],
        unselected_label_color=COLORS['muted'],
    )

    return ft.View(
        "/historico",
        bgcolor=COLORS['bg'],
        appbar=ft.AppBar(
            title=ft.Text("Histórico y Logs del Sistema"),
            bgcolor=COLORS['card'],
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=on_volver_dashboard)
        ),
        controls=[tbs]
    )