import mysql.connector
from mysql.connector import pooling
import bcrypt
import re
import time
import random
import base64
import requests
import os
import json
import csv
import io
from datetime import datetime
from collections import defaultdict

# --- CONFIGURACIÓN LOCAL (JSON) ---
CONFIG_FILE = "ajustes_locales.json"

LOCAL_CONFIG = {
    "db_host": "127.0.0.1",
    "db_port": "3306",
    "db_user": "root",
    "db_pass": "123456",
    "db_name": "comisaria_db",
    "esp32_ip": "10.197.123.128",
    "esp32_cam_ip": "10.197.123.146"
}

ESP32_IP = LOCAL_CONFIG["esp32_ip"]
ESP32_CAM_IP = LOCAL_CONFIG["esp32_cam_ip"]

# Variables para controlar el estado online/offline del ESP32 (Heartbeat)
ultima_conexion_esp32 = 0

def obtener_datos_exportacion_sensores():
    """Obtiene todos los logs de sensores para exportar a CSV."""
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = """
                SELECT s.nombre as Sensor, sl.valor as Valor, s.unidad as Unidad, sl.timestamp as Fecha
                FROM sensores_log sl
                JOIN sensores s ON sl.sensor_id = s.id
                ORDER BY sl.timestamp DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            conexion.close()
    return []

def obtener_datos_exportacion_chats():
    """Obtiene todos los mensajes de chat para exportar a CSV."""
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = """
                SELECT emisor, receptor, texto, estado, timestamp as Fecha
                FROM mensajes_chat
                ORDER BY emisor, receptor, timestamp ASC
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            conexion.close()
    return []

def exportar_a_csv_string(datos):
    """Convierte una lista de diccionarios a un string formato CSV."""
    if not datos:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=datos[0].keys())
    writer.writeheader()
    writer.writerows(datos)
    return output.getvalue()

def actualizar_heartbeat_esp32():
    global ultima_conexion_esp32
    ultima_conexion_esp32 = time.time()


def obtener_estado_esp32():
    # Si hace menos de 8 segundos que recibimos un dato de un sensor, está online
    return (time.time() - ultima_conexion_esp32) < 8


def load_local_config():
    global LOCAL_CONFIG, ESP32_IP, ESP32_CAM_IP
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                LOCAL_CONFIG.update(json.load(f))
        except Exception as e:
            print(f"[ERROR LOCAL] Fallo al leer config local: {e}")
    else:
        save_local_config(LOCAL_CONFIG)

    ESP32_IP = LOCAL_CONFIG.get("esp32_ip", "")
    ESP32_CAM_IP = LOCAL_CONFIG.get("esp32_cam_ip", "")


def save_local_config(new_config):
    global LOCAL_CONFIG, ESP32_IP, ESP32_CAM_IP
    LOCAL_CONFIG.update(new_config)
    ESP32_IP = LOCAL_CONFIG.get("esp32_ip", "")
    ESP32_CAM_IP = LOCAL_CONFIG.get("esp32_cam_ip", "")
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(LOCAL_CONFIG, f, indent=4)
        inicializar_pool()
    except Exception as e:
        print(f"[ERROR LOCAL] Fallo al guardar config local: {e}")


# --- INICIALIZACIÓN DE BASE DE DATOS ---
db_pool = None


def inicializar_pool():
    global db_pool
    try:
        db_config = {
            'host': LOCAL_CONFIG['db_host'],
            'port': int(LOCAL_CONFIG['db_port']),
            'user': LOCAL_CONFIG['db_user'],
            'password': LOCAL_CONFIG['db_pass'],
            'database': LOCAL_CONFIG['db_name'],
            'connect_timeout': 2
        }
        db_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="com_pool", pool_size=10, pool_reset_session=True, **db_config
        )
    except Exception as e:
        print(f"[ERROR BD] Fallo crítico al inicializar Pool de BD (Revisa credenciales/IP): {e}")
        db_pool = None


load_local_config()
inicializar_pool()


def probar_conexion():
    try:
        if db_pool:
            conn = db_pool.get_connection()
            conn.close()
            return True
        else:
            inicializar_pool()
            if db_pool:
                conn = db_pool.get_connection()
                conn.close()
                return True
    except:
        return False
    return False


