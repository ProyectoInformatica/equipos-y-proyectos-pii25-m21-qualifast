import socket
import threading
import datetime
import time
import glob

# Definimos la configuración básica de conexión y archivos
ip_servidor = "0.0.0.0"
port_999 = 999
port_666 = 666
lista_mensajes = []

sem_lista_mensajes = threading.Semaphore(1)

def validar_archivo(emisor, receptor):
    archivo = f"{emisor}_{receptor}.txt"
    archivo_invertido = f"{receptor}_{emisor}.txt"
    try:
        f = open(archivo, "r")
        f.close()
        return archivo
    except FileNotFoundError:
        try:
            f = open(archivo_invertido, "r")
            f.close()
            return archivo_invertido
        except FileNotFoundError:
            return archivo

def guardar_mensaje_en_archivo(mensaje_formateado):
    mensaje = mensaje_formateado.decode()
    partes = mensaje.split(";")
    if len(partes) >= 6:
        emisor = partes[0].replace("@", "")
        receptor = partes[1].replace("@", "")
        print(f"[SISTEMA] Mensaje de {emisor} para {receptor}")
        archivo_final = validar_archivo(emisor, receptor)
        guardado = False

        while not guardado:
            if sem_lista_mensajes.acquire(timeout=2):
                try:
                    with open(archivo_final, "a") as f:
                        f.write(mensaje + "\n")

                    chat_registrado = False
                    try:
                        with open("indice_chats.txt", "r") as indice:
                            if archivo_final in [line.strip() for line in indice.readlines()]:
                                chat_registrado = True
                    except FileNotFoundError:
                        pass

                    if not chat_registrado:
                        with open("indice_chats.txt", "a") as nuevo_indice:
                            nuevo_indice.write(archivo_final + "\n")

                    sem_lista_mensajes.release()
                    guardado = True
                except Exception as e:
                    sem_lista_mensajes.release()
                    guardado = True
            else:
                time.sleep(1)

def puerto_666():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((ip_servidor, port_666))
    servidor.listen()
    print("Servidor [666]: Listo para recibir mensajes.")

    while True:
        try:
            conn, addr = servidor.accept()
            conn.settimeout(10)
            try:
                mensaje = conn.recv(1024).decode()
                if mensaje:
                    partes = mensaje.split(";")
                    if len(partes) >= 6:
                        estado = partes[3]

                        if estado == "LEIDO":
                            emisor = partes[0].replace("@", "")
                            receptor = partes[1].replace("@", "")

                            if sem_lista_mensajes.acquire(timeout=5):
                                try:
                                    archivo = validar_archivo(emisor, receptor)
                                    with open(archivo, "r") as f:
                                        lines = f.readlines()

                                    new_lines = []
                                    cambio = False

                                    for m in lines:
                                        m_str = m.strip()
                                        p = m_str.split(";")
                                        if len(p) >= 6 and p[0].replace("@", "") == emisor:
                                            # Actualizamos el estado a LEIDO
                                            if p[3] in ["ENTREGADO", "RECIBIDO"]:
                                                ts_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                                                nuevo_m = f"{p[0]};{p[1]};{p[2]};LEIDO;{ts_now};{p[5]}"
                                                new_lines.append(nuevo_m)
                                                cambio = True
                                            else:
                                                new_lines.append(m_str)
                                        else:
                                            new_lines.append(m_str)

                                    if cambio:
                                        with open(archivo, "w") as f:
                                            for nl in new_lines: f.write(nl + "\n")

                                    sem_lista_mensajes.release()
                                    conn.send("OK".encode())
                                except:
                                    sem_lista_mensajes.release()
                                    conn.send("KO".encode())
                        else:
                            # Guardado normal (Estado pasa a RECIBIDO)
                            emisor = partes[0]
                            receptor = partes[1]
                            ts_orig = partes[2]
                            contenido = partes[5]
                            ahora = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                            msg_proc = f"{emisor};{receptor};{ts_orig};RECIBIDO;{ahora};{contenido}"
                            guardar_mensaje_en_archivo(msg_proc.encode())
                            conn.send("OK".encode())
            except:
                pass
            conn.close()
        except:
            pass

