import flet as ft
from vista.temas import COLORS


def crear_vista_configuracion(config_actual, on_guardar_click, on_volver_dashboard):
    # Valores iniciales
    val_temp = float(config_actual.get("temp_max", 28.0))
    val_luz = float(config_actual.get("luz_min", 400.0))

    # --- CONTROL DE TEMPERATURA (Texto Normal) ---
    txt_temp_info = ft.Text(
        f"Encender ventilador si T > {val_temp:.1f} °C",
        color=COLORS['text'],
        size=12
        # italic=True  <-- ELIMINADO
    )

    def on_change_temp(e):
        txt_temp_info.value = f"Encender ventilador si T > {float(e.control.value):.1f} °C"
        txt_temp_info.update()

    slider_temp = ft.Slider(
        min=15, max=40, divisions=25, value=val_temp,
        label="{value}°C", active_color=COLORS['accent'],
        on_change=on_change_temp
    )

    # --- CONTROL DE LUZ (Texto Normal) ---
    txt_luz_info = ft.Text(
        f"Encender luces si Luz < {int(val_luz)} Lux",
        color=COLORS['text'],
        size=12
        # italic=True  <-- ELIMINADO
    )

    def on_change_luz(e):
        txt_luz_info.value = f"Encender luces si Luz < {int(e.control.value)} Lux"
        txt_luz_info.update()

    slider_luz = ft.Slider(
        min=0, max=1000, divisions=100, value=val_luz,
        label="{value} Lux", active_color=COLORS['accent'],
        on_change=on_change_luz
    )

    # --- ESTRUCTURA VISUAL ---
    contenido = ft.Container(
        width=500, padding=30, bgcolor=COLORS['card'], border_radius=15,
        border=ft.border.all(1, COLORS['glass']),
        content=ft.Column([
            ft.Text("⚙️ Configuración de Automatización", size=22, weight="bold", color=COLORS['accent']),
            ft.Divider(color=COLORS['glass']),

            # Bloque Temperatura
            ft.Text("Control Ambiental (Ventilación)", weight="bold"),
            slider_temp,
            ft.Container(content=txt_temp_info, alignment=ft.alignment.center),

            ft.Divider(height=20, color="transparent"),

            # Bloque Luz
            ft.Text("Control Iluminación (Luces)", weight="bold"),
            slider_luz,
            ft.Container(content=txt_luz_info, alignment=ft.alignment.center),

            ft.Divider(color=COLORS['glass'], height=30),

            # Botones
            ft.Row([
                ft.ElevatedButton("Volver", on_click=on_volver_dashboard, bgcolor=COLORS['bg']),
                ft.ElevatedButton("Guardar Configuración", bgcolor=COLORS['good'], color="white",
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