def conectar():
    try:
        return db_pool.get_connection() if db_pool else None
    except Exception as e:
        print(f"[ERROR BD] No se pudo obtener conexión del pool: {e}")
        return None


def _convertir_a_base64(blob):
    if blob:
        return base64.b64encode(blob).decode('utf-8')
    return None


# --- LOGIN ÓPTIMO ---
def validar_usuario(u, p):
    conexion = conectar()
    rol, user_id, foto_b64 = None, None, None
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = """
                    SELECT u.password, r.nombre as rol, p.id, p.foto
                    FROM usuarios u
                             JOIN personas p ON u.persona_id = p.id
                             JOIN roles r ON u.rol_id = r.id
                    WHERE u.username = %s \
                      AND p.activo = 1
                    """
            cursor.execute(query, (u,))
            usuario = cursor.fetchone()

            if usuario:
                hash_db = usuario['password']
                match = False
                if hash_db.startswith('$2b$') or hash_db.startswith('$2a$'):
                    if bcrypt.checkpw(p.encode('utf-8'), hash_db.encode('utf-8')):
                        match = True
                elif p == hash_db:
                    match = True

                if match:
                    rol, user_id = usuario['rol'], usuario['id']
                    foto_b64 = _convertir_a_base64(usuario['foto'])
        except Exception as e:
            print(f"[ERROR BD] Fallo en validar_usuario: {e}")
        finally:
            conexion.close()
    return rol, user_id, foto_b64


# --- USUARIOS ---
def get_usuarios():
    conexion = conectar()
    res = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = """
                    SELECT p.id, u.username as user, u.password, r.nombre as rol, p.foto
                    FROM usuarios u
                        JOIN personas p \
                    ON u.persona_id = p.id
                        JOIN roles r ON u.rol_id = r.id
                    WHERE p.activo = 1
                    ORDER BY p.fecha_alta DESC
                    """
            cursor.execute(query)
            datos = cursor.fetchall()
            for d in datos:
                d['foto'] = _convertir_a_base64(d['foto'])
                res.append(d)
        except Exception as e:
            print(f"[ERROR BD] Fallo en get_usuarios: {e}")
        finally:
            conexion.close()
    return res


def add_usuario(u, p, r, foto_bytes=None):
    conexion = conectar()
    if conexion:
        try:
            conexion.start_transaction()
            cursor = conexion.cursor()
            dni = f"U{random.randint(1000, 9999)}X"
            cursor.execute(
                "INSERT INTO personas (dni, nombre, apellidos, tipo_persona, foto) VALUES (%s, %s, %s, 'USUARIO', %s)",
                (dni, u, 'Personal', foto_bytes))
            persona_id = cursor.lastrowid
            cursor.execute("SELECT id FROM roles WHERE nombre = %s", (r,))
            rol_id = cursor.fetchone()[0]
            hashed = bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("INSERT INTO usuarios (persona_id, username, password, rol_id) VALUES (%s, %s, %s, %s)",
                           (persona_id, u, hashed, rol_id))
            conexion.commit()
            return True
        except Exception as e:
            conexion.rollback()
            print(f"[ERROR BD] Fallo en add_usuario: {e}")
        finally:
            conexion.close()
    return False


def update_usuario(uid, user, password, rol, foto_bytes=None):
    conexion = conectar()
    if conexion:
        try:
            conexion.start_transaction()
            cursor = conexion.cursor()
            if foto_bytes:
                cursor.execute("UPDATE personas SET nombre=%s, foto=%s WHERE id=%s", (user, foto_bytes, uid))
            else:
                cursor.execute("UPDATE personas SET nombre=%s WHERE id=%s", (user, uid))

            cursor.execute("SELECT id FROM roles WHERE nombre = %s", (rol,))
            rol_id = cursor.fetchone()[0]
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("UPDATE usuarios SET username=%s, password=%s, rol_id=%s WHERE persona_id=%s",
                           (user, hashed, rol_id, uid))
            conexion.commit()
            return True
        except Exception as e:
            conexion.rollback()
            print(f"[ERROR BD] Fallo en update_usuario: {e}")
        finally:
            conexion.close()
    return False


def delete_usuario(uid):
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("UPDATE personas SET activo = 0, fecha_baja = NOW() WHERE id=%s", (uid,))
            conexion.commit()
            return True
        except Exception as e:
            print(f"[ERROR BD] Fallo en delete_usuario: {e}")
        finally:
            conexion.close()
    return False


