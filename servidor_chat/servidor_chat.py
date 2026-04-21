import socket
import threading
import datetime
import time
import os
import glob

# Definimos la configuración básica de conexión y archivos
ip_servidor = "0.0.0.0"
port_999 = 999
port_666 = 666
lista_mensajes = []

# Utilizamos un semáforo para evitar conflictos al escribir en archivos compartidos
sem_lista_mensajes = threading.Semaphore(1)

# --- FUNCIONES AUXILIARES ---

def validar_archivo(emisor, receptor):
    """Determinamos el nombre del archivo de chat buscando ambas combinaciones."""
    archivo = f"{emisor}_{receptor}.txt"
    archivo_invertido = f"{receptor}_{emisor}.txt"
    try:
        archivo_final = open(archivo, "r")
        archivo_final.close()
        archivo_final = archivo
    except FileNotFoundError:
        try:
            archivo_final = open(archivo_invertido, "r")
            archivo_final.close()
            archivo_final = archivo_invertido
        except FileNotFoundError:
            archivo_final = archivo
    return archivo_final

def guardar_mensaje_en_archivo(mensaje_formateado):
    """Escribimos el mensaje físicamente en el disco gestionando la concurrencia."""
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
                    archivo_final_escribir = open(archivo_final, "a")
                    archivo_final_escribir.write(mensaje + "\n")
                    archivo_final_escribir.close()
                    print(f"[SISTEMA] Guardado en: {archivo_final}")

                    chat_registrado = False
                    try:
                        indice = open("indice_chats.txt", "r")
                        indice_chats = indice.readlines()
                        indice.close()
                        for i in range(len(indice_chats)):
                            if indice_chats[i].strip() == archivo_final:
                                chat_registrado = True
                    except FileNotFoundError:
                        chat_registrado = False

                    if chat_registrado == False:
                        nuevo_indice = open("indice_chats.txt", "a")
                        nuevo_indice.write(archivo_final + "\n")
                        nuevo_indice.close()

                    sem_lista_mensajes.release()
                    guardado = True
                except Exception as e:
                    print(f"[ERROR GUARDADO] {e}")
                    sem_lista_mensajes.release()
                    guardado = True
            else:
                time.sleep(1)
    else:
        print(f"[ERROR] El mensaje recibido no tiene el formato correcto")

# --- GESTIÓN DE PUERTOS ---

def puerto_666():
    """Gestionamos la recepción de mensajes y las confirmaciones de lectura."""
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((ip_servidor, port_666))
    servidor.listen()
    print("Servidor [666]: Listo para recibir mensajes.")

    conexion_servidor = True

    while conexion_servidor:
        try:
            conn, addr = servidor.accept()
            conn.settimeout(10)

            try:
                mensaje = conn.recv(1024).decode()
                if mensaje != "":
                    partes = mensaje.split(";")

                    if mensaje == "!DESCONECTAR":
                        print(f"[666] Apagando")
                        conn.send(f"[666] Apagando".encode())
                        conexion_servidor = False

                    elif len(partes) >= 6:
                        estado = partes[3]

                        # Si recibimos LEIDO, actualizamos el historial
                        if estado == "LEIDO":
                            emisor = partes[0].replace("@", "")
                            receptor = partes[1].replace("@", "")

                            if sem_lista_mensajes.acquire(timeout=5):
                                try:
                                    archivo = validar_archivo(emisor, receptor)
                                    f = open(archivo, "r")
                                    lines = f.readlines()
                                    f.close()

                                    new_lines = []
                                    cambio = False

                                    i = 0
                                    while i < len(lines):
                                        m = lines[i].strip()
                                        p = m.split(";")

                                        if len(p) >= 6 and p[1].replace("@", "") == emisor:
                                            if p[3] == "ENTREGADO" or p[3] == "RECIBIDO":
                                                ts_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                                                nuevo_m = f"{p[0]};{p[1]};{p[2]};LEIDO;{ts_now};{p[5]}"
                                                new_lines.append(nuevo_m)
                                                cambio = True
                                            else:
                                                new_lines.append(m)
                                        else:
                                            new_lines.append(m)
                                        i = i + 1

                                    if cambio:
                                        f = open(archivo, "w")
                                        for nl in new_lines: f.write(nl + "\n")
                                        f.close()

                                    sem_lista_mensajes.release()
                                    conn.send("OK".encode())
                                except:
                                    sem_lista_mensajes.release()
                                    conn.send("KO".encode())

                        # Si es mensaje normal, lo guardamos como RECIBIDO
                        else:
                            emisor = partes[0]
                            receptor = partes[1]
                            ts_orig = partes[2]
                            contenido = partes[5]

                            nuevo_estado = "RECIBIDO"
                            ahora = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

                            msg_proc = f"{emisor};{receptor};{ts_orig};{nuevo_estado};{ahora};{contenido}"
                            guardar_mensaje_en_archivo(msg_proc.encode())
                            conn.send("OK".encode())
                    else:
                        conn.send("KO".encode())
            except Exception as e:
                print(f"[666 Error] {e}")

            conn.close()
        except Exception as e:
            print(f"[ERROR 666 loop] {e}")


