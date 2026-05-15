import flet as ft
import os
import cv2
import numpy as np

def leer_archivo_binario(ruta):
    if ruta and os.path.exists(ruta):
        try:
            with open(ruta, "rb") as f:
                file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
                img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            if img is not None:
                h, w = img.shape[:2]
                min_dim = min(h, w)
                start_x = (w // 2) - (min_dim // 2)
                start_y = (h // 2) - (min_dim // 2)
                cropped_img = img[start_y:start_y + min_dim, start_x:start_x + min_dim]
                img_resized = cv2.resize(cropped_img, (200, 200))
                ret, buffer = cv2.imencode('.jpg', img_resized, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if ret:
                    return buffer.tobytes()
        except Exception as e:
            print(f"[ERROR SISTEMA] Procesando imagen OpenCV: {e}")
        try:
            with open(ruta, "rb") as f:
                return f.read(1024 * 1024)
        except:
            pass
    return None

def get_nav_rail(page, current_route, on_logout_click):
    rol = page.session.get("user_rol")
    nombre = page.session.get("user_name")
    foto = page.session.get("user_foto")

    rutas = ["/dashboard", "/presos", "/chat"]
    if rol == "comisario": rutas.append("/usuarios")
    rutas.extend(["/consumo", "/historico", "/config"])

    destinations = [
        ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Panel"),
        ft.NavigationRailDestination(icon=ft.Icons.LOCK_OUTLINE, selected_icon=ft.Icons.LOCK, label="Presos"),
        ft.NavigationRailDestination(icon=ft.Icons.CHAT_OUTLINED, selected_icon=ft.Icons.CHAT, label="Chat"),
    ]
    if rol == "comisario":
        destinations.append(
            ft.NavigationRailDestination(icon=ft.Icons.PEOPLE_OUTLINE, selected_icon=ft.Icons.PEOPLE, label="Personal"))
    destinations.extend([
        ft.NavigationRailDestination(icon=ft.Icons.BOLT_OUTLINED, selected_icon=ft.Icons.BOLT, label="Consumo"),
        ft.NavigationRailDestination(icon=ft.Icons.HISTORY_OUTLINED, selected_icon=ft.Icons.HISTORY, label="Histórico"),
        ft.NavigationRailDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="Ajustes"),
    ])

    avatar = ft.Container(
        width=40, height=40, border_radius=20, bgcolor="#374151", alignment=ft.alignment.center,
        content=ft.Image(src_base64=foto, fit=ft.ImageFit.COVER, border_radius=20, width=40,
                         height=40) if foto else ft.Icon(ft.Icons.PERSON, color="white")
    )

    return ft.NavigationRail(
        selected_index=rutas.index(current_route) if current_route in rutas else 0,
        label_type=ft.NavigationRailLabelType.ALL,
        destinations=destinations,
        on_change=lambda e: page.go(rutas[e.control.selected_index]),
        bgcolor="#1f2937",
        indicator_color="#38bdf8",
        leading=ft.Column([
            ft.Container(padding=10, content=avatar),
            ft.Text(nombre, size=10, weight="bold", color="white", text_align="center"),
            ft.Text(rol, size=8, color="#38bdf8", text_align="center"),
            ft.Divider(color="#374151")
        ], horizontal_alignment="center", spacing=2),
        trailing=ft.IconButton(ft.Icons.LOGOUT, icon_color="#ef4444", on_click=on_logout_click)
    )