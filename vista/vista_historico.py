import flet as ft
from vista.temas import COLORS


def crear_vista_historico(datos_sensores, datos_actuadores, on_volver_dashboard):
    """
    Muestra los logs históricos organizados por tipo de sensor/actuador.
    CORREGIDO: Error de scroll en Container.
    """

    # 1. Organizar datos sensores por tipo
    logs_por_tipo = {}
    for log in datos_sensores:
        tipo = log['sensor']
        if tipo not in logs_por_tipo:
            logs_por_tipo[tipo] = []
        logs_por_tipo[tipo].append(log)

    # 2. Crear pestañas para Sensores
    tabs_sensores = []

    # Si no hay logs, mostramos mensaje
    if not logs_por_tipo:
        tabs_sensores.append(ft.Tab(text="Sin datos", content=ft.Text("No hay registros disponibles.")))

    for tipo, logs in logs_por_tipo.items():
        # Crear filas de datos
        filas = []
        for l in reversed(logs):  # Más recientes primero
            filas.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(l['timestamp'], color=COLORS['text'])),
                    ft.DataCell(ft.Text(str(l['valor']), color=COLORS['accent'])),
                ])
            )

        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Fecha/Hora", weight="bold", color=COLORS['muted'])),
                ft.DataColumn(ft.Text("Valor", weight="bold", color=COLORS['muted'])),
            ],
            rows=filas,
            border=ft.border.all(1, COLORS['glass']),
            heading_row_color=COLORS['glass'],
            vertical_lines=ft.border.BorderSide(1, COLORS['glass']),
            horizontal_lines=ft.border.BorderSide(1, COLORS['glass']),
        )

        # --- CORRECCIÓN DEL ERROR ---
        # El scroll se aplica a la COLUMNA, no al Container.
        tab_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(f"Histórico: {tipo}", size=20, weight="bold", color=COLORS['accent']),
                    tabla
                ],
                scroll=ft.ScrollMode.AUTO,  # <--- AQUÍ SÍ FUNCIONA EL SCROLL
                expand=True
            ),
            padding=20,
            expand=True
        )

        tabs_sensores.append(ft.Tab(text=tipo, content=tab_content))

    # 3. Pestaña Actuadores
    items_actuadores = []
    for k, v in datos_actuadores.items():
        items_actuadores.append(
            ft.ListTile(
                leading=ft.Icon(ft.Icons.SETTINGS_REMOTE, color=COLORS['accent']),
                title=ft.Text(f"Dispositivo: {k.upper()}", color=COLORS['text']),
                subtitle=ft.Text(f"Estado Actual: {v.get('estado', 'N/A')}", color=COLORS['muted'])
            )
        )

    tab_actuadores = ft.Tab(
        text="Actuadores",
        content=ft.Container(
            content=ft.ListView(controls=items_actuadores, spacing=10),
            padding=20
        )
    )

    tabs_sensores.append(tab_actuadores)

    tbs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=tabs_sensores,
        expand=True,
        divider_color=COLORS['glass'],
        indicator_color=COLORS['accent'],
        label_color=COLORS['accent'],
        unselected_label_color=COLORS['muted'],
        scrollable=True  # Permite scroll en las pestañas si hay muchas
    )

    return ft.View(
        "/historico",
        bgcolor=COLORS['bg'],
        appbar=ft.AppBar(
            title=ft.Text("Registro Histórico de Sensores"),
            bgcolor=COLORS['card'],
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=on_volver_dashboard)
        ),
        controls=[tbs]
    )