# --- PRESOS ---
def get_presos():
    conexion = conectar()
    res = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = """
                    SELECT p.id, \
                           CONCAT(p.nombre, ' ', p.apellidos)              as nombre, \
                           pr.delito, \
                           c.codigo                                        as celda,
                           DATE_FORMAT(ac.fecha_ingreso, '%d/%m/%Y %H:%M') as fecha_ingreso, \
                           p.foto
                    FROM personas p
                             JOIN presos pr ON p.id = pr.persona_id
                             LEFT JOIN asignacion_celdas ac ON pr.persona_id = ac.preso_id AND ac.activo = 1
                             LEFT JOIN celdas c ON ac.celda_id = c.id
                    WHERE p.activo = 1 \
                    ORDER BY p.fecha_alta DESC
                    """
            cursor.execute(query)
            datos = cursor.fetchall()
            for d in datos:
                d['foto'] = _convertir_a_base64(d['foto'])
                res.append(d)
        except Exception as e:
            print(f"[ERROR BD] Fallo en get_presos: {e}")
        finally:
            conexion.close()
    return res


def add_preso(nombre_completo, delito, celda_codigo, foto_bytes=None):
    conexion = conectar()
    if conexion:
        try:
            conexion.start_transaction()
            cursor = conexion.cursor()
            partes = nombre_completo.split(" ", 1)
            nombre = partes[0]
            apellidos = partes[1] if len(partes) > 1 else "Desconocido"
            dni = f"P{random.randint(10000, 99999)}Z"
            cursor.execute(
                "INSERT INTO personas (dni, nombre, apellidos, tipo_persona, foto) VALUES (%s, %s, %s, 'PRESO', %s)",
                (dni, nombre, apellidos, foto_bytes))
            persona_id = cursor.lastrowid
            cursor.execute("INSERT INTO presos (persona_id, delito) VALUES (%s, %s)", (persona_id, delito))
            cursor.execute("SELECT id FROM celdas WHERE codigo = %s", (celda_codigo,))
            row = cursor.fetchone()
            celda_id = row[0] if row else 1
            cursor.execute("INSERT INTO asignacion_celdas (preso_id, celda_id) VALUES (%s, %s)", (persona_id, celda_id))
            conexion.commit()
            return True
        except Exception as e:
            conexion.rollback()
            print(f"[ERROR BD] Fallo en add_preso: {e}")
        finally:
            conexion.close()
    return False


def update_preso(pid, dat, foto_bytes=None):
    conexion = conectar()
    if conexion:
        try:
            conexion.start_transaction()
            cursor = conexion.cursor()
            partes = dat.get('nombre', '').split(" ", 1)
            nombre = partes[0]
            apellidos = partes[1] if len(partes) > 1 else "Desconocido"

            if foto_bytes:
                cursor.execute("UPDATE personas SET nombre=%s, apellidos=%s, foto=%s WHERE id=%s",
                               (nombre, apellidos, foto_bytes, pid))
            else:
                cursor.execute("UPDATE personas SET nombre=%s, apellidos=%s WHERE id=%s", (nombre, apellidos, pid))

            cursor.execute("UPDATE presos SET delito=%s WHERE persona_id=%s", (dat.get('delito'), pid))
            cursor.execute("SELECT id FROM celdas WHERE codigo = %s", (dat.get('celda'),))
            nueva_celda_id = cursor.fetchone()[0]
            cursor.execute(
                "UPDATE asignacion_celdas SET activo = 0, fecha_salida = NOW() WHERE preso_id = %s AND activo = 1",
                (pid,))
            cursor.execute("INSERT INTO asignacion_celdas (preso_id, celda_id) VALUES (%s, %s)", (pid, nueva_celda_id))
            conexion.commit()
            return True
        except Exception as e:
            conexion.rollback()
            print(f"[ERROR BD] Fallo en update_preso: {e}")
        finally:
            conexion.close()
    return False


def delete_preso(pid):
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("UPDATE personas SET activo = 0, fecha_baja = NOW() WHERE id=%s", (pid,))
            cursor.execute(
                "UPDATE asignacion_celdas SET activo = 0, fecha_salida = NOW() WHERE preso_id=%s AND activo=1", (pid,))
            conexion.commit()
            return True
        except Exception as e:
            print(f"[ERROR BD] Fallo en delete_preso: {e}")
        finally:
            conexion.close()
    return False