def gestionar_cliente_999(conn, addr):
    """Atendemos Login sin password y Peticiones de actualización."""
    print(f"[999] Atendiendo a {addr}")
    login_ok = False
    conexion_activa = True
    usuario_conectado = ""

    conn.settimeout(10)

    while conexion_activa:
        try:
            datos = conn.recv(1024).decode().strip()
            if datos == "":
                conexion_activa = False
            else:
                es_login = datos.startswith("LOGIN")
                partes = datos.split(";")
                es_update = False
                es_list = False
                ts_solicitado = "00000000000000"

                if len(partes) >= 5:
                    if partes[3] == "UPDATE":
                        es_update = True
                        ts_solicitado = partes[4]
                    elif partes[3] == "LIST":
                        es_list = True

                # Bloque de Login Simplificado
                if es_login:
                    d = datos.split(":")
                    if len(d) >= 2:
                        conn.send("OK".encode())
                        login_ok = True
                        usuario_conectado = d[1]
                    else:
                        conn.send("KO".encode())
                        conexion_activa = False

                # Bloque de Actualización (Descarga de mensajes)
                elif es_update and login_ok:
                    mensajes_a_enviar = []

                    if sem_lista_mensajes.acquire(timeout=5):
                        try:
                            chats = glob.glob("*_*.txt")
                            i = 0
                            while i < len(chats):
                                archivo = chats[i]
                                if usuario_conectado in archivo:
                                    f = open(archivo, "r")
                                    msgs = f.readlines()
                                    f.close()

                                    modificado = False
                                    nuevas_lineas = []

                                    j = 0
                                    while j < len(msgs):
                                        m = msgs[j].strip()
                                        p = m.split(";")
                                        linea_final = m

                                        if len(p) >= 6:
                                            origen = p[0].replace("@", "")
                                            destino = p[1].replace("@", "")
                                            estado = p[3]
                                            ts_estado = p[4]

                                            if destino == usuario_conectado and estado == "RECIBIDO":
                                                mensajes_a_enviar.append(m)
                                                now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                                                linea_final = f"{p[0]};{p[1]};{p[2]};ENTREGADO;{now};{p[5]}"
                                                modificado = True

                                            elif origen == usuario_conectado and ts_estado > ts_solicitado:
                                                mensajes_a_enviar.append(m)

                                        nuevas_lineas.append(linea_final)
                                        j = j + 1

                                    if modificado:
                                        f = open(archivo, "w")
                                        for nl in nuevas_lineas: f.write(nl + "\n")
                                        f.close()
                                i = i + 1
                            sem_lista_mensajes.release()
                        except:
                            sem_lista_mensajes.release()

                    cant = len(mensajes_a_enviar)
                    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    cab = f"SERVER;{usuario_conectado};{ts};UPDATE;{ts};\"{cant}\""
                    conn.send(cab.encode())

                    if conn.recv(1024).decode() == "OK":
                        k = 0
                        while k < cant:
                            conn.send(mensajes_a_enviar[k].encode())
                            conn.recv(1024)
                            k = k + 1

                # Bloque de Listado de conversaciones
                elif es_list and login_ok:
                    chats_a_enviar = []
                    if sem_lista_mensajes.acquire(timeout=5):
                        try:
                            archivos = glob.glob("*_*.txt")
                            procesados = []
                            i = 0
                            while i < len(archivos):
                                nombre = archivos[i]
                                if usuario_conectado in nombre:
                                    partes_nom = nombre.replace(".txt", "").split("_")
                                    otro = ""
                                    if len(partes_nom) == 2:
                                        if partes_nom[0] == usuario_conectado:
                                            otro = partes_nom[1]
                                        elif partes_nom[1] == usuario_conectado:
                                            otro = partes_nom[0]

                                    ya_esta = False
                                    for usr in procesados:
                                        if usr == otro: ya_esta = True

                                    if otro != "" and not ya_esta:
                                        procesados.append(otro)
                                        pendientes = 0
                                        try:
                                            f = open(nombre, "r")
                                            lineas = f.readlines()
                                            f.close()
                                            for l in lineas:
                                                cp = l.split(";")
                                                if len(cp) >= 6:
                                                    if cp[1].replace("@", "") == usuario_conectado and cp[3] == "RECIBIDO":
                                                        pendientes += 1
                                        except:
                                            pass

                                        ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                                        item = f"{otro};{usuario_conectado};00000000000000;LIST;00000000000000;\"{pendientes}\""
                                        chats_a_enviar.append(item)
                                i = i + 1
                            sem_lista_mensajes.release()
                        except:
                            sem_lista_mensajes.release()

                    cant = len(chats_a_enviar)
                    ts_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    header = f"SERVER;{usuario_conectado};{ts_now};LIST;{ts_now};\"{cant}\""
                    conn.send(header.encode())

                    if conn.recv(1024).decode() == "OK":
                        for chat_item in chats_a_enviar:
                            conn.send(chat_item.encode())
                            conn.recv(1024)

                else:
                    conn.send("KO".encode())
                    conexion_activa = False
        except:
            conexion_activa = False
    conn.close()


def puerto_999():
    """Lanzamos el servidor de escucha para conexiones entrantes."""
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((ip_servidor, port_999))
    servidor.listen()
    print("Servidor [999]: Listo para Login automático y Updates (Multihilo).")

    while True:
        try:
            conn, addr = servidor.accept()
            t = threading.Thread(target=gestionar_cliente_999, args=(conn, addr))
            t.start()
        except Exception as e:
            print(f"[ERROR ACCEPT 999] {e}")


# --- ARRANQUE PRINCIPAL ---
hilo_envios = threading.Thread(target=puerto_666)
hilo_recibos = threading.Thread(target=puerto_999)

hilo_envios.start()
hilo_recibos.start()

hilo_envios.join()
hilo_recibos.join()