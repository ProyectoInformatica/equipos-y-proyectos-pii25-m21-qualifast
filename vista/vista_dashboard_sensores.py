import flet as ft
from vista.temas import COLORS, DEVICE_ICONS
import vista.vista_gestion_presos
import vista.vista_gestion_usuarios


# Definir crear_dashboard_view() que acepte rol, datos y handlers
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
        on_crear_usuario_click
):
    """
    Crea la estructura principal del Dashboard.
    Organiza la pantalla en dos columnas: Izquierda (Mapa/Gestión) y Derecha (Sensores/Log).
    """

    # --- TOPBAR (Barra Superior) ---
    title = ft.Text("Planta Comisaría", size=18, weight=ft.FontWeight.BOLD, color=COLORS['text'])
    legend = ft.Text("🟢 Puerta abierta 🔴 Puerta cerrada", size=10, color=COLORS['muted'])

    # Etiqueta de usuario y botón salir
    user_label = ft.Container(
        content=ft.Text(f"Usuario: {rol_usuario.upper()}", size=10, weight=ft.FontWeight.BOLD, color=COLORS['text']),
        bgcolor=COLORS['glass'],
        padding=10,
        border_radius=5
    )
    logout_btn = ft.ElevatedButton("Cerrar sesión", bgcolor=COLORS['bg'], color=COLORS['accent'],
                                   on_click=on_logout_click)

    topbar = ft.Row([
        ft.Row([title, legend]),
        ft.Container(expand=True),
        ft.Row([user_label, logout_btn])
    ])

    # --- MAPA (Placeholder - Columna Izquierda) ---
    # Aquí va la representación visual de la comisaría
    map_card = ft.Container(
        content=ft.Column([
            ft.Text("Mapa de la comisaría", color=COLORS['text'], size=16),
            ft.Text("(Visualización de habitaciones y puertas)", color=COLORS['muted'])
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=COLORS['card'],
        border=ft.border.all(2, COLORS['glass']),
        expand=True,
        padding=14,
        alignment=ft.alignment.center
    )

    # --- BOTTOM ROW (Gestión - Columna Izquierda) ---
    bottom_row = ft.Row(spacing=12, expand=False)

    # 1. Tarjeta de Presos (Reutilizamos la vista creada en el sprint anterior)
    bottom_row.controls.append(
        vista.vista_gestion_presos.crear_vista_presos(
            lista_presos=datos_presos,
            on_crear_preso_handler=on_crear_preso_click,
            on_refrescar_handler=on_refrescar_click
        )
    )

    # 2. Tarjeta de Usuarios (Solo visible para Comisario)
    bottom_row.controls.append(
        vista.vista_gestion_usuarios.crear_vista_usuarios(
            rol_actual=rol_usuario,
            lista_usuarios=datos_usuarios,
            on_crear_usuario_handler=on_crear_usuario_click
        )
    )

    # --- ENSAMBLAJE COLUMNA IZQUIERDA ---
    left_column = ft.Column(
        spacing=12,
        expand=True,
        controls=[topbar, map_card, bottom_row]
    )

    # --- PREPARACIÓN COLUMNA DERECHA (Placeholder para la siguiente tarea) ---
    # Esta columna contendrá el Log y los controles, que haremos en el siguiente paso.
    right_column = ft.Container(
        width=380,
        bgcolor=COLORS['card'],
        padding=14,
        expand=False,
        border=ft.border.all(1, COLORS['glass']),
        content=ft.Column([
            ft.Text("Panel Lateral", color=COLORS['muted']),
            ft.Text("(Aquí irá el Log en el siguiente paso)", size=10, color=COLORS['muted'])
        ])
    )

    # --- VISTA FINAL ---
    main_row = ft.Row([left_column, right_column], spacing=18, expand=True)

    return ft.View(
        "/dashboard",
        controls=[main_row],
        bgcolor=COLORS['bg'],
        padding=18
    )