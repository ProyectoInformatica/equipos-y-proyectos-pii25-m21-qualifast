import socket
import threading
import time
from datetime import datetime
import os
import glob

# ¡Recuerda cambiar esto por la IP de tu Mac cuando se lo pases a otros ordenadores!
SERVER_IP = "127.0.0.1"

class ClienteChat:
    def __init__(self, usuario, on_update_callback):
        self.usuario = usuario
        self.on_update = on_update_callback  # Función para refrescar Flet
        self.conversacion_actual = ""
        self.corriendo = True
        self.lista_contactos = []
        self.mensajes_chat_actual = []

        # Conectar e iniciar hilo receptor
        threading.Thread(target=self._hilo_recepcion, daemon=True).start()

    def _obtener_timestamp(self):
        return datetime.now().strftime("%Y%m%d%H%M%S")

    def _hilo_recepcion(self):
        """Bucle en segundo plano que pide actualizaciones al puerto 999 sin bloquear la UI"""
        ts_ultimo = "00000000000000"
        while self.corriendo:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((SERVER_IP, 999))
                # Ya solo enviamos el usuario, sin contraseña
                s.send(f"LOGIN:{self.usuario}".encode())

                if s.recv(1024).decode() == "OK":
                    # 1. Pedir LISTA
                    s.send(f"@{self.usuario};@;{self._obtener_timestamp()};LIST;00000000000000;\"\"".encode())
                    cabecera = s.recv(1024).decode().split(";")
                    if len(cabecera) >= 6:
                        cantidad = int(cabecera[5].replace('"', ''))
                        s.send("OK".encode())
                        contactos_tmp = []
                        for _ in range(cantidad):
                            datos_chat = s.recv(1024).decode()
                            contactos_tmp.append(datos_chat)
                            s.send("OK".encode())
                        self.lista_contactos = contactos_tmp

                    # 2. Pedir UPDATE del chat actual
                    if self.conversacion_actual:
                        s.send(f"{self.usuario};{self.conversacion_actual};{self._obtener_timestamp()};UPDATE;{ts_ultimo};\"\"".encode())
                        cab_upd = s.recv(1024).decode().split(";")
                        if len(cab_upd) >= 6:
                            cant_upd = int(cab_upd[5].replace('"', ''))
                            s.send("OK".encode())
                            for _ in range(cant_upd):
                                msg = s.recv(1024).decode()
                                self.mensajes_chat_actual.append(msg)
                                s.send("OK".encode())
                                ts_ultimo = msg.split(";")[4]  # Actualizar ts

                    # Avisar a la UI Flet que hay nuevos datos
                    self.on_update()
                s.close()
            except Exception as e:
                pass  # Ignorar fallos de red silenciosamente en el log
            time.sleep(2)

    def enviar_mensaje(self, destinatario, texto):
        """Envía el mensaje al servidor por el puerto 666"""
        ts = self._obtener_timestamp()
        msg_formateado = f"{self.usuario};{destinatario};{ts};ENVIADO;{ts};\"{texto}\""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((SERVER_IP, 666))
            s.send(msg_formateado.encode())
            s.recv(1024)
            s.close()
            self.mensajes_chat_actual.append(msg_formateado)
            self.on_update()
        except:
            print("Error enviando mensaje")

    def cambiar_chat(self, nuevo_destinatario):
        self.conversacion_actual = nuevo_destinatario
        self.mensajes_chat_actual = []  # Limpiar historial local para cargar el nuevo
        self.on_update()