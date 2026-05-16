import flet as ft
from vista.temas import COLORS


def crear_vista_consumo(on_volver_dashboard):
    def create_kpi_card(title, value_ctrl, unit, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icon, color=color, size=24), ft.Text(title, color=COLORS['muted'], size=14)],
                       alignment="center"),
                value_ctrl,
                ft.Text(unit, size=14, color=COLORS['accent'], weight="bold")
            ], horizontal_alignment="center", spacing=5),
            bgcolor=COLORS['room_bg'], padding=20, border_radius=10, border=ft.border.all(1, color), expand=True,
            height=140, alignment=ft.alignment.center
        )

    txt_total_val = ft.Text("...", size=32, weight="bold", color=COLORS['text'])
    txt_dia_val = ft.Text("...", size=32, weight="bold", color=COLORS['text'])
    txt_mes_val = ft.Text("...", size=32, weight="bold", color=COLORS['text'])

    card_total = create_kpi_card("Potencia Actual", txt_total_val, "Watts (W)", ft.Icons.SPEED, COLORS['good'])
    card_dia = create_kpi_card("Media Diaria", txt_dia_val, "Watts (W)", ft.Icons.LIGHT_MODE, COLORS['accent'])
    card_mes = create_kpi_card("Media Mensual", txt_mes_val, "Watts (W)", ft.Icons.CALENDAR_MONTH, "orange")

    tabla_consumo = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Dispositivo", weight="bold")),
            ft.DataColumn(ft.Text("Estado", weight="bold")),
            ft.DataColumn(ft.Text("Consumo", weight="bold", text_align="right")),
        ],
        rows=[], border=ft.border.all(1, COLORS['glass']), heading_row_color=COLORS['glass'], expand=True
    )

    def actualizar_consumo(datos):
        if not txt_total_val.page: return
        txt_total_val.value = str(datos["total_actual"])
        txt_dia_val.value = str(datos["media_dia"])
        txt_mes_val.value = str(datos["media_mes"])

        tabla_consumo.rows.clear()
        for d in datos["detalles"]:
            color_st = COLORS['good'] if d['estado'] in ["ON", "Activo", "Moviendo", "Online", "Constante"] else COLORS['muted']
            tabla_consumo.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(d['nombre'], color=COLORS['text'])),
                    ft.DataCell(ft.Text(d['estado'], color=color_st, weight="bold")),
                    # Cambiamos "watts" por "consumo" para que coincida con la Base de Datos
                    ft.DataCell(ft.Text(str(d.get('consumo', '0 W')), color=COLORS['text'])),
                ])
            )
        if txt_total_val.page:
            txt_total_val.update()
            txt_dia_val.update()
            txt_mes_val.update()
            tabla_consumo.update()

    header = ft.Row([
        ft.Text("Monitor de Consumo Eléctrico", size=24, weight="bold", color=COLORS['accent']),
        ft.Container(expand=True),
    ], alignment="center")

    kpi_row = ft.Row([card_total, card_dia, card_mes], alignment="center", spacing=20)

    content_col = ft.Column([
        header, ft.Divider(color=COLORS['glass']), ft.Container(height=10),
        kpi_row, ft.Container(height=20),
        ft.Text("Desglose por Dispositivo", size=18, weight="bold", color=COLORS['text']),
        ft.Container(content=ft.Column([tabla_consumo], scroll=ft.ScrollMode.AUTO, expand=True), expand=True)
    ], expand=True)

    # Ahora devolvemos un Container preparado para encajar con el menú lateral
    main_container = ft.Container(bgcolor=COLORS['card'], padding=30, border_radius=10,
                                  border=ft.border.all(1, COLORS['glass']), expand=True, content=content_col)

    # Adjuntamos el callback para que el hilo de fondo pueda actualizarlo
    main_container.data = {"update_callback": actualizar_consumo}

    return main_container