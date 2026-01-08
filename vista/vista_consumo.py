import flet as ft
from vista.temas import COLORS


def crear_vista_consumo(on_volver_dashboard):
    # --- UI Elements ---

    # 1. Header Cards
    def create_kpi_card(title, value, unit, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icon, color=color, size=24), ft.Text(title, color=COLORS['muted'], size=12)],
                       alignment="center"),
                ft.Text(f"{value}", size=28, weight="bold", color=COLORS['text'], text_align="center"),
                ft.Text(unit, size=14, color=COLORS['accent'], weight="bold")
            ], horizontal_alignment="center", spacing=5),
            bgcolor=COLORS['card'],
            padding=20,
            border_radius=10,
            border=ft.border.all(1, color),
            width=200,
            height=140,
            alignment=ft.alignment.center
        )

    # Contenedores para actualizar valores
    txt_total_val = ft.Text("...", size=28, weight="bold", color=COLORS['text'])
    txt_dia_val = ft.Text("...", size=28, weight="bold", color=COLORS['text'])
    txt_mes_val = ft.Text("...", size=28, weight="bold", color=COLORS['text'])

    # Reconstruimos las cards con las referencias de texto
    card_total = ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.FLASH_ON, color="yellow", size=24),
                    ft.Text("Consumo Actual", color=COLORS['muted'], size=12)], alignment="center"),
            txt_total_val,
            ft.Text("Watts (W)", size=14, color="yellow", weight="bold")
        ], horizontal_alignment="center", spacing=5),
        bgcolor=COLORS['card'], padding=20, border_radius=10, border=ft.border.all(1, "yellow"), width=200, height=140,
        alignment=ft.alignment.center
    )

    card_dia = ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.TODAY, color=COLORS['accent'], size=24),
                    ft.Text("Media Diaria", color=COLORS['muted'], size=12)], alignment="center"),
            txt_dia_val,
            ft.Text("Watts (Promedio)", size=12, color=COLORS['accent'])
        ], horizontal_alignment="center", spacing=5),
        bgcolor=COLORS['card'], padding=20, border_radius=10, border=ft.border.all(1, COLORS['accent']), width=200,
        height=140, alignment=ft.alignment.center
    )

    card_mes = ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.CALENDAR_MONTH, color=COLORS['good'], size=24),
                    ft.Text("Media Mensual", color=COLORS['muted'], size=12)], alignment="center"),
            txt_mes_val,
            ft.Text("Watts (Promedio)", size=12, color=COLORS['good'])
        ], horizontal_alignment="center", spacing=5),
        bgcolor=COLORS['card'], padding=20, border_radius=10, border=ft.border.all(1, COLORS['good']), width=200,
        height=140, alignment=ft.alignment.center
    )

    # 2. Data Table
    tabla_consumo = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Dispositivo", color=COLORS['accent'], weight="bold")),
            ft.DataColumn(ft.Text("Estado", color=COLORS['accent'], weight="bold")),
            ft.DataColumn(ft.Text("Consumo (W)", color=COLORS['accent'], weight="bold"), numeric=True),
        ],
        rows=[],
        border=ft.border.all(1, COLORS['glass']),
        heading_row_color=COLORS['glass'],
        column_spacing=40
    )

    container_tabla = ft.Container(
        content=tabla_consumo,
        bgcolor=COLORS['card'],
        padding=20,
        border_radius=10,
        alignment=ft.alignment.top_center
    )

    # --- CALLBACK DE ACTUALIZACIÓN ---
    def update_view(data):
        if not data: return

        # KPI Update
        txt_total_val.value = f"{data['total_actual']}"
        txt_dia_val.value = f"{data['media_dia']}"
        txt_mes_val.value = f"{data['media_mes']}"

        # Tabla Update
        tabla_consumo.rows.clear()
        detalles = data.get('detalles', [])
        for d in detalles:
            color_st = COLORS['good'] if d['estado'] in ["ON", "Activo", "Online", "Moviendo"] else COLORS['muted']
            if d['estado'] == "Moviendo": color_st = "orange"

            tabla_consumo.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(d['nombre'], color=COLORS['text'])),
                    ft.DataCell(ft.Text(d['estado'], color=color_st, weight="bold")),
                    ft.DataCell(ft.Text(f"{d['watts']} W", color=COLORS['text'])),
                ])
            )

        if txt_total_val.page:
            txt_total_val.update()
            txt_dia_val.update()
            txt_mes_val.update()
            tabla_consumo.update()

    # Layout Principal
    header = ft.Row([
        ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: on_volver_dashboard(e), icon_color=COLORS['accent']),
        ft.Text("Monitor de Consumo Eléctrico", size=24, weight="bold", color=COLORS['text']),
        ft.Container(expand=True),
        #ft.Icon(ft.Icons.REFRESH, color=COLORS['muted'], size=16),
        #ft.Text("Actualizado cada 5s", color=COLORS['muted'], size=12)
    ], alignment="center")

    kpi_row = ft.Row([card_total, card_dia, card_mes], alignment="center", spacing=20)

    content = ft.Column([
        header,
        ft.Divider(color=COLORS['muted']),
        ft.Container(height=20),
        kpi_row,
        ft.Container(height=20),
        ft.Text("Desglose por Dispositivo", size=16, color=COLORS['text'], weight="bold"),
        container_tabla
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    view = ft.View(
        "/consumo",
        controls=[ft.Container(content=content, padding=20, expand=True)],
        bgcolor=COLORS['bg']
    )
    view.data = {"update_callback": update_view}  # Hook para el controlador

    return view