# --- SENSORES Y ACTUADORES ---
def registrar_dato_sensor(datos):
    actualizar_heartbeat_esp32()  # <--- Notifica que el ESP32 está vivo
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre FROM sensores")
            sensores_db = {r['nombre']: r['id'] for r in cursor.fetchall()}
            query = "INSERT INTO sensores_log (timestamp, sensor_id, valor) VALUES (%s, %s, %s)"
            valores = []
            for d in datos:
                sid = sensores_db.get(d['sensor'])
                if sid:
                    num = float(re.search(r"([0-9\.]+)", str(d['valor'])).group(1))
                    valores.append((d['timestamp'], sid, num))
            cursor.executemany(query, valores)
            conexion.commit()
        except Exception as e:
            print(f"[ERROR BD] Fallo en registrar_dato_sensor: {e}")
        finally:
            conexion.close()
    verificar_automatizacion(datos)


def verificar_automatizacion(ultimos_datos):
    config = get_configuracion()
    actuadores = get_estado_actuadores()
    temp_val, luz_val = None, None
    for d in ultimos_datos:
        match = re.search(r"([0-9\.]+)", str(d['valor']))
        if match:
            if "Temperatura" in d['sensor']:
                temp_val = float(match.group(1))
            elif "Luz" in d['sensor']:
                luz_val = float(match.group(1))

    if temp_val is not None and actuadores.get('fan', {}).get('mode') == 'auto':
        if temp_val > config['temp_max']:
            set_estado_actuador('fan', 'on')
        elif temp_val <= config['temp_max']:
            set_estado_actuador('fan', 'off')

    if luz_val is not None and actuadores.get('leds', {}).get('mode') == 'auto':
        if luz_val < config['luz_min']:
            set_estado_actuador('leds', 'on')
        elif luz_val >= config['luz_min']:
            set_estado_actuador('leds', 'off')


def get_configuracion():
    conexion = conectar()
    config = {"temp_max": 28.0, "luz_min": 400.0}
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT clave, valor FROM configuracion")
            for fila in cursor.fetchall():
                config[fila['clave']] = float(fila['valor'])
        except Exception as e:
            print(f"[ERROR BD] Fallo en get_configuracion: {e}")
        finally:
            conexion.close()
    return config


def save_configuracion(data):
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            for k, v in data.items():
                cursor.execute(
                    "INSERT INTO configuracion (clave, valor) VALUES (%s, %s) ON DUPLICATE KEY UPDATE valor = %s",
                    (k, str(v), str(v)))
            conexion.commit()
            return True
        except Exception as e:
            print(f"[ERROR BD] Fallo en save_configuracion: {e}")
        finally:
            conexion.close()
    return False


def get_estado_actuadores():
    conexion = conectar()
    estados = {}
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT uid, label, estado, mode FROM actuadores WHERE activo = 1")
            for fila in cursor.fetchall():
                estados[fila['uid']] = fila
        except Exception as e:
            print(f"[ERROR BD] Fallo en get_estado_actuadores: {e}")
        finally:
            conexion.close()
    return estados


def set_estado_actuador(uid, estado, user_id=None):
    return _actualizar_actuador(uid, estado, user_id)


def toggle_actuador(uid, user_id=None):
    estados = get_estado_actuadores()
    curr = estados.get(uid, {}).get("estado", "cerrada")
    nuevo = "abierta" if curr == "cerrada" else "cerrada"
    return _actualizar_actuador(uid, nuevo, user_id)


def _actualizar_actuador(uid, estado, user_id):
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id, estado FROM actuadores WHERE uid = %s AND activo = 1", (uid,))
            actuador = cursor.fetchone()

            if actuador and actuador['estado'] != estado:
                actuador_id = actuador['id']
                cursor.execute("UPDATE actuadores SET estado = %s WHERE id = %s", (estado, actuador_id))
                cursor.execute("""
                               INSERT INTO historico_actuadores (actuador_id, usuario_id, accion, timestamp)
                               VALUES (%s, %s, %s, NOW())
                               """, (actuador_id, user_id, estado))
                conexion.commit()

                try:
                    ip = LOCAL_CONFIG.get("esp32_ip", "")
                    requests.get(f"http://{ip}/actuadores", params={"dispositivo": uid, "estado": estado}, timeout=2)
                except Exception as e:
                    print(f"[ERROR HARDWARE] ESP32 no detectado en IP {ip} al cambiar estado: {e}")

            return True
        except Exception as e:
            print(f"[ERROR BD] Fallo en _actualizar_actuador: {e}")
        finally:
            conexion.close()
    return False


