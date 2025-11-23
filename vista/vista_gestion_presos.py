import flet as ft
from vista.temas import COLORS


def crear_vista_presos(lista_presos, on_crear_preso_handler, on_refrescar_handler, on_borrar_preso_handler):
    """
    Crea la tarjeta de gestión de presos.
    Recibe la lista actual de presos y las funciones del controlador, incluyendo borrar.
    """

    # Campo de texto para el nuevo preso
    campo_nombre_preso = ft.TextField(
        label="Nombre del preso",
        bgcolor=COLORS['glass'],
        color=COLORS['text'],
        border_color=COLORS['glass']
    )

    # Botón para añadir
    boton_nuevo_preso = ft.ElevatedButton(
        "Nuevo preso",
        bgcolor=COLORS['accent'],
        color='#06203a',
        # Llama al handler del controlador pasándole el campo de texto
        on_click=lambda e: on_crear_preso_handler(e, campo_nombre_preso)
    )

    # Botón de refrescar manual
    boton_refrescar = ft.IconButton(
        icon=ft.Icons.REFRESH,
        on_click=on_refrescar_handler
    )

    prisoner_header = ft.Row([
        ft.Text("Registros de presos", size=12, weight=ft.FontWeight.BOLD, color=COLORS['text']),
        ft.Container(expand=True),
        boton_refrescar,
        boton_nuevo_preso
    ])

    # Lista de presos
    prisoner_list = ft.ListView(expand=True, spacing=5)

    if not lista_presos:
        prisoner_list.controls.append(
            ft.Text("No hay presos registrados.", color=COLORS['muted'])
        )
    else:
        for preso in lista_presos:
            # Creamos una fila: Texto a la izquierda, Botón borrar a la derecha
            prisoner_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        # Información del preso
                        ft.Column([
                            ft.Text(f"{preso['nombre']}", color=COLORS['text'], weight=ft.FontWeight.BOLD),
                            ft.Text(f"ID: {preso['id']} - {preso['delito']}", color=COLORS['muted'], size=10),
                        ], spacing=2, expand=True),

                        # Botón de borrar (Conectado al handler)
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=COLORS['bad'],
                            tooltip="Eliminar registro",
                            on_click=lambda e, pid=preso['id']: on_borrar_preso_handler(e, pid)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                    bgcolor=COLORS['room_bg'],
                    padding=10,
                    border_radius=5
                )
            )

    prisoner_list_container = ft.Container(
        content=prisoner_list,
        bgcolor=COLORS['glass'],
        height=150,  # Altura fija con scroll
        padding=10,
        border_radius=5
    )

    prisoner_card = ft.Container(
        bgcolor=COLORS['card'],
        border=ft.border.all(2, COLORS['glass']),
        expand=True,
        padding=12,
        content=ft.Column([
            prisoner_header,
            campo_nombre_preso,  # Input
            ft.Divider(height=5, color="transparent"),
            prisoner_list_container  # Lista
        ])
    )

    return prisoner_card