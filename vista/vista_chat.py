import flet as ft
from modelo.cliente_chat import ClienteChat
from vista.temas import COLORS

def crear_vista_chat(page: ft.Page):
    usuario = page.session.get("user_name")

    # Referencias a controles
    lista_contactos_ui = ft.ListView(expand=True, spacing=10)
    lista_mensajes_ui = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    campo_texto = ft.TextField(hint_text="Escribe un mensaje...", expand=True, on_submit=lambda e: enviar_click(e))

    # Controles para iniciar un chat con alguien nuevo
    campo_nuevo_chat = ft.TextField(hint_text="Nombre de usuario...", height=40, expand=True, content_padding=10)

    def iniciar_nuevo_chat_click(e):
        nuevo_usuario = campo_nuevo_chat.value.strip()
        if nuevo_usuario:
            cliente.cambiar_chat(nuevo_usuario)
            campo_nuevo_chat.value = ""
            lista_mensajes_ui.controls.clear()
            lista_mensajes_ui.controls.append(
                ft.Text(f"Has iniciado una conversación con {nuevo_usuario}", color="grey", italic=True, text_align="center")
            )
            page.update()

    btn_nuevo_chat = ft.IconButton(ft.Icons.PERSON_ADD, on_click=iniciar_nuevo_chat_click, icon_color=COLORS['accent'])

    def actualizar_ui():
        if not page: return

        # 1. Actualizar Contactos
        lista_contactos_ui.controls.clear()
        for c in cliente.lista_contactos:
            datos = c.split(";")
            if len(datos) >= 6:
                nombre_contacto = datos[0].replace("@", "")
                no_leidos = int(datos[5].replace('"', ''))

                # Círculo perfecto horizontal para los no leídos
                badge = ft.Container(
                    content=ft.Text(str(no_leidos), size=12, color="white", weight="bold"),
                    bgcolor="red",
                    width=24,
                    height=24,
                    border_radius=12,
                    alignment=ft.alignment.center
                ) if no_leidos > 0 else ft.Container(width=0, height=0)

                tile = ft.ListTile(
                    leading=ft.Icon(ft.Icons.PERSON),
                    title=ft.Text(nombre_contacto, color="white", expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS), # Obliga al texto a ser horizontal
                    trailing=badge,
                    on_click=lambda e, nom=nombre_contacto: cliente.cambiar_chat(nom)
                )
                lista_contactos_ui.controls.append(tile)

        # 2. Actualizar Mensajes
        lista_mensajes_ui.controls.clear()

        if cliente.conversacion_actual and not cliente.mensajes_chat_actual:
            lista_mensajes_ui.controls.append(
                ft.Text(f"Chat con {cliente.conversacion_actual}", color="grey", italic=True, text_align="center")
            )

        # Ordenamos los mensajes por su timestamp original por si llegan desordenados
        mensajes_ordenados = sorted(cliente.mensajes_chat_actual, key=lambda x: x.split(";")[2] if len(x.split(";"))>=6 else "")

        for m in mensajes_ordenados:
            datos = m.split(";")
            if len(datos) >= 6:
                emisor = datos[0].replace("@", "")
                texto = datos[5].replace('"', '')
                estado = datos[3]

                es_mio = (emisor == usuario)
                color_bg = COLORS['accent'] if es_mio else COLORS['glass']
                align = ft.MainAxisAlignment.END if es_mio else ft.MainAxisAlignment.START

                # Sistema de doble check estilo WhatsApp
                check = " ✓" if estado in ["ENVIADO", "RECIBIDO"] else (" ✓✓" if estado == "ENTREGADO" else (" ✓✓ (Leído)" if estado == "LEIDO" else ""))

                burbuja = ft.Container(
                    content=ft.Text(texto + (check if es_mio else ""), color="white"),
                    bgcolor=color_bg, padding=10, border_radius=10,
                    max_width=400  # Evita que burbujas cortas sean muy anchas
                )
                lista_mensajes_ui.controls.append(ft.Row([burbuja], alignment=align))

        try:
            page.update()
        except:
            pass

    cliente = ClienteChat(usuario, actualizar_ui)

    def enviar_click(e):
        if campo_texto.value and cliente.conversacion_actual:
            cliente.enviar_mensaje(cliente.conversacion_actual, campo_texto.value)
            campo_texto.value = ""
            page.update()

    # --- LAYOUT ---
    panel_izquierdo = ft.Container(
        width=280, # Ensanchado para asegurar espacio horizontal a los nombres
        border=ft.border.only(right=ft.border.BorderSide(1, COLORS['muted'])),
        padding=10,
        content=ft.Column([
            ft.Text("Contactos", size=20, weight="bold"),
            ft.Row([campo_nuevo_chat, btn_nuevo_chat]),
            ft.Divider(color=COLORS['muted']),
            lista_contactos_ui
        ])
    )

    panel_derecho = ft.Container(
        expand=True, padding=10,
        content=ft.Column([
            ft.Text("Chat Interno", size=20, weight="bold"),
            lista_mensajes_ui,
            ft.Row([campo_texto, ft.IconButton(ft.Icons.SEND, on_click=enviar_click, icon_color=COLORS['accent'])])
        ])
    )

    return ft.Row([panel_izquierdo, panel_derecho], expand=True)