def toggle_modo_actuador(uid):
    """Alterna entre Auto y Manual para un actuador"""
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT mode FROM actuadores WHERE uid = %s", (uid,))
            res = cursor.fetchone()
            if res:
                nuevo_modo = "manual" if res['mode'] == "auto" else "auto"
                cursor.execute("UPDATE actuadores SET mode = %s WHERE uid = %s", (nuevo_modo, uid))
                conexion.commit()
                return True
        except Exception as e:
            print(f"[ERROR BD] Error en toggle_modo_actuador: {e}")
        finally:
            conexion.close()
    return False


def set_modo_actuador(uid, modo):
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("UPDATE actuadores SET mode = %s WHERE uid = %s", (modo, uid))
            conexion.commit()
            return True
        except Exception as e:
            print(f"[ERROR BD] Fallo en set_modo_actuador: {e}")
        finally:
            conexion.close()
    return False

def get_ultimos_sensores_raw():
    conexion = conectar()
    res = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT sl.timestamp, s.nombre as sensor, sl.valor, s.unidad FROM sensores_log sl JOIN sensores s ON sl.sensor_id = s.id ORDER BY sl.id DESC LIMIT 20")
            for r in cursor.fetchall():
                res.append({"timestamp": r['timestamp'].strftime('%Y-%m-%d %H:%M:%S'), "sensor": r['sensor'],
                            "valor": f"{r['valor']} {r['unidad']}"})
        except Exception as e:
            print(f"[ERROR BD] Fallo en get_ultimos_sensores_raw: {e}")
        finally:
            conexion.close()
    return res[::-1]

# --------- FUNCIONES AÑADIDAS PARA SOLUCIONAR EL CRASH DEL HISTÓRICO ---------

def get_log_sensores_filtrado(horas=24):
    conexion = conectar()
    res = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT sl.timestamp, s.nombre as sensor, sl.valor, s.unidad FROM sensores_log sl JOIN sensores s ON sl.sensor_id = s.id WHERE sl.timestamp >= NOW() - INTERVAL %s HOUR ORDER BY sl.timestamp DESC",
                (horas,))
            for r in cursor.fetchall():
                res.append({"timestamp": r['timestamp'].strftime('%Y-%m-%d %H:%M:%S'), "sensor": r['sensor'],
                            "valor": f"{r['valor']} {r['unidad']}"})
        except Exception as e:
            print(f"[ERROR BD] Fallo en get_log_sensores_filtrado: {e}")
        finally:
            conexion.close()
    return res

def get_log_actuadores_paginado(uid_parcial, limit=50, offset=0):
    conexion = conectar()
    res = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = "SELECT ha.timestamp, a.uid as id, a.label, ha.accion, IFNULL(p.nombre, 'sistema') as usuario FROM historico_actuadores ha JOIN actuadores a ON ha.actuador_id = a.id LEFT JOIN personas p ON ha.usuario_id = p.id WHERE a.uid LIKE %s ORDER BY ha.timestamp DESC LIMIT %s OFFSET %s"
            cursor.execute(query, (f"%{uid_parcial}%", limit, offset))
            for r in cursor.fetchall():
                r['timestamp'] = r['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                res.append(r)
        except Exception as e:
            print(f"[ERROR BD] Fallo en get_log_actuadores_paginado: {e}")
        finally:
            conexion.close()
    return res

def get_promedio_sensores_por_hora():
    conexion = conectar()
    res_dict = defaultdict(list)
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT s.nombre as sensor, DATE_FORMAT(sl.timestamp, '%Y-%m-%d %H:00') as hora, AVG(sl.valor) as promedio, MAX(s.unidad) as unidad FROM sensores_log sl JOIN sensores s ON sl.sensor_id = s.id GROUP BY s.nombre, hora ORDER BY hora ASC")
            for r in cursor.fetchall():
                res_dict[r['sensor']].append({"hora": r['hora'], "valor": f"{r['promedio']:.1f} {r['unidad']}"})
        except Exception as e:
            print(f"[ERROR BD] Fallo en get_promedio_sensores_por_hora: {e}")
        finally:
            conexion.close()
    return dict(res_dict)


def get_consumo_electrico():
    total_w = random.uniform(5, 15)
    return {"total_actual": round(total_w, 2), "media_dia": round(total_w * 0.9, 2),
            "media_mes": round(total_w * 0.8, 2), "detalles": []}


# ==============================================================
# --- SISTEMA DE CHAT CON MYSQL ---
# ==============================================================
def guardar_historial_txt(emisor, receptor, texto):
    fecha_completa = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{fecha_completa}] DE: {emisor} | PARA: {receptor} | MSG: {texto}\n"
    if not os.path.exists("logs_chat"):
        os.makedirs("logs_chat")
    archivo = f"logs_chat/chat_{emisor}.txt"
    try:
        with open(archivo, "a", encoding="utf-8") as f:
            f.write(linea)
    except Exception as e:
        print(f"[ERROR LOCAL] No se pudo guardar log de chat en TXT: {e}")


