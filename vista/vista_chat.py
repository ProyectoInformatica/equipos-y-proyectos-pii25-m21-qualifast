import flet as ft
import time
import threading
import modelo.manejador_datos as modelo
from vista.temas import COLORS


def crear_vista_chat(page: ft.Page):
    usuario = page.session.get("user_name")

    # Variables de estado
    estado_chat = {
        "conversacion_actual": "",
        "corriendo": True
    }

    # Controles UI
    lista_contactos_ui = ft.ListView(expand=True, spacing=10)
    lista_mensajes_ui = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    campo_texto = ft.TextField(hint_text="Escribe un mensaje...", expand=True, on_submit=lambda e: enviar_click(e))
    campo_nuevo_chat = ft.TextField(hint_text="Nombre de usuario...", height=40, expand=True, content_padding=10)

    def cambiar_chat(nuevo_destinatario):
        estado_chat["conversacion_actual"] = nuevo_destinatario
        modelo.marcar_mensajes_leidos(nuevo_destinatario, usuario)
        refrescar_ui_ahora()

    def iniciar_nuevo_chat_click(e):
        nuevo_usuario = campo_nuevo_chat.value.strip()
        if nuevo_usuario:
            campo_nuevo_chat.value = ""
            cambiar_chat(nuevo_usuario)

    btn_nuevo_chat = ft.IconButton(ft.Icons.PERSON_ADD, on_click=iniciar_nuevo_chat_click, icon_color="#38bdf8")

    def enviar_click(e):
        if campo_texto.value and estado_chat["conversacion_actual"]:
            # Guardamos en la base de datos
            modelo.enviar_mensaje(usuario, estado_chat["conversacion_actual"], campo_texto.value)
            campo_texto.value = ""
            refrescar_ui_ahora()

    def refrescar_ui_ahora():
        if not page or page.route != "/chat":
            return

        # 1. ACTUALIZAR CONTACTOS DESDE MYSQL
        contactos_db = modelo.get_contactos_chat(usuario)
        nuevos_contactos = []

        # Si acabamos de iniciar chat con alguien y aún no hay mensajes, lo forzamos en la lista
        if estado_chat["conversacion_actual"] and not any(
                c['contacto'] == estado_chat["conversacion_actual"] for c in contactos_db):
            contactos_db.insert(0, {'contacto': estado_chat["conversacion_actual"], 'no_leidos': 0})

        for c in contactos_db:
            nombre = c['contacto']
            no_leidos = c['no_leidos']

            badge = ft.Container(
                content=ft.Text(str(no_leidos), size=12, color="white", weight="bold"),
                bgcolor="red", width=24, height=24, border_radius=12, alignment=ft.alignment.center
            ) if no_leidos > 0 else ft.Container(width=0, height=0)

            es_actual = (nombre == estado_chat["conversacion_actual"])
            fondo = "#374151" if es_actual else ft.Colors.TRANSPARENT

            tile = ft.ListTile(
                leading=ft.Icon(ft.Icons.PERSON),
                title=ft.Text(nombre, color="white", expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                trailing=badge,
                bgcolor=fondo,
                on_click=lambda e, nom=nombre: cambiar_chat(nom)
            )
            nuevos_contactos.append(tile)

        lista_contactos_ui.controls = nuevos_contactos

        # 2. ACTUALIZAR MENSAJES DESDE MYSQL
        nuevos_mensajes = []
        if estado_chat["conversacion_actual"]:
            mensajes_db = modelo.get_mensajes_chat(usuario, estado_chat["conversacion_actual"])

            if not mensajes_db:
                nuevos_mensajes.append(
                    ft.Text(f"Chat con {estado_chat['conversacion_actual']}", color="#9ca3af", italic=True,
                            text_align="center"))

            for m in mensajes_db:
                es_mio = (m['emisor'] == usuario)
                color_bg = "#38bdf8" if es_mio else "#374151"
                align = ft.MainAxisAlignment.END if es_mio else ft.MainAxisAlignment.START

                # --- LÓGICA DE TICKS TIPO WHATSAPP AÑADIDA ---
                check = ""
                if es_mio:
                    if m['estado'] == 'RECIBIDO':
                        check = " ✓"  # Enviado (1 tick)
                    elif m['estado'] == 'ENTREGADO':
                        check = " ✓✓"  # Entregado (2 ticks)
                    elif m['estado'] == 'LEIDO':
                        check = " ✓✓ (Leído)"  # Visto (2 ticks azules simulados)

                hora = ft.Text(m['fecha'].split(" ")[1][:5], size=10, color="#d1d5db")  # Solo saca HH:MM
                texto_burbuja = ft.Text(m['texto'] + check, color="white")

                burbuja = ft.Container(
                    content=ft.Column([texto_burbuja, hora], spacing=2,
                                      horizontal_alignment=ft.CrossAxisAlignment.END if es_mio else ft.CrossAxisAlignment.START),
                    bgcolor=color_bg, padding=10, border_radius=10
                )
                nuevos_mensajes.append(ft.Row([burbuja], alignment=align))

        lista_mensajes_ui.controls = nuevos_mensajes

        try:
            page.update()
        except:
            pass

    # --- Hilo en segundo plano para comprobar mensajes nuevos ---
    def bucle_refresco():
        while estado_chat["corriendo"]:
            if page:
                # 1. MATA-HILOS FANTASMA: Si sales de /chat, apagamos este hilo
                if page.route != "/chat":
                    estado_chat["corriendo"] = False
                    break

                # 2. Marcamos que estamos activos (los mensajes que nos manden pasan de ✓ a ✓✓)
                modelo.marcar_mensajes_entregados(usuario)

                # 3. Si tienes seleccionado un usuario, marca esos mensajes como LEÍDOS
                if estado_chat["conversacion_actual"]:
                    modelo.marcar_mensajes_leidos(estado_chat["conversacion_actual"], usuario)

                refrescar_ui_ahora()
            time.sleep(0.5)

    hilo = threading.Thread(target=bucle_refresco, daemon=True)
    hilo.start()

    # Cuando la vista se destruye, paramos el hilo
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

    # Truco para parar el hilo si el usuario se va a otra pantalla (o cierra la app)
    page.on_disconnect = on_dispose

    return vista_final