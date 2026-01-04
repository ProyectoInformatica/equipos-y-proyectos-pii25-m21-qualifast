import flet as ft
from vista.temas import COLORS, DEVICE_ICONS
import os
import csv
import json
import subprocess
import platform

# --- RUTAS DE ARCHIVOS (Definidas aquí para evitar errores de importación) ---
FILE_PRESOS = "modelo/presos.json"
FILE_PUERTAS = "modelo/puertas_log.json"
FILE_SENSORES = "modelo/sensores_log.json"
FILE_ACTUADORES = "modelo/actuadores_estado.json"

# Configuración de paginación
ITEMS_POR_PAGINA = 50


# =============================================================================================
#  LÓGICA DE EXPORTACIÓN
# =============================================================================================
def ejecutar_exportacion_directa(archivo_json, ruta_destino):
    try:
        if not os.path.exists(archivo_json):
            return False, f"No se encuentra: {archivo_json}"

        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)

        if not datos:
            return False, "El archivo JSON está vacío."

        # Adaptar diccionarios a lista
        if isinstance(datos, dict):
            datos_preparados = []
            for k, v in datos.items():
                if isinstance(v, dict):
                    fila = {"id": k}
                    fila.update(v)
                    datos_preparados.append(fila)
                else:
                    datos_preparados.append({"parametro": k, "valor": v})
            datos = datos_preparados

        if isinstance(datos, list) and len(datos) > 0:
            columnas = datos[0].keys()
            with open(ruta_destino, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=columnas)
                writer.writeheader()
                writer.writerows(datos)
            return True, f"Guardado correctamente"

        return False, "Formato de datos no compatible."
    except Exception as e:
        return False, str(e)


def obtener_ruta_guardado_universal(nombre_defecto):
    """
    Abre la ventana de 'Guardar como' forzando que aparezca AL FRENTE (TopMost).
    """
    sistema = platform.system()
    try:
        if sistema == "Darwin":  # macOS
            script = f"""osascript -e 'POSIX path of (choose file name default name "{nombre_defecto}" with prompt "Guardar CSV como:")'"""
            return subprocess.check_output(script, shell=True).decode('utf-8').strip()

        elif sistema == "Windows":  # Windows
            cmd = f"""powershell -Command "Add-Type -AssemblyName System.Windows.Forms; $form = New-Object System.Windows.Forms.Form; $form.TopMost = $true; $form.StartPosition = 'Manual'; $form.ShowInTaskbar = $false; $form.Opacity = 0; $form.Show(); $f = New-Object System.Windows.Forms.SaveFileDialog; $f.FileName='{nombre_defecto}'; $f.Filter='CSV (*.csv)|*.csv'; $result = $f.ShowDialog($form); $form.Close(); if ($result -eq [System.Windows.Forms.DialogResult]::OK) {{ Write-Host $f.FileName }}" """
            return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        else:
            return None
    except:
        return None