def enviar_mensaje(emisor, receptor, texto):
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            query = "INSERT INTO mensajes_chat (emisor, receptor, texto, estado) VALUES (%s, %s, %s, 'RECIBIDO')"
            cursor.execute(query, (emisor, receptor, texto))
            conexion.commit()
            guardar_historial_txt(emisor, receptor, texto)
            return True
        except Exception as e:
            print(f"[ERROR BD] Fallo enviando mensaje DB: {e}")
        finally:
            conexion.close()
    return False


def get_contactos_chat(mi_usuario):
    conexion = conectar()
    contactos = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = """
                    SELECT CASE WHEN emisor = %s THEN receptor ELSE emisor END                                    as contacto, \
                           SUM(CASE \
                                   WHEN receptor = %s AND estado IN ('RECIBIDO', 'ENTREGADO') THEN 1 \
                                   ELSE 0 END)                                                                    as no_leidos
                    FROM mensajes_chat \
                    WHERE emisor = %s \
                       OR receptor = %s \
                    GROUP BY contacto \
                    ORDER BY MAX(timestamp) DESC
                    """
            cursor.execute(query, (mi_usuario, mi_usuario, mi_usuario, mi_usuario))
            contactos = cursor.fetchall()
        except Exception as e:
            print(f"[ERROR BD] Fallo en get_contactos_chat: {e}")
        finally:
            conexion.close()
    return contactos


def get_mensajes_chat(usuario1, usuario2):
    conexion = conectar()
    mensajes = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = """
                    SELECT emisor, receptor, texto, estado, timestamp
                    FROM mensajes_chat
                    WHERE (emisor = %s \
                      AND receptor = %s) \
                       OR (emisor = %s \
                      AND receptor = %s)
                    ORDER BY timestamp ASC
                    """
            cursor.execute(query, (usuario1, usuario2, usuario2, usuario1))
            resultados = cursor.fetchall()
            for r in resultados:
                r['fecha'] = r['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                mensajes.append(r)
        except Exception as e:
            print(f"[ERROR BD] Fallo en get_mensajes_chat: {e}")
        finally:
            conexion.close()
    return mensajes


def marcar_mensajes_entregados(mi_usuario):
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            query = "UPDATE mensajes_chat SET estado = 'ENTREGADO' WHERE receptor = %s AND estado = 'RECIBIDO'"
            cursor.execute(query, (mi_usuario,))
            conexion.commit()
        except Exception as e:
            print(f"[ERROR BD] Fallo marcando entregados: {e}")
        finally:
            conexion.close()


def marcar_mensajes_leidos(emisor_contacto, mi_usuario):
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            query = "UPDATE mensajes_chat SET estado = 'LEIDO' WHERE emisor = %s AND receptor = %s AND estado IN ('RECIBIDO', 'ENTREGADO')"
            cursor.execute(query, (emisor_contacto, mi_usuario))
            conexion.commit()
        except Exception as e:
            print(f"[ERROR BD] Fallo marcando leidos: {e}")
        finally:
            conexion.close()