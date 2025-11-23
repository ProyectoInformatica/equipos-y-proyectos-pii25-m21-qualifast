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
        on_crear_usuario_click,
        on_borrar_preso_click,
        on_ver_camaras_click  # <--- NUEVO ARGUMENTO
):
    """
    Crea la estructura principal del Dashboard.
    """

    # --- TOPBAR (Barra Superior) ---
    title = ft.Text("Planta Comisaría", size=18, weight=ft.FontWeight.BOLD, color=COLORS['text'])
    legend = ft.Text("🟢 Puerta abierta 🔴 Puerta cerrada", size=10, color=COLORS['muted'])

    # Botón para ir a cámaras (NUEVO)
    boton_camaras = ft.ElevatedButton(
        "Ver Cámaras",
        icon=ft.Icons.CAMERA_ALT,
        bgcolor=COLORS['glass'],
        color=COLORS['text'],
        on_click=on_ver_camaras_click
    )

    user_label = ft.Container(
        content=ft.Text(f"Usuario: {rol_usuario.upper()}", size=10, weight=ft.FontWeight.BOLD, color=COLORS['text']),
        bgcolor=COLORS['glass'],
        padding=10,
        border_radius=5
    )
    logout_btn = ft.ElevatedButton("Cerrar sesión", bgcolor=COLORS['bg'], color=COLORS['accent'],
                                   on_click=on_logout_click)

    topbar = ft.Row([
        ft.Column([title, legend], spacing=2),
        ft.Container(expand=True),
        boton_camaras,  # Añadido aquí
        ft.Container(width=10),
        user_label,
        logout_btn
    ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    # --- MAPA ---
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

    # --- BOTTOM ROW (Gestión) ---
    bottom_row = ft.Row(spacing=12, expand=False)

    # 1. Tarjeta de Presos
    bottom_row.controls.append(
        vista.vista_gestion_presos.crear_vista_presos(
            lista_presos=datos_presos,
            on_crear_preso_handler=on_crear_preso_click,
            on_refrescar_handler=on_refrescar_click,
            on_borrar_preso_handler=on_borrar_preso_click
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

    # --- PANEL DERECHO (Log de Sensores) ---
    right_content = ft.Column(spacing=12, expand=True)

    right_content.controls.append(
        ft.Text("Panel de Control y Sensores", size=12, weight=ft.FontWeight.BOLD, color=COLORS['text'])
    )

    right_content.controls.append(
        ft.Container(
            content=ft.Text("Controles Actuadores", size=10, color=COLORS['muted']),
            padding=5, bgcolor=COLORS['glass'], border_radius=5
        )
    )

    right_content.controls.append(ft.Divider(height=10, color=COLORS['muted']))

    # Título del Log
    right_content.controls.append(
        ft.Text("Log de Sensores (Últimos registros)", size=10, color=COLORS['muted'])
    )

    # Lista del log
    log_list = ft.ListView(expand=True, spacing=5, padding=5)

    if not datos_sensores:
        log_list.controls.append(ft.Text("Esperando datos...", color=COLORS['muted'], size=10))
    else:
        for log in reversed(datos_sensores[-15:]):
            icono = "📝"
            # Mapeo simple de iconos según el sensor (asegurándose que existen en DEVICE_ICONS)
            key_sensor = log['sensor'].lower().replace("-", "")  # ej: mq-2 -> mq2
            if log['sensor'] == 'DHT11': key_sensor = 'dht'

            icono = DEVICE_ICONS.get(key_sensor, "📝")

            log_item = ft.Container(
                content=ft.Row([
                    ft.Text(f"{log['timestamp'].split(' ')[1]}", size=9, color=COLORS['muted']),
                    ft.Text(icono, size=12),
                    ft.Text(f"{log['sensor']}:", size=10, weight=ft.FontWeight.BOLD, color=COLORS['accent']),
                    ft.Text(f"{log['valor']}", size=10, color=COLORS['text']),
                ], spacing=5),
                bgcolor=COLORS['glass'],
                padding=5,
                border_radius=4
            )
            log_list.controls.append(log_item)

    right_content.controls.append(ft.Container(content=log_list, expand=True))

    right_column = ft.Container(
        width=380,
        bgcolor=COLORS['card'],
        padding=14,
        expand=False,
        content=right_content,
        border=ft.border.all(1, COLORS['glass'])
    )

    # --- VISTA FINAL ---
    main_row = ft.Row([left_column, right_column], spacing=18, expand=True)

    return ft.View(
        "/dashboard",
        controls=[main_row],
        bgcolor=COLORS['bg'],
        padding=18
    )