def gestionar_cliente_999(conn, addr):
    login_ok = False
    usuario_conectado = ""
    conn.settimeout(10)

    while True:
        try:
            datos = conn.recv(1024).decode().strip()
            if not datos: break

            es_login = datos.startswith("LOGIN")
            partes = datos.split(";")
            es_update = len(partes) >= 5 and partes[3] == "UPDATE"
            es_list = len(partes) >= 5 and partes[3] == "LIST"

            if es_login:
                d = datos.split(":")
                if len(d) >= 2:
                    conn.send("OK".encode())
                    login_ok = True
                    usuario_conectado = d[1]
                else:
                    conn.send("KO".encode())
                    break

            elif es_update and login_ok:
                ts_solicitado = partes[4]
                mensajes_a_enviar = []

                if sem_lista_mensajes.acquire(timeout=5):
                    try:
                        chats = glob.glob("*_*.txt")
                        for archivo in chats:
                            if usuario_conectado in archivo:
                                with open(archivo, "r") as f:
                                    msgs = f.readlines()

                                nuevas_lineas = []
                                modificado = False

                                for m in msgs:
                                    m_str = m.strip()
                                    p = m_str.split(";")
                                    linea_final = m_str

                                    if len(p) >= 6:
                                        origen = p[0].replace("@", "")
                                        destino = p[1].replace("@", "")
                                        estado = p[3]
                                        ts_estado = p[4]

                                        if destino == usuario_conectado and estado == "RECIBIDO":
                                            mensajes_a_enviar.append(m_str)
                                            now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                                            linea_final = f"{p[0]};{p[1]};{p[2]};ENTREGADO;{now};{p[5]}"
                                            modificado = True
                                        elif origen == usuario_conectado and ts_estado > ts_solicitado:
                                            mensajes_a_enviar.append(m_str)
                                        elif destino == usuario_conectado and ts_estado > ts_solicitado:
                                            mensajes_a_enviar.append(m_str)

                                    nuevas_lineas.append(linea_final)

                                if modificado:
                                    with open(archivo, "w") as f:
                                        for nl in nuevas_lineas: f.write(nl + "\n")
                        sem_lista_mensajes.release()
                    except:
                        sem_lista_mensajes.release()

                cant = len(mensajes_a_enviar)
                ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                conn.send(f"SERVER;{usuario_conectado};{ts};UPDATE;{ts};\"{cant}\"".encode())

                if conn.recv(1024).decode() == "OK":
                    for msg in mensajes_a_enviar:
                        conn.send(msg.encode())
                        conn.recv(1024)

            elif es_list and login_ok:
                chats_a_enviar = []
                if sem_lista_mensajes.acquire(timeout=5):
                    try:
                        archivos = glob.glob("*_*.txt")
                        procesados = []
                        for nombre in archivos:
                            if usuario_conectado in nombre:
                                p_nom = nombre.replace(".txt", "").split("_")
                                otro = p_nom[1] if p_nom[0] == usuario_conectado else p_nom[0]

                                if otro and otro not in procesados:
                                    procesados.append(otro)
                                    pendientes = 0
                                    try:
                                        with open(nombre, "r") as f:
                                            for l in f.readlines():
                                                cp = l.strip().split(";")
                                                # Conta como no leídos los RECIBIDO o ENTREGADO
                                                if len(cp) >= 6 and cp[1].replace("@", "") == usuario_conectado and cp[3] in ["RECIBIDO", "ENTREGADO"]:
                                                    pendientes += 1
                                    except:
                                        pass
                                    chats_a_enviar.append(f"{otro};{usuario_conectado};00000000000000;LIST;00000000000000;\"{pendientes}\"")
                        sem_lista_mensajes.release()
                    except:
                        sem_lista_mensajes.release()

                cant = len(chats_a_enviar)
                ts_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                conn.send(f"SERVER;{usuario_conectado};{ts_now};LIST;{ts_now};\"{cant}\"".encode())

                if conn.recv(1024).decode() == "OK":
                    for c_item in chats_a_enviar:
                        conn.send(c_item.encode())
                        conn.recv(1024)
            else:
                conn.send("KO".encode())
                break
        except:
            break
    conn.close()

def puerto_999():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((ip_servidor, port_999))
    servidor.listen()
    print("Servidor [999]: Listo para Login automático y Updates (Multihilo).")

    while True:
        try:
            conn, addr = servidor.accept()
            threading.Thread(target=gestionar_cliente_999, args=(conn, addr)).start()
        except:
            pass

hilo_envios = threading.Thread(target=puerto_666)
hilo_recibos = threading.Thread(target=puerto_999)

hilo_envios.start()
hilo_recibos.start()

hilo_envios.join()
hilo_recibos.join()