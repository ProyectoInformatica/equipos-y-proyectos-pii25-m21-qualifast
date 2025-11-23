import flet as ft
from vista.temas import COLORS


def crear_dialogo_preso(titulo, on_guardar, preso_actual=None):
    val_nombre = preso_actual.get("nombre", "") if preso_actual else ""
    val_delito = preso_actual.get("delito", "") if preso_actual else ""
    val_celda = preso_actual.get("celda", "") if preso_actual else ""

    txt_nombre = ft.TextField(label="Nombre Completo", value=val_nombre, bgcolor=COLORS['glass'],
                              border_color=COLORS['muted'])
    txt_delito = ft.TextField(label="Motivo / Delito", value=val_delito, bgcolor=COLORS['glass'],
                              border_color=COLORS['muted'], multiline=True)
    txt_celda = ft.TextField(label="Celda Asignada", value=val_celda, bgcolor=COLORS['glass'],
                             border_color=COLORS['muted'])

    dialogo = None

    def guardar_click(e):
        datos = {
            "nombre": txt_nombre.value,
            "delito": txt_delito.value,
            "celda": txt_celda.value,
            "id": preso_actual.get("id") if preso_actual else None
        }
        on_guardar(e, datos, dialogo)

    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Text(titulo, color=COLORS['text']),
        content=ft.Column([txt_nombre, txt_delito, txt_celda], tight=True, width=400),
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
    """
    Tarjeta de presos con ESTILO ORIGINAL (filas detalladas) y ALTURA EXPANDIDA.
    """

    # --- HEADER ---
    boton_refrescar = ft.IconButton(
        icon=ft.Icons.REFRESH,
        icon_color=COLORS['text'],
        tooltip="Recargar",
        on_click=on_refrescar_handler
    )

    boton_nuevo_preso = ft.ElevatedButton(
        "Nuevo preso",
        icon=ft.Icons.ADD,
        bgcolor=COLORS['accent'],
        color='#06203a',
        on_click=on_abrir_crear_handler
    )

    header_title = ft.Text("Gestión de Presos", size=14, weight=ft.FontWeight.BOLD, color=COLORS['text'])

    # --- BUSCADOR ---
    campo_busqueda = ft.TextField(
        hint_text="Buscar...",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=COLORS['glass'],
        color=COLORS['text'],
        border_color=COLORS['glass'],
        text_size=12,
        height=35,
        content_padding=5,
        expand=True
    )

    top_row = ft.Row([
        header_title,
        ft.Container(width=10),
        campo_busqueda,
        boton_refrescar,
        boton_nuevo_preso
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # --- LISTA DE PRESOS (Diseño detallado restaurado) ---
    list_view = ft.ListView(expand=True, spacing=5, padding=5)

    def renderizar_lista(texto_filtro=""):
        list_view.controls.clear()
        lista_filtrada = [p for p in lista_presos if texto_filtro.lower() in p['nombre'].lower()]

        if not lista_filtrada:
            list_view.controls.append(
                ft.Text("No se encontraron coincidencias.", color=COLORS['muted'], size=12, italic=True))
        else:
            for preso in lista_filtrada:
                p_nombre = preso.get("nombre", "Sin nombre")
                p_delito = preso.get("delito", "Sin causa")
                p_celda = preso.get("celda", "N/A")
                p_fecha = preso.get("fecha_ingreso", "--/--")
                p_id = preso.get("id")

                btn_editar = ft.IconButton(
                    icon=ft.Icons.EDIT,
                    icon_size=18,
                    icon_color=COLORS['accent'],
                    tooltip="Editar",
                    on_click=lambda e, p=preso: on_abrir_editar_handler(e, p)
                )

                btn_borrar = ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_size=18,
                    icon_color=COLORS['bad'],
                    tooltip="Eliminar",
                    on_click=lambda e, pid=p_id: on_borrar_preso_handler(e, pid)
                )

                # --- DISEÑO DE FILA DETALLADO (Como estaba antes) ---
                item_container = ft.Container(
                    bgcolor=COLORS['room_bg'],
                    padding=10,
                    border_radius=5,
                    content=ft.Row([
                        ft.Icon(ft.Icons.PERSON, color=COLORS['muted'], size=24),

                        # Columna Izquierda: Nombre y Delito
                        ft.Column([
                            ft.Text(p_nombre, color=COLORS['text'], weight=ft.FontWeight.BOLD),
                            ft.Text(f"Motivo: {p_delito}", color=COLORS['muted'], size=11),
                        ], spacing=2, expand=True),

                        # Columna Derecha: Celda y Fecha
                        ft.Column([
                            ft.Text(f"Celda: {p_celda}", color=COLORS['accent'], size=11, weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.RIGHT),
                            ft.Text(f"Ingreso: {p_fecha}", color=COLORS['muted'], size=10,
                                    text_align=ft.TextAlign.RIGHT),
                        ], spacing=2, alignment=ft.MainAxisAlignment.END),

                        ft.Container(width=10),
                        ft.Row([btn_editar, btn_borrar], spacing=0)

                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
                list_view.controls.append(item_container)

        if list_view.page: list_view.update()

    campo_busqueda.on_change = lambda e: renderizar_lista(e.control.value)
    renderizar_lista()

    # --- CONTENEDOR FINAL ---
    return ft.Container(
        bgcolor=COLORS['card'],
        border=ft.border.all(2, COLORS['glass']),
        border_radius=10,
        padding=15,
        expand=True,  # ESTO asegura que sea LARGA hacia abajo
        content=ft.Column([
            top_row,
            ft.Divider(height=10, color="transparent"),
            list_view
        ])
    )