import flet as ft
import time
import threading
import modelo.manejador_datos as modelo

def crear_vista_chat(page: ft.Page):
    usuario = page.session.get("user_name")

    # Variables de estado
    estado_chat = {
        "conversacion_actual": "",
        "corriendo": True,
        "ultimo_hash": ""  # <-- NUEVO: Para evitar parpadeos y bloqueos de UI
    }

    # Controles UI
    lista_contactos_ui = ft.ListView(expand=True, spacing=10)
    lista_mensajes_ui = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    campo_texto = ft.TextField(hint_text="Escribe un mensaje...", expand=True, on_submit=lambda e: enviar_click(e))
    campo_nuevo_chat = ft.TextField(hint_text="Nombre de usuario...", height=40, expand=True, content_padding=10)

    def cambiar_chat(nuevo_destinatario):
        estado_chat["conversacion_actual"] = nuevo_destinatario
        estado_chat["ultimo_hash"] = "" # Forzamos recarga al cambiar de chat
        modelo.marcar_mensajes_leidos(nuevo_destinatario, usuario)
        refrescar_ui_ahora()

    def iniciar_nuevo_chat_click(e):
        nuevo_usuario = campo_nuevo_chat.value.strip()
        if nuevo_usuario:
            campo_nuevo_chat.value = ""
            cambiar_chat(nuevo_usuario)

    btn_nuevo_chat = ft.IconButton(ft.Icons.PERSON_ADD, on_click=iniciar_nuevo_chat_click, icon_color="#38bdf8")

    def enviar_click(e):
        texto = campo_texto.value.strip()
        if texto and estado_chat["conversacion_actual"]:
            # 1. Guardar en BD
            exito = modelo.enviar_mensaje(usuario, estado_chat["conversacion_actual"], texto)
            if exito:
                # 2. Limpiar campo de texto
                campo_texto.value = ""
                page.update() # Actualizamos el campo de texto rápido
                # 3. Forzar refresco de la lista
                refrescar_ui_ahora()

    def refrescar_ui_ahora():
        # Si salimos de la ruta, matamos el hilo y salimos
        if not page or page.route != "/chat":
            estado_chat["corriendo"] = False
            return

        contactos_db = modelo.get_contactos_chat(usuario)
        mensajes_db = []
        if estado_chat["conversacion_actual"]:
            mensajes_db = modelo.get_mensajes_chat(usuario, estado_chat["conversacion_actual"])

        # --- LÓGICA DE OPTIMIZACIÓN (Evita bloqueos) ---
        hash_actual = str(contactos_db) + str(mensajes_db)
        if hash_actual == estado_chat["ultimo_hash"]:
            return  # Si no hay mensajes nuevos, NO re-renderizamos la UI
        estado_chat["ultimo_hash"] = hash_actual
        # -----------------------------------------------

        nuevos_contactos = []
        if estado_chat["conversacion_actual"] and not any(c['contacto'] == estado_chat["conversacion_actual"] for c in contactos_db):
            contactos_db.insert(0, {'contacto': estado_chat["conversacion_actual"], 'no_leidos': 0})

        for c in contactos_db:
            nombre = c['contacto']
            no_leidos = c['no_leidos']

            badge = ft.Container(
                content=ft.Text(str(no_leidos), size=12, color="white", weight="bold"),
                bgcolor="red", width=24, height=24, border_radius=12, alignment=ft.alignment.center
            ) if no_leidos > 0 else ft.Container(width=0, height=0)

            es_actual = (nombre == estado_chat["conversacion_actual"])
            fondo = "#374151" if es_actual else ft.colors.TRANSPARENT

            tile = ft.ListTile(
                leading=ft.Icon(ft.Icons.PERSON),
                # FIX: Quitamos expand=True de aquí para evitar las letras verticales
                title=ft.Text(nombre, color="white", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                trailing=badge,
                bgcolor=fondo,
                on_click=lambda e, nom=nombre: cambiar_chat(nom)
            )
            nuevos_contactos.append(tile)

        lista_contactos_ui.controls = nuevos_contactos

        # 2. ACTUALIZAR MENSAJES
        nuevos_mensajes = []
        if estado_chat["conversacion_actual"]:
            if not mensajes_db:
                nuevos_mensajes.append(ft.Text(f"Chat con {estado_chat['conversacion_actual']}", color="#9ca3af", italic=True, text_align="center"))

            for m in mensajes_db:
                es_mio = (m['emisor'] == usuario)
                color_bg = "#38bdf8" if es_mio else "#374151"
                align = ft.MainAxisAlignment.END if es_mio else ft.MainAxisAlignment.START

                check = ""
                if es_mio:
                    check = " ✓ (Env)" if m['estado'] == 'RECIBIDO' else " ✓✓ (Leído)"

                hora = ft.Text(m['fecha'].split(" ")[1][:5], size=10, color="#d1d5db")
                texto_burbuja = ft.Text(m['texto'] + check, color="white")

                burbuja = ft.Container(
                    content=ft.Column([texto_burbuja, hora], spacing=2,
                                      horizontal_alignment=ft.CrossAxisAlignment.END if es_mio else ft.CrossAxisAlignment.START),
                    bgcolor=color_bg, padding=10, border_radius=10, max_width=400
                )
                nuevos_mensajes.append(ft.Row([burbuja], alignment=align))

        lista_mensajes_ui.controls = nuevos_mensajes

        try:
            page.update()
        except:
            pass

    # --- Hilo en segundo plano ---
    def bucle_refresco():
        while estado_chat["corriendo"]:
            if page and page.route == "/chat":
                if estado_chat["conversacion_actual"]:
                    modelo.marcar_mensajes_leidos(estado_chat["conversacion_actual"], usuario)
                refrescar_ui_ahora()
            else:
                # FIX: Si salimos de la pestaña chat, rompemos el bucle para no consumir RAM
                estado_chat["corriendo"] = False
                break
            time.sleep(2)

    hilo = threading.Thread(target=bucle_refresco, daemon=True)
    hilo.start()

    def on_dispose(e):
        estado_chat["corriendo"] = False

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

    vista_final = ft.Row([panel_izquierdo, panel_derecho], expand=True)
    page.on_disconnect = on_dispose

    return vista_final