import flet as ft
from modelo.cliente_chat import ClienteChat
from vista.temas import COLORS


def crear_vista_chat(page: ft.Page):
    usuario = page.session.get("user_name")

    lista_contactos_ui = ft.ListView(expand=True, spacing=10)
    lista_mensajes_ui = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    campo_texto = ft.TextField(hint_text="Escribe un mensaje...", expand=True, on_submit=lambda e: enviar_click(e))

    campo_nuevo_chat = ft.TextField(hint_text="Nombre de usuario...", height=40, expand=True, content_padding=10)

    def iniciar_nuevo_chat_click(e):
        nuevo_usuario = campo_nuevo_chat.value.strip()
        if nuevo_usuario:
            campo_nuevo_chat.value = ""
            cliente.cambiar_chat(nuevo_usuario)  # El on_update interno se encarga del refresco

    btn_nuevo_chat = ft.IconButton(ft.Icons.PERSON_ADD, on_click=iniciar_nuevo_chat_click, icon_color="#38bdf8")

    def actualizar_ui():
        if not page: return

        # === 1. ACTUALIZACIÓN ATÓMICA DE CONTACTOS ===
        nuevos_contactos = []
        for c in cliente.lista_contactos:
            datos = c.split(";")
            if len(datos) >= 6:
                nombre_contacto = datos[0].replace("@", "")
                no_leidos = int(datos[5].replace('"', ''))

                badge = ft.Container(
                    content=ft.Text(str(no_leidos), size=12, color="white", weight="bold"),
                    bgcolor="red", width=24, height=24, border_radius=12, alignment=ft.alignment.center
                ) if no_leidos > 0 else ft.Container(width=0, height=0)

                tile = ft.ListTile(
                    leading=ft.Icon(ft.Icons.PERSON),
                    title=ft.Text(nombre_contacto, color="white", expand=True, max_lines=1,
                                  overflow=ft.TextOverflow.ELLIPSIS),
                    trailing=badge,
                    on_click=lambda e, nom=nombre_contacto: cliente.cambiar_chat(nom)
                )
                nuevos_contactos.append(tile)

        lista_contactos_ui.controls = nuevos_contactos

        # === 2. ACTUALIZACIÓN ATÓMICA DE MENSAJES ===
        nuevos_mensajes = []

        if cliente.conversacion_actual and not cliente.mensajes_chat_actual:
            nuevos_mensajes.append(
                ft.Text(f"Chat con {cliente.conversacion_actual}", color="#9ca3af", italic=True, text_align="center")
            )

        mensajes_ordenados = sorted(cliente.mensajes_chat_actual,
                                    key=lambda x: x.split(";")[2] if len(x.split(";")) >= 6 else "")

        for m in mensajes_ordenados:
            datos = m.split(";")
            if len(datos) >= 6:
                emisor = datos[0].replace("@", "")
                texto = ";".join(datos[5:]).replace('"', '')  # Reconstruye de forma segura
                estado = datos[3]

                es_mio = (emisor == usuario)
                color_bg = "#38bdf8" if es_mio else "#374151"
                align = ft.MainAxisAlignment.END if es_mio else ft.MainAxisAlignment.START

                check = " ✓" if estado in ["ENVIADO", "RECIBIDO"] else (
                    " ✓✓" if estado == "ENTREGADO" else (" ✓✓ (Leído)" if estado == "LEIDO" else ""))

                burbuja = ft.Container(
                    content=ft.Text(texto + (check if es_mio else ""), color="white"),
                    bgcolor=color_bg, padding=10, border_radius=10, max_width=400
                )
                nuevos_mensajes.append(ft.Row([burbuja], alignment=align))

        lista_mensajes_ui.controls = nuevos_mensajes

        try:
            page.update()
        except:
            pass

    cliente = ClienteChat(usuario, actualizar_ui)

    def enviar_click(e):
        if campo_texto.value and cliente.conversacion_actual:
            cliente.enviar_mensaje(cliente.conversacion_actual, campo_texto.value)
            campo_texto.value = ""
            try:
                page.update()
            except:
                pass

    # --- LAYOUT ---
    panel_izquierdo = ft.Container(
        width=280,
        border=ft.border.only(right=ft.border.BorderSide(1, "#9ca3af")),
        padding=10,
        content=ft.Column([
            ft.Text("Contactos", size=20, weight="bold"),
            ft.Row([campo_nuevo_chat, btn_nuevo_chat]),
            ft.Divider(color="#9ca3af"),
            lista_contactos_ui
        ])
    )

    panel_derecho = ft.Container(
        expand=True, padding=10,
        content=ft.Column([
            ft.Text("Chat Interno", size=20, weight="bold"),
            lista_mensajes_ui,
            ft.Row([campo_texto, ft.IconButton(ft.Icons.SEND, on_click=enviar_click, icon_color="#38bdf8")])
        ])
    )

    return ft.Row([panel_izquierdo, panel_derecho], expand=True)