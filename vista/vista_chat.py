import flet as ft
import time
import threading
import modelo.manejador_datos as modelo
from vista.temas import COLORS


def crear_vista_chat(page: ft.Page):
    usuario = page.session.get("user_name")

    estado_chat = {
        "conversacion_actual": "",
        "foto_actual": None,
        "rol_actual": "",
        "corriendo": True
    }

    lista_contactos_ui = ft.ListView(expand=True, spacing=8)
    lista_mensajes_ui = ft.ListView(expand=True, spacing=12, auto_scroll=True)

    campo_texto = ft.TextField(
        hint_text="Escribe un mensaje de seguridad...",
        expand=True,
        border_color=COLORS['glass'],
        focused_border_color=COLORS['accent'],
        text_size=14,
        on_submit=lambda e: enviar_click(e)
    )

    campo_nuevo_chat = ft.TextField(
        hint_text="Nombre de agente...",
        height=40,
        expand=True,
        text_size=13,
        content_padding=10,
        border_color=COLORS['glass']
    )

    header_chat = ft.Container(
        content=ft.Text("Chat Interno", size=18, weight="bold", color=COLORS['text']),
        padding=ft.padding.only(bottom=15, top=5, left=5, right=5),
        border=ft.border.only(bottom=ft.border.BorderSide(1, COLORS['glass']))
    )

    area_input_chat = ft.Container(visible=False)

    def cambiar_chat(nuevo_destinatario, foto_b64=None, rol=None):
        estado_chat["conversacion_actual"] = nuevo_destinatario
        estado_chat["foto_actual"] = foto_b64
        estado_chat["rol_actual"] = rol if rol else "agente"
        modelo.marcar_mensajes_leidos(nuevo_destinatario, usuario)

        avatar_src = ft.Image(src_base64=foto_b64, fit=ft.ImageFit.COVER, border_radius=20) if foto_b64 else ft.Icon(
            ft.Icons.PERSON, color="white")

        rol_mostrar = f"Rol: {estado_chat['rol_actual'].upper()}"

        header_chat.content = ft.Row([
            ft.Row([
                ft.Container(content=avatar_src, width=40, height=40, border_radius=20, bgcolor="#374151"),
                ft.Column([
                    ft.Text(nuevo_destinatario, weight="bold", size=16, color="white"),
                    ft.Text(rol_mostrar, size=11, color=COLORS['good'])
                ], spacing=2)
            ], spacing=15),
            ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_color="#ef4444",
                tooltip="Borrar conversación",
                on_click=lambda e: confirmar_borrado_dialogo(e)
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        if header_chat.page: header_chat.update()

        area_input_chat.visible = True
        if area_input_chat.page: area_input_chat.update()

        refrescar_ui_ahora()

    def confirmar_borrado_dialogo(e):
        def ejecutar_borrado(evt):
            modelo.eliminar_conversacion(usuario, estado_chat["conversacion_actual"])
            estado_chat["conversacion_actual"] = ""

            header_chat.content = ft.Text("Chat Interno", size=18, weight="bold", color=COLORS['text'])
            area_input_chat.visible = False

            e.page.close(dlg)

            if header_chat.page: header_chat.update()
            if area_input_chat.page: area_input_chat.update()
            refrescar_ui_ahora()

        dlg = ft.AlertDialog(
            title=ft.Text("¿Vaciar conversación?"),
            content=ft.Text(f"Se eliminarán permanentemente los mensajes con {estado_chat['conversacion_actual']}."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda evt: e.page.close(dlg)),
                ft.ElevatedButton("Vaciar", bgcolor="#ef4444", color="white", on_click=ejecutar_borrado)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        e.page.open(dlg)

    def iniciar_nuevo_chat_click(e):
        nuevo_usuario = campo_nuevo_chat.value.strip()
        if nuevo_usuario:
            campo_nuevo_chat.value = ""
            cambiar_chat(nuevo_usuario, None, None)

    btn_nuevo_chat = ft.IconButton(ft.Icons.ADD_CIRCLE, icon_color=COLORS['accent'], on_click=iniciar_nuevo_chat_click)

    def enviar_click(e):
        texto = campo_texto.value.strip()
        destinatario = estado_chat["conversacion_actual"]
        if texto and destinatario:
            if modelo.enviar_mensaje(usuario, destinatario, texto):
                campo_texto.value = ""
                if campo_texto.page: campo_texto.update()
                refrescar_ui_ahora()

    def refrescar_ui_ahora():
        if not lista_contactos_ui.page: return

        contactos_db = modelo.get_contactos_chat(usuario)
        lista_contactos_ui.controls.clear()

        for c in contactos_db:
            nombre_c = c['contacto']
            no_leidos = c['no_leidos']
            foto_c = c['foto']
            rol_c = c.get('rol', 'agente')

            badge = ft.Container(
                content=ft.Text(str(no_leidos), size=12, weight="bold", color="black"),
                bgcolor=COLORS['accent'], padding=ft.padding.all(6), border_radius=12, alignment=ft.alignment.center
            ) if no_leidos > 0 else ft.Container()

            avatar_list = ft.Image(src_base64=foto_c, fit=ft.ImageFit.COVER, border_radius=20) if foto_c else ft.Icon(
                ft.Icons.PERSON, color="#94a3b8")

            item = ft.Container(
                content=ft.Row([
                    ft.Container(content=avatar_list, width=40, height=40, border_radius=20, bgcolor="#374151"),
                    ft.Text(nombre_c, size=18, weight="bold" if no_leidos > 0 else "normal", expand=True),
                    badge
                ], spacing=12),
                padding=10,
                border_radius=8,
                bgcolor=COLORS['glass'] if estado_chat["conversacion_actual"] == nombre_c else "transparent",
                on_click=lambda e, n=nombre_c, f=foto_c, r=rol_c: cambiar_chat(n, f, r)
            )
            lista_contactos_ui.controls.append(item)

        lista_contactos_ui.update()

        destinatario_actual = estado_chat["conversacion_actual"]
        lista_mensajes_ui.controls.clear()

        if destinatario_actual:
            mensajes_db = modelo.get_mensajes_chat(usuario, destinatario_actual)

            for m in mensajes_db:
                soy_emisor = (m['emisor'] == usuario)

                icon_tick = ft.Container()
                if soy_emisor:
                    if m['estado'] == "RECIBIDO":
                        icon_tick = ft.Icon(ft.Icons.CHECK, size=14, color="gray")
                    elif m['estado'] == "ENTREGADO":
                        icon_tick = ft.Icon(ft.Icons.DONE_ALL, size=14, color="gray")
                    elif m['estado'] == "LEIDO":
                        icon_tick = ft.Icon(ft.Icons.DONE_ALL, size=14, color="#38bdf8")

                meta_row = ft.Row([
                    ft.Text(m['fecha'], size=10, color=COLORS['muted']),
                    icon_tick
                ], spacing=4, alignment=ft.MainAxisAlignment.END if soy_emisor else ft.MainAxisAlignment.START)

                burbuja = ft.Container(
                    content=ft.Column([
                        ft.Text(m['texto'], color="white" if soy_emisor else "#e2e8f0", size=14),
                        meta_row
                    ], spacing=3, tight=True),
                    alignment=ft.alignment.center_left,
                    padding=ft.padding.only(left=12, right=12, top=8, bottom=5),
                    border_radius=ft.border_radius.only(
                        top_left=12, top_right=12,
                        bottom_left=12 if soy_emisor else 2,
                        bottom_right=2 if soy_emisor else 12
                    ),
                    bgcolor="#1e3a8a" if soy_emisor else COLORS['room_bg']
                )

                fila_mensaje = ft.Row(
                    [burbuja],
                    alignment=ft.MainAxisAlignment.END if soy_emisor else ft.MainAxisAlignment.START
                )
                lista_mensajes_ui.controls.append(fila_mensaje)

        lista_mensajes_ui.update()

    def bucle_refresco():
        while estado_chat["corriendo"] and not lista_contactos_ui.page:
            time.sleep(0.05)

        while estado_chat["corriendo"]:
            if lista_contactos_ui.page:
                modelo.marcar_mensajes_entregados(usuario)
                if estado_chat["conversacion_actual"]:
                    modelo.marcar_mensajes_leidos(estado_chat["conversacion_actual"], usuario)
                refrescar_ui_ahora()
            time.sleep(1.5)

    hilo = threading.Thread(target=bucle_refresco, daemon=True)
    hilo.start()

    panel_izquierdo = ft.Container(
        width=280,
        border=ft.border.only(right=ft.border.BorderSide(1, COLORS['glass'])),
        padding=ft.padding.only(right=15, top=5, bottom=5),
        content=ft.Column([
            ft.Text("Contactos", size=18, weight="bold", color=COLORS['accent']),
            ft.Row([campo_nuevo_chat, btn_nuevo_chat], spacing=5),
            ft.Divider(color=COLORS['glass'], height=10),
            lista_contactos_ui
        ], expand=True)
    )

    area_input_chat.content = ft.Row([
        campo_texto,
        ft.IconButton(ft.Icons.SEND, icon_color=COLORS['accent'], icon_size=24, on_click=enviar_click)
    ], spacing=10)

    panel_derecho = ft.Container(
        expand=True,
        padding=ft.padding.only(left=15),
        content=ft.Column([
            header_chat,
            lista_mensajes_ui,
            area_input_chat
        ], expand=True)
    )

    main_layout = ft.Container(
        content=ft.Row([panel_izquierdo, panel_derecho], expand=True),
        padding=25,
        expand=True,
        bgcolor=COLORS['card'],
        border_radius=10,
        border=ft.border.all(1, COLORS['glass'])
    )

    return main_layout