# =============================================================================================
#  VISTA PRINCIPAL
# =============================================================================================
def crear_vista_historico(datos_promedio_sensores, datos_log_actuadores, on_volver_dashboard):
    # --- Función del botón de exportar ---
    def iniciar_descarga(e, ruta_json):
        nombre_file = os.path.basename(ruta_json).replace(".json", ".csv")

        # Feedback visual
        e.page.snack_bar = ft.SnackBar(ft.Text("Abriendo ventana de guardado..."), duration=1000)
        e.page.snack_bar.open = True
        e.page.update()

        # Obtener ruta (Bloqueante hasta que el usuario elija)
        ruta_destino = obtener_ruta_guardado_universal(nombre_file)

        if ruta_destino:
            exito, msj = ejecutar_exportacion_directa(ruta_json, ruta_destino)
            col = COLORS['good'] if exito else "red"
            e.page.snack_bar = ft.SnackBar(ft.Text(msj), bgcolor=col)
            e.page.snack_bar.open = True
            e.page.update()

    # --- Botones de Exportación (A la derecha) ---
    botones_exportar = ft.Row([
        ft.Text("Exportar a CSV:", size=12, color=COLORS['muted'], weight="bold"),
        ft.IconButton(ft.Icons.PEOPLE, tooltip="Presos", icon_size=20,
                      on_click=lambda e: iniciar_descarga(e, FILE_PRESOS)),
        ft.IconButton(ft.Icons.MEETING_ROOM, tooltip="Log Puertas", icon_size=20,
                      on_click=lambda e: iniciar_descarga(e, FILE_PUERTAS)),
        ft.IconButton(ft.Icons.SENSORS, tooltip="Log Sensores", icon_size=20,
                      on_click=lambda e: iniciar_descarga(e, FILE_SENSORES)),
        ft.IconButton(ft.Icons.TOGGLE_ON, tooltip="Estado Actuadores", icon_size=20,
                      on_click=lambda e: iniciar_descarga(e, FILE_ACTUADORES)),
    ], spacing=2)

    tabs_list = []

    # =============================================================================================
    # 1. PESTAÑA PUERTAS
    # =============================================================================================
    logs_puertas = [log for log in datos_log_actuadores if "door" in log['id']]
    puertas_ids = ["door-1", "door-2", "door-3", "door-4"]
    columnas_puertas_ui = []

    for pid in puertas_ids:
        logs_esta_puerta = list(reversed([p for p in logs_puertas if p['id'] == pid]))
        label_puerta = logs_esta_puerta[0]['label'] if logs_esta_puerta else pid.replace("door-", "P")

        lv_puerta = ft.ListView(expand=True, spacing=10, padding=5)
        btn_cargar = ft.TextButton("⬇️ Cargar más", visible=False)
        estado_pag = {"mostrados": 0, "total": len(logs_esta_puerta)}

        def cargar_mas_puerta(e, lv=lv_puerta, btn=btn_cargar, logs=logs_esta_puerta, st=estado_pag):
            inicio = st["mostrados"]
            fin = inicio + ITEMS_POR_PAGINA
            chunk = logs[inicio:fin]

            for evento in chunk:
                color_estado = COLORS['good'] if evento['accion'] == "abierta" else COLORS['bad']
                icon_estado = ft.Icons.LOCK_OPEN if evento['accion'] == "abierta" else ft.Icons.LOCK_OUTLINE

                card = ft.Container(
                    bgcolor=COLORS['glass'], padding=8, border_radius=5,
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(icon_estado, color=color_estado, size=14),
                            ft.Text(evento['accion'].upper(), color=color_estado, weight="bold", size=11)
                        ]),
                        ft.Text(f"👤 {evento.get('usuario', 'sistema')}", size=10, color=COLORS['text']),
                        ft.Text(f"🕒 {evento['timestamp']}", size=9, color=COLORS['muted']),
                    ], spacing=2)
                )
                lv.controls.append(card)

            st["mostrados"] += len(chunk)
            btn.visible = (st["mostrados"] < st["total"])
            if lv.page: lv.update()
            if btn.page: btn.update()

        btn_cargar.on_click = cargar_mas_puerta

        if not logs_esta_puerta:
            lv_puerta.controls.append(ft.Text("Sin actividad", size=10, color=COLORS['muted'], italic=True))
        else:
            cargar_mas_puerta(None)

        col_container = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text(f"PUERTA {label_puerta}", weight="bold", color=COLORS['accent'], size=12),
                    bgcolor=COLORS['room_bg'], padding=5, border_radius=5, alignment=ft.alignment.center
                ),
                lv_puerta,
                btn_cargar
            ], expand=True),
            expand=1,
            bgcolor=COLORS['card'], padding=5, border=ft.border.all(1, COLORS['glass']), border_radius=8
        )
        columnas_puertas_ui.append(col_container)

    tab_puertas = ft.Tab(
        text="🚪 Puertas",
        content=ft.Container(
            content=ft.Row(controls=columnas_puertas_ui, expand=True, spacing=5),
            padding=10
        )
    )
    tabs_list.append(tab_puertas)

    # =============================================================================================
    # 2. PESTAÑA ACTUADORES
    # =============================================================================================
    logs_otros = [log for log in datos_log_actuadores if "door" not in log['id']]
    logs_otros = list(reversed(logs_otros))

    tabla_act = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Fecha / Hora", weight="bold")),
            ft.DataColumn(ft.Text("Dispositivo", weight="bold")),
            ft.DataColumn(ft.Text("Estado", weight="bold")),
            ft.DataColumn(ft.Text("Usuario", weight="bold")),
        ],
        rows=[],
        border=ft.border.all(1, COLORS['glass']),
        heading_row_color=COLORS['glass'],
        column_spacing=20
    )

    btn_cargar_act = ft.ElevatedButton("⬇️ Cargar más", visible=False, bgcolor=COLORS['glass'], color=COLORS['text'])
    estado_pag_act = {"mostrados": 0, "total": len(logs_otros)}

    def cargar_mas_actuadores(e):
        inicio = estado_pag_act["mostrados"]
        fin = inicio + ITEMS_POR_PAGINA
        chunk = logs_otros[inicio:fin]

        for log in chunk:
            icon_str = ft.Icons.SETTINGS
            if "led" in log['id']:
                icon_str = ft.Icons.LIGHTBULB
            elif "fan" in log['id']:
                icon_str = ft.Icons.AIR
            color_st = COLORS['good'] if log['accion'] == "on" else COLORS['muted']

            row = ft.DataRow(cells=[
                ft.DataCell(ft.Text(log['timestamp'], size=12, color=COLORS['text'])),
                ft.DataCell(ft.Row([
                    ft.Icon(icon_str, size=16, color=COLORS['accent']),
                    ft.Text(log.get('label', log['id']), size=12, color=COLORS['text'])
                ])),
                ft.DataCell(ft.Container(
                    content=ft.Text(log['accion'].upper(), size=10, weight="bold", color="#000000"),
                    bgcolor=color_st, padding=5, border_radius=5
                )),
                ft.DataCell(ft.Text(f"👤 {log.get('usuario', 'sistema')}", size=12, color=COLORS['muted'])),
            ])
            tabla_act.rows.append(row)

        estado_pag_act["mostrados"] += len(chunk)
        btn_cargar_act.visible = (estado_pag_act["mostrados"] < estado_pag_act["total"])
        if tabla_act.page: tabla_act.update()
        if btn_cargar_act.page: btn_cargar_act.update()

    btn_cargar_act.on_click = cargar_mas_actuadores

    if not logs_otros:
        tabla_act.rows.append(ft.DataRow(
            cells=[ft.DataCell(ft.Text("Sin registros", italic=True)), ft.DataCell(ft.Text("")),
                   ft.DataCell(ft.Text("")), ft.DataCell(ft.Text(""))]))
    else:
        cargar_mas_actuadores(None)

    tab_actuadores = ft.Tab(
        text="⚙️ Historial Actuadores",
        content=ft.Container(
            content=ft.Column([
                ft.Text("Registro de actividad (Luces, Ventilación)", size=16, weight="bold", color=COLORS['text']),
                ft.Column([tabla_act], scroll=ft.ScrollMode.AUTO, expand=True),
                ft.Row([btn_cargar_act], alignment=ft.MainAxisAlignment.CENTER)
            ], expand=True),
            padding=10
        )
    )
    tabs_list.append(tab_actuadores)

    # =============================================================================================
    # 3. PESTAÑA SENSORES
    # =============================================================================================
    controles_sensores = []

    if not datos_promedio_sensores:
        controles_sensores.append(
            ft.Text("No hay suficientes datos para calcular promedios.", italic=True, color=COLORS['muted']))
    else:
        for nombre_sensor, datos_lista in datos_promedio_sensores.items():
            datos_lista = list(reversed(datos_lista))
            t_sensor = ft.DataTable(
                columns=[ft.DataColumn(ft.Text("Hora")), ft.DataColumn(ft.Text("Promedio"))],
                rows=[], border=ft.border.all(1, COLORS['glass']), heading_row_color=COLORS['glass']
            )

            btn_c = ft.TextButton("Cargar más", visible=False)
            st_sen = {"mostrados": 0, "total": len(datos_lista), "datos": datos_lista, "tabla": t_sensor, "btn": btn_c}

            def cargar_mas_sensor(e, st=st_sen):
                inicio = st["mostrados"]
                fin = inicio + ITEMS_POR_PAGINA
                chunk = st["datos"][inicio:fin]
                for d in chunk:
                    st["tabla"].rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(d['hora'], color=COLORS['text'])),
                        ft.DataCell(ft.Text(d['valor'], color=COLORS['accent'], weight="bold")),
                    ]))
                st["mostrados"] += len(chunk)
                st["btn"].visible = (st["mostrados"] < st["total"])
                if st["tabla"].page: st["tabla"].update()
                if st["btn"].page: st["btn"].update()

            st_sen["btn"].on_click = cargar_mas_sensor
            cargar_mas_sensor(None)

            icon_s = "📝"
            if "Temp" in nombre_sensor:
                icon_s = DEVICE_ICONS['dht11']
            elif "Humo" in nombre_sensor:
                icon_s = DEVICE_ICONS['mq-2']
            elif "Aire" in nombre_sensor:
                icon_s = DEVICE_ICONS['mq-135']
            elif "Luz" in nombre_sensor:
                icon_s = DEVICE_ICONS['ldr']

            card_sensor = ft.Container(
                bgcolor=COLORS['card'], padding=15, border_radius=10, border=ft.border.all(1, COLORS['glass']),
                content=ft.Column([
                    ft.Text(f"{icon_s} {nombre_sensor}", size=16, weight="bold", color=COLORS['accent']),
                    ft.Divider(color=COLORS['glass']),
                    ft.Column([t_sensor], scroll=ft.ScrollMode.AUTO, expand=True),
                    btn_c
                ], expand=True)
            )
            controles_sensores.append(card_sensor)

    tab_sensores = ft.Tab(
        text="📈 Sensores (Medias)",
        content=ft.Container(
            content=ft.GridView(
                controls=controles_sensores,
                runs_count=2, max_extent=400, child_aspect_ratio=0.8, spacing=10, run_spacing=10,
            ),
            padding=20
        )
    )
    tabs_list.append(tab_sensores)

    # --- Estructura Final ---
    tbs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=tabs_list,
        expand=True,
        divider_color=COLORS['glass'],
        indicator_color=COLORS['accent'],
        label_color=COLORS['accent'],
        unselected_label_color=COLORS['muted'],
    )

    # Header: Título y Botones de Exportar alineados a los extremos
    header = ft.Row([
        ft.Text("Registros del Sistema", size=20, weight="bold"),
        botones_exportar
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    return ft.View(
        "/historico",
        bgcolor=COLORS['bg'],
        appbar=ft.AppBar(
            title=ft.Text("Histórico y Logs"),
            bgcolor=COLORS['card'],
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=on_volver_dashboard)
        ),
        controls=[
            ft.Container(
                content=ft.Column([
                    header,
                    ft.Divider(color=COLORS['glass']),
                    tbs
                ], expand=True),
                padding=20, expand=True
            )
        ]
    )