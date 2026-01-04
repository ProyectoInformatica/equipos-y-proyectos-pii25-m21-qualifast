import flet as ft
from vista.temas import COLORS
import os
import csv
import json
import subprocess
import platform


# --- 1. LÓGICA DE EXPORTACIÓN (CSV) ---
def ejecutar_exportacion_directa(archivo_json, ruta_destino):
    try:
        if not os.path.exists(archivo_json):
            return False, f"No se encuentra: {archivo_json}"

        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)

        if not datos:
            return False, "El archivo JSON está vacío."

        # Adaptar diccionarios (ej: actuadores) a lista
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


# --- 2. SELECTOR DE ARCHIVOS NATIVO (MAC + WINDOWS) ---
def obtener_ruta_guardado_universal(nombre_defecto):
    """
    Abre la ventana de 'Guardar como' usando los comandos nativos
    de cada sistema operativo para evitar errores de librerías.
    """
    sistema = platform.system()
    ruta_final = None

    try:
        if sistema == "Darwin":  # macOS
            script = f"""osascript -e 'POSIX path of (choose file name default name "{nombre_defecto}" with prompt "Guardar CSV como:")'"""
            ruta_final = subprocess.check_output(script, shell=True).decode('utf-8').strip()

        elif sistema == "Windows":  # Windows
            # Comando de PowerShell para abrir diálogo de guardado
            cmd = f"""powershell -Command "Add-Type -AssemblyName System.Windows.Forms; $f = New-Object System.Windows.Forms.SaveFileDialog; $f.FileName='{nombre_defecto}'; $f.Filter='CSV (*.csv)|*.csv'; if ($f.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {{ Write-Host $f.FileName }}" """
            ruta_final = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

        else:
            # Linux u otros (Fallback simple por si acaso)
            return os.path.join(os.getcwd(), nombre_defecto)

    except subprocess.CalledProcessError:
        return None  # Usuario canceló
    except Exception as e:
        print(f"Error nativo SO: {e}")
        return None

    return ruta_final


# --- 3. VISTA DE CONFIGURACIÓN ---
def crear_vista_configuracion(config_actual, on_guardar_click, on_volver_dashboard):
    # Función del botón
    def iniciar_descarga(e, ruta_json):
        nombre_default = os.path.basename(ruta_json).replace(".json", ".csv")

        # Feedback de carga
        e.page.snack_bar = ft.SnackBar(ft.Text("Abriendo ventana de guardado..."), duration=1000)
        e.page.snack_bar.open = True
        e.page.update()

        # 1. Obtener ruta del SO
        ruta_destino = obtener_ruta_guardado_universal(nombre_default)

        # 2. Exportar si hay ruta
        if ruta_destino:
            exito, msj = ejecutar_exportacion_directa(ruta_json, ruta_destino)

            color = COLORS['good'] if exito else "red"
            e.page.snack_bar = ft.SnackBar(ft.Text(msj), bgcolor=color)
            e.page.snack_bar.open = True
            e.page.update()

    # --- UI GRÁFICA ---
    val_temp = float(config_actual.get("temp_max", 28.0))
    val_luz = float(config_actual.get("luz_min", 400.0))

    slider_temp = ft.Slider(
        min=15, max=40, divisions=25, value=val_temp,
        label="{value}°C", active_color=COLORS['accent']
    )
    slider_luz = ft.Slider(
        min=0, max=1000, divisions=100, value=val_luz,
        label="{value} Lux", active_color=COLORS['accent']
    )

    seccion_exportar = ft.Container(
        padding=10,
        content=ft.Column([
            ft.Text("📊 Exportar Datos a CSV", weight="bold", color=COLORS['accent']),
            ft.Row([
                ft.Column([
                    ft.IconButton(ft.Icons.PEOPLE, on_click=lambda e: iniciar_descarga(e, "modelo/presos.json"),
                                  tooltip="Presos"),
                    ft.Text("Presos", size=10)
                ], horizontal_alignment="center"),

                ft.Column([
                    ft.IconButton(ft.Icons.MEETING_ROOM,
                                  on_click=lambda e: iniciar_descarga(e, "modelo/puertas_log.json"), tooltip="Puertas"),
                    ft.Text("Puertas", size=10)
                ], horizontal_alignment="center"),

                ft.Column([
                    ft.IconButton(ft.Icons.SENSORS, on_click=lambda e: iniciar_descarga(e, "modelo/sensores_log.json"),
                                  tooltip="Sensores"),
                    ft.Text("Sensores", size=10)
                ], horizontal_alignment="center"),

                ft.Column([
                    ft.IconButton(ft.Icons.TOGGLE_ON,
                                  on_click=lambda e: iniciar_descarga(e, "modelo/actuadores_estado.json"),
                                  tooltip="Estados"),
                    ft.Text("Estado", size=10)
                ], horizontal_alignment="center"),

            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    contenido = ft.Container(
        width=500, padding=30, bgcolor=COLORS['card'], border_radius=15,
        border=ft.border.all(1, COLORS['glass']),
        content=ft.Column([
            ft.Text("⚙️ Panel de Control", size=22, weight="bold"),
            ft.Divider(),
            ft.Text("Umbral Temperatura"), slider_temp,
            ft.Text("Umbral Luz"), slider_luz,
            ft.Divider(),
            seccion_exportar,
            ft.Divider(),
            ft.Row([
                ft.ElevatedButton("Volver", on_click=on_volver_dashboard),
                ft.ElevatedButton("Guardar Config", bgcolor=COLORS['good'], color="white",
                                  on_click=lambda e: on_guardar_click(e, {
                                      "temp_max": slider_temp.value,
                                      "luz_min": slider_luz.value
                                  }))
            ], alignment=ft.MainAxisAlignment.END)
        ])
    )

    return ft.View(
        "/config",
        bgcolor=COLORS['bg'],
        controls=[ft.Container(content=contenido, expand=True, alignment=ft.alignment.center)]
    )