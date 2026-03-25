import flet as ft
from vista.temas import COLORS


def crear_dialogo_preso(titulo, on_guardar, preso_actual=None):
    val_nombre = preso_actual.get("nombre", "") if preso_actual else ""
    val_delito = preso_actual.get("delito", "") if preso_actual else ""
    val_celda = preso_actual.get("celda", "Celda 1") if preso_actual else "Celda 1"

    txt_nombre = ft.TextField(
        label="Nombre Completo",
        value=val_nombre,
        bgcolor=COLORS['glass'],
        border_color=COLORS['muted']
    )
    txt_delito = ft.TextField(
        label="Motivo / Delito",
        value=val_delito,
        bgcolor=COLORS['glass'],
        border_color=COLORS['muted'],
        multiline=True
    )
    dd_celda = ft.Dropdown(
        label="Celda Asignada",
        value=val_celda,
        bgcolor=COLORS['glass'],
        border_color=COLORS['muted'],
        options=[
            ft.dropdown.Option("Celda 1"),
            ft.dropdown.Option("Celda 2"),
            ft.dropdown.Option("Celda 3"),
            ft.dropdown.Option("Celda 4"),
        ]
    )

    dialogo = None

    def guardar_click(e):
        datos = {
            "nombre": txt_nombre.value,
            "delito": txt_delito.value,
            "celda": dd_celda.value,
            "id": preso_actual.get("id") if preso_actual else None
        }
        on_guardar(e, datos, dialogo)

    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Text(titulo, color=COLORS['text']),
        content=ft.Column([txt_nombre, txt_delito, dd_celda], tight=True, width=400),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: e.page.close(dialogo)),
            ft.ElevatedButton("Guardar", on_click=guardar_click, bgcolor=COLORS['accent'], color=COLORS['bg']),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=COLORS['card']
    )
    return dialogo


def crear_vista_presos(lista_presos, on_abrir_crear_handler, on_abrir_editar_handler, on_refrescar_handler,
                       on_borrar_preso_handler):
    boton_refrescar = ft.IconButton(icon=ft.Icons.REFRESH, icon_color=COLORS['text'], tooltip="Recargar BD",
                                    on_click=on_refrescar_handler)
    boton_nuevo_preso = ft.ElevatedButton("Registrar Nuevo Preso", icon=ft.Icons.ADD, bgcolor=COLORS['accent'],
                                          color='#06203a', on_click=on_abrir_crear_handler)

    header_title = ft.Text("Base de Datos: Gestión de Presos", size=24, weight=ft.FontWeight.BOLD,
                           color=COLORS['accent'])

    campo_busqueda = ft.TextField(
        hint_text="Buscar preso por nombre...", prefix_icon=ft.Icons.SEARCH, bgcolor=COLORS['glass'],
        color=COLORS['text'], border_color=COLORS['glass'], height=45, expand=True
    )

    top_row = ft.Row([header_title, ft.Container(expand=True), campo_busqueda, boton_refrescar, boton_nuevo_preso],
                     alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    list_view = ft.ListView(expand=True, spacing=10, padding=10)

    def renderizar_lista(texto_filtro=""):
        list_view.controls.clear()
        lista_filtrada = [p for p in lista_presos if texto_filtro.lower() in p['nombre'].lower()]

        if not lista_filtrada:
            list_view.controls.append(
                ft.Text("No se encontraron coincidencias en la base de datos.", color=COLORS['muted'], size=14,
                        italic=True))
        else:
            for preso in lista_filtrada:
                p_id = preso.get("id")
                item_container = ft.Container(
                    bgcolor=COLORS['room_bg'], padding=15, border_radius=8,
                    content=ft.Row([
                        ft.Icon(ft.Icons.PERSON, color=COLORS['muted'], size=30),
                        ft.Column([
                            ft.Text(preso.get("nombre", ""), color=COLORS['text'], weight=ft.FontWeight.BOLD, size=16),
                            ft.Text(f"Delito imputado: {preso.get('delito', '')}", color=COLORS['muted'], size=13)
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(f"{preso.get('celda', 'Sin asignar')}", color=COLORS['accent'], size=14,
                                    weight="bold"),
                            ft.Text(f"Ingreso: {preso.get('fecha_ingreso', '')}", color=COLORS['muted'], size=11)
                        ], spacing=2, alignment=ft.MainAxisAlignment.END),
                        ft.Container(width=20),
                        ft.Row([
                            ft.IconButton(icon=ft.Icons.EDIT, icon_color=COLORS['accent'], tooltip="Editar Registro",
                                          on_click=lambda e, p=preso: on_abrir_editar_handler(e, p)),
                            ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=COLORS['bad'], tooltip="Eliminar",
                                          on_click=lambda e, pid=p_id: on_borrar_preso_handler(e, pid))
                        ], spacing=5)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
                list_view.controls.append(item_container)
        if list_view.page: list_view.update()

    campo_busqueda.on_change = lambda e: renderizar_lista(e.control.value)
    renderizar_lista()

    return ft.Container(
        bgcolor=COLORS['card'], border=ft.border.all(2, COLORS['glass']), border_radius=10, padding=25, expand=True,
        content=ft.Column([top_row, ft.Divider(height=20, color=COLORS['glass']), list_view])
    )