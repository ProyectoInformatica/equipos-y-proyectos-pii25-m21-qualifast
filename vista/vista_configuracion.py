import flet as ft
from vista.temas import COLORS


def crear_vista_configuracion(config_actual, on_guardar_click, on_volver_dashboard):
    # Valores actuales
    val_temp = float(config_actual.get("temp_max", 28.0))
    val_luz = float(config_actual.get("luz_min", 400.0))

    # Controles Slider
    slider_temp = ft.Slider(min=15, max=40, divisions=25, value=val_temp, label="{value} °C",
                            active_color=COLORS['accent'])
    txt_temp = ft.Text(f"Encender ventilador si T > {val_temp} °C", color=COLORS['text'])

    def on_change_temp(e):
        txt_temp.value = f"Encender ventilador si T > {int(e.control.value)} °C"
        txt_temp.update()

    slider_temp.on_change = on_change_temp

    slider_luz = ft.Slider(min=0, max=1000, divisions=100, value=val_luz, label="{value} Lux",
                           active_color=COLORS['accent'])
    txt_luz = ft.Text(f"Encender luces si Luz < {val_luz} Lux", color=COLORS['text'])

    def on_change_luz(e):
        txt_luz.value = f"Encender luces si Luz < {int(e.control.value)} Lux"
        txt_luz.update()

    slider_luz.on_change = on_change_luz

    # Botón Guardar
    def guardar_accion(e):
        nuevos_datos = {
            "temp_max": slider_temp.value,
            "luz_min": slider_luz.value
        }
        on_guardar_click(e, nuevos_datos)

    # Estructura
    contenido = ft.Container(
        width=500,
        padding=30,
        bgcolor=COLORS['card'],
        border=ft.border.all(1, COLORS['glass']),
        border_radius=10,
        content=ft.Column([
            ft.Text("⚙️ Configuración de Automatización", size=20, weight="bold", color=COLORS['accent']),
            ft.Divider(color=COLORS['glass']),

            ft.Text("Control Ambiental (Ventilación)", weight="bold", color=COLORS['text']),
            ft.Text("Umbral de temperatura máxima:", size=12, color=COLORS['muted']),
            slider_temp,
            txt_temp,
            ft.Container(height=20),

            ft.Text("Control Iluminación (LDR)", weight="bold", color=COLORS['text']),
            ft.Text("Umbral de luz mínima (Oscuridad):", size=12, color=COLORS['muted']),
            slider_luz,
            txt_luz,
            ft.Container(height=30),

            ft.Row([
                ft.ElevatedButton("Cancelar", on_click=on_volver_dashboard, bgcolor=COLORS['bg'],
                                  color=COLORS['muted']),
                ft.ElevatedButton("Guardar Configuración", icon=ft.Icons.SAVE, bgcolor=COLORS['good'], color="white",
                                  on_click=guardar_accion)
            ], alignment=ft.MainAxisAlignment.END)

        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    return ft.View(
        "/config",
        bgcolor=COLORS['bg'],
        appbar=ft.AppBar(
            title=ft.Text("Configuración del Sistema"),
            bgcolor=COLORS['card'],
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=on_volver_dashboard)
        ),
        controls=[ft.Container(content=contenido, alignment=ft.alignment.center, expand=True)]
    )