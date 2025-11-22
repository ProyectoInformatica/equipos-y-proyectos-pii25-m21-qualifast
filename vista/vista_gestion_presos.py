import flet as ft
from vista.temas import COLORS


def crear_vista_presos(lista_presos, on_crear_preso_handler, on_refrescar_handler, on_borrar_preso_handler):
    """
    Crea la tarjeta de gestión de presos con búsqueda y borrado.
    """

    # 1. Header
    boton_refrescar = ft.IconButton(
        icon=ft.Icons.REFRESH,
        icon_color=COLORS['text'],
        tooltip="Recargar lista",
        on_click=on_refrescar_handler
    )

    header = ft.Row(
        controls=[
            ft.Text("Gestión de Presos", size=14, weight=ft.FontWeight.BOLD, color=COLORS['text']),
            ft.Container(expand=True),
            boton_refrescar
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # 2. Buscador
    campo_busqueda = ft.TextField(
        label="Buscar preso...",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=COLORS['glass'],
        color=COLORS['text'],
        border_color=COLORS['glass'],
        text_size=12,
        height=35,
        content_padding=5
    )

    # 3. Formulario de creación
    campo_nombre = ft.TextField(
        label="Nuevo nombre",
        bgcolor=COLORS['glass'],
        color=COLORS['text'],
        border_color=COLORS['glass'],
        text_size=12,
        height=40,
        content_padding=10,
        expand=True
    )

    boton_crear = ft.ElevatedButton(
        text="Añadir",
        bgcolor=COLORS['accent'],
        color='#06203a',
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
        on_click=lambda e: on_crear_preso_handler(e, campo_nombre)
    )

    form_row = ft.Row([campo_nombre, boton_crear], spacing=10)

    # 4. Lista de presos (ListView)
    list_view = ft.ListView(expand=True, spacing=5, padding=5)

    def renderizar_lista(texto_filtro=""):
        """Función interna para dibujar la lista filtrada"""
        list_view.controls.clear()

        # Filtramos la lista original
        lista_filtrada = [
            p for p in lista_presos
            if texto_filtro.lower() in p['nombre'].lower() or texto_filtro in str(p['id'])
        ]

        if not lista_filtrada:
            list_view.controls.append(
                ft.Text("No se encontraron presos.", color=COLORS['muted'], size=12, italic=True)
            )
        else:
            for preso in lista_filtrada:
                # Botón de borrado
                boton_borrar = ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=COLORS['bad'],
                    tooltip="Eliminar preso",
                    on_click=lambda e, id_p=preso['id']: on_borrar_preso_handler(e, id_p)
                )

                item_container = ft.Container(
                    bgcolor=COLORS['room_bg'],
                    padding=8,
                    border_radius=5,
                    content=ft.Row([
                        ft.Icon(ft.Icons.PERSON, color=COLORS['muted'], size=16),
                        ft.Column([
                            ft.Text(preso['nombre'], color=COLORS['text'], weight=ft.FontWeight.BOLD, size=12),
                            ft.Text(f"ID: {preso['id']} - {preso['delito']}", color=COLORS['muted'], size=10)
                        ], spacing=2, expand=True),
                        boton_borrar  # Añadimos el botón
                    ])
                )
                list_view.controls.append(item_container)

        # [CORRECCIÓN] Solo actualizamos si el control ya está en la página
        if list_view.page:
            list_view.update()

    # Conectar el evento de cambio en búsqueda
    campo_busqueda.on_change = lambda e: renderizar_lista(e.control.value)

    # Render inicial (carga los datos en memoria antes de mostrarse)
    renderizar_lista()

    list_container = ft.Container(
        content=list_view,
        bgcolor=COLORS['glass'],
        border_radius=5,
        padding=5,
        expand=True
    )

    # 5. Ensamblaje final
    return ft.Container(
        bgcolor=COLORS['card'],
        border=ft.border.all(2, COLORS['glass']),
        border_radius=10,
        padding=15,
        expand=True,
        content=ft.Column([
            header,
            campo_busqueda,
            ft.Divider(height=5, color="transparent"),
            form_row,
            ft.Divider(height=10, color="transparent"),
            list_container
        ])
    )