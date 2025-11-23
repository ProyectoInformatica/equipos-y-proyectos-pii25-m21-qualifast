import flet as ft
from vista.temas import COLORS, DEVICE_ICONS
import vista.vista_gestion_presos
import vista.vista_gestion_usuarios


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

    # 1. Tarjeta de Presos
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

    # ---------------------------------------------------------
    # TAREA: IMPLEMENTAR PANEL DE LOG (PANEL DERECHO)
    # ---------------------------------------------------------

    # [Subtarea] Diseñar la right_column (Estructura interna)
    right_content = ft.Column(spacing=12, expand=True)

    # Cabecera del panel
    right_content.controls.append(
        ft.Text("Panel de Control y Sensores", size=12, weight=ft.FontWeight.BOLD, color=COLORS['text'])
    )

    # Placeholder para controles 
    right_content.controls.append(
        ft.Container(
            content=ft.Text("Controles (Sprint 3)", size=10, color=COLORS['muted'], italic=True),
            padding=5, bgcolor=COLORS['glass'], border_radius=5
        )
    )

    right_content.controls.append(ft.Divider(height=10, color=COLORS['muted']))

    # Título del Log
    right_content.controls.append(
        ft.Text("Log de Sensores (Últimos registros)", size=10, color=COLORS['muted'])
    )

    # [Subtarea] Añadir ft.ListView para el log de sensores
    log_list = ft.ListView(expand=True, spacing=5, padding=5)

    if not datos_sensores:
        log_list.controls.append(ft.Text("Esperando datos...", color=COLORS['muted'], size=10))
    else:
        # [Subtarea] Iterar sobre datos_sensores (en reverso)
        # Mostramos los últimos 15 para no saturar la vista
        for log in reversed(datos_sensores[-15:]):

            # Icono según el tipo de sensor
            icono = "📝"
            if log['sensor'] == "DHT11":
                icono = DEVICE_ICONS['dht']
            elif log['sensor'] == "MQ-2":
                icono = DEVICE_ICONS['mq2']
            elif log['sensor'] == "MQ-135":
                icono = DEVICE_ICONS['mq135']
            elif log['sensor'] == "LDR":
                icono = DEVICE_ICONS['ldr']

            # Diseño de cada fila del log
            log_item = ft.Container(
                content=ft.Row([
                    ft.Text(f"{log['timestamp'].split(' ')[1]}", size=9, color=COLORS['muted']),  # Hora
                    ft.Text(icono, size=12),
                    ft.Text(f"{log['sensor']}:", size=10, weight=ft.FontWeight.BOLD, color=COLORS['accent']),
                    ft.Text(f"{log['valor']}", size=10, color=COLORS['text']),
                ], spacing=5),
                bgcolor=COLORS['glass'],
                padding=5,
                border_radius=4
            )
            log_list.controls.append(log_item)

    # Añadimos la lista al contenido derecho
    right_content.controls.append(ft.Container(content=log_list, expand=True))

    # [Subtarea] Diseñar la right_column (Contenedor Principal)
    right_column = ft.Container(
        width=380,
        bgcolor=COLORS['card'],
        padding=14,
        expand=False,  # Fijo a 380px
        content=right_content,
        border=ft.border.all(1, COLORS['glass'])
    )

    # --- ENSAMBLAJE FINAL ---
    main_row = ft.Row([left_column, right_column], spacing=18, expand=True)

    return ft.View(
        "/dashboard",
        controls=[main_row],
        bgcolor=COLORS['bg'],
        padding=18
    )