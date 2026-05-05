import socket
import threading
import time
from datetime import datetime

SERVER_IP = "127.0.0.1"


class ClienteChat:
    def __init__(self, usuario, on_update_callback):
        self.usuario = usuario
        self.on_update = on_update_callback
        self.conversacion_actual = ""
        self.corriendo = True
        self.lista_contactos = []
        self.mensajes_chat_actual = []
        self.ts_ultimo_por_chat = {}

        # Conectar e iniciar hilo receptor
        threading.Thread(target=self._hilo_recepcion, daemon=True).start()

    def _obtener_timestamp(self):
        return datetime.now().strftime("%Y%m%d%H%M%S")

    def _hilo_recepcion(self):
        while self.corriendo:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((SERVER_IP, 999))
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
                            datos_chat = s.recv(1024).decode().strip()
                            if datos_chat:
                                contactos_tmp.append(datos_chat)
                            s.send("OK".encode())
                        self.lista_contactos = contactos_tmp

                    # 2. Pedir UPDATE del chat actual
                    if self.conversacion_actual:
                        ts_ultimo = self.ts_ultimo_por_chat.get(self.conversacion_actual, "00000000000000")
                        s.send(
                            f"{self.usuario};{self.conversacion_actual};{self._obtener_timestamp()};UPDATE;{ts_ultimo};\"\"".encode())
                        cab_upd = s.recv(1024).decode().split(";")

                        if len(cab_upd) >= 6:
                            try:
                                cant_upd = int(cab_upd[5].replace('"', ''))
                            except:
                                cant_upd = 0

                            s.send("OK".encode())

                            for _ in range(cant_upd):
                                msg = s.recv(1024).decode().strip()
                                s.send("OK".encode())

                                partes = msg.split(";")
                                if len(partes) >= 6:
                                    emisor = partes[0].replace("@", "")
                                    ts_orig = partes[2]
                                    estado = partes[3]
                                    ts_msg = partes[4]

                                    existe = False
                                    for i in range(len(self.mensajes_chat_actual)):
                                        if self.mensajes_chat_actual[i].split(";")[2] == ts_orig:
                                            self.mensajes_chat_actual[i] = msg
                                            existe = True
                                            break

                                    if not existe:
                                        self.mensajes_chat_actual.append(msg)

                                    if ts_msg > ts_ultimo:
                                        self.ts_ultimo_por_chat[self.conversacion_actual] = ts_msg

                                    if emisor == self.conversacion_actual and estado != "LEIDO":
                                        self._enviar_confirmacion_leido(emisor, ts_orig)

                    # Avisar a Flet de manera segura
                    try:
                        self.on_update()
                    except Exception as e:
                        pass

                s.close()
            except Exception as e:
                pass
            time.sleep(2)

    def _enviar_confirmacion_leido(self, emisor, ts_orig):
        try:
            ts = self._obtener_timestamp()
            msg_leido = f"{emisor};{self.usuario};{ts_orig};LEIDO;{ts};\"\""
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((SERVER_IP, 666))
            s.send(msg_leido.encode())
            s.recv(1024)
            s.close()
        except:
            pass

    def enviar_mensaje(self, destinatario, texto):
        ts = self._obtener_timestamp()
        texto_limpio = texto.replace(";", ",")  # Evitar que rompa la estructura CSV
        msg_formateado = f"{self.usuario};{destinatario};{ts};ENVIADO;{ts};\"{texto_limpio}\""
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
            pass

    def cambiar_chat(self, nuevo_destinatario):
        self.conversacion_actual = nuevo_destinatario
        self.mensajes_chat_actual = []
        self.ts_ultimo_por_chat[nuevo_destinatario] = "00000000000000"
        try:
            self.on_update()
        except:
            pass