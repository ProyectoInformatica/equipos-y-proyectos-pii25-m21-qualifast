import mysql.connector
import re
import time
import os
import random
import csv
from datetime import datetime, timedelta
from collections import defaultdict

# --- CONFIGURACIÓN DE BASE DE DATOS ---
DB_CONFIG = {
    'host': 'localhost',
    'database': 'comisaria_db',
    'user': 'root',
    'password': '1234'
}

_CACHE_CONSUMO = {"timestamp": 0, "data": {}}

def conectar():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

# --- CONFIGURACIÓN ---
def get_configuracion():
    conexion = conectar()
    config = {"temp_max": 28.0, "luz_min": 400.0}
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT clave, valor FROM configuracion")
        for fila in cursor.fetchall():
            try:
                config[fila['clave']] = float(fila['valor'])
            except ValueError:
                config[fila['clave']] = fila['valor']
        conexion.close()
    return config

def save_configuracion(data):
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        for k, v in data.items():
            cursor.execute("""
                INSERT INTO configuracion (clave, valor) VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE valor = %s
            """, (k, str(v), str(v)))
        conexion.commit()
        conexion.close()
        return True
    return False

# --- AUTOMATIZACIÓN ---
def verificar_automatizacion(ultimos_datos):
    config = get_configuracion()
    umbral_temp = float(config.get("temp_max", 28.0))
    umbral_luz = float(config.get("luz_min", 400.0))

    actuadores = get_estado_actuadores()

    temp_val, luz_val = None, None
    for d in ultimos_datos:
        try:
            val_str = str(d['valor'])
            match = re.search(r"([0-9\.]+)", val_str)
            if match:
                num = float(match.group(1))
                if "Temperatura" in d['sensor']: temp_val = num
                elif "Luz" in d['sensor']: luz_val = num
        except: continue

    modo_fan = actuadores.get('fan', {}).get('mode', 'manual')
    if modo_fan == "auto" and temp_val is not None:
        estado_fan = actuadores.get('fan', {}).get('estado', 'off')
        if temp_val > umbral_temp and estado_fan == "off":
            set_estado_actuador("fan", "on", "AUTO-SISTEMA")
        elif temp_val <= umbral_temp and estado_fan == "on":
            set_estado_actuador("fan", "off", "AUTO-SISTEMA")

    modo_led = actuadores.get('leds', {}).get('mode', 'manual')
    if modo_led == "auto" and luz_val is not None:
        estado_led = actuadores.get('leds', {}).get('estado', 'off')
        if luz_val < umbral_luz and estado_led == "off":
            set_estado_actuador("leds", "on", "AUTO-SISTEMA")
        elif luz_val >= umbral_luz and estado_led == "on":
            set_estado_actuador("leds", "off", "AUTO-SISTEMA")

# --- SENSORES ---
def registrar_dato_sensor(datos):
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        query = "INSERT INTO sensores_log (timestamp, sensor, valor) VALUES (%s, %s, %s)"
        valores = [(d['timestamp'], d['sensor'], str(d['valor'])) for d in datos]
        cursor.executemany(query, valores)
        conexion.commit()
        conexion.close()
    verificar_automatizacion(datos)

def _formatear_fecha(fecha_db):
    """Convierte el objeto datetime de MySQL a texto para la app Flet."""
    if isinstance(fecha_db, datetime):
        return fecha_db.strftime('%Y-%m-%d %H:%M:%S')
    return str(fecha_db)

def get_ultimos_sensores_raw():
    conexion = conectar()
    res = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sensores_log ORDER BY id DESC LIMIT 20")
        res = [{"timestamp": _formatear_fecha(r["timestamp"]), "sensor": r["sensor"], "valor": r["valor"]} for r in cursor.fetchall()]
        conexion.close()
    return res[::-1]

def get_log_sensores_filtrado(horas=24):
    conexion = conectar()
    res = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        # Quitamos DATE_FORMAT de la consulta SQL para evitar problemas con los %s
        query = "SELECT timestamp, sensor, valor FROM sensores_log WHERE timestamp >= NOW() - INTERVAL %s HOUR ORDER BY timestamp DESC LIMIT 2000"
        cursor.execute(query, (horas,))
        for r in cursor.fetchall():
            r['timestamp'] = _formatear_fecha(r['timestamp'])
            res.append(r)
        conexion.close()
    return res

def get_promedio_sensores_por_hora():
    conexion = conectar()
    logs = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT timestamp, sensor, valor FROM sensores_log ORDER BY id DESC LIMIT 3000")
        for r in cursor.fetchall():
            r['timestamp'] = _formatear_fecha(r['timestamp'])
            logs.append(r)
        conexion.close()

    logs.reverse()
    data = defaultdict(list)
    for l in logs:
        try:
            dt = datetime.strptime(l['timestamp'], "%Y-%m-%d %H:%M:%S")
            key = (l['sensor'], dt.strftime("%Y-%m-%d %H:00"))
            match = re.search(r"([0-9\.]+)\s*(.*)", str(l['valor']))
            if match: data[(*key, match.group(2))].append(float(match.group(1)))
        except:
            continue
    res = defaultdict(list)
    for (sen, hora, unid), vals in sorted(data.items(), key=lambda x: x[0][1]):
        prom = sum(vals) / len(vals)
        fmt = f"{int(prom) if prom.is_integer() else f'{prom:.1f}'} {unid}"
        res[sen].append({"hora": hora, "valor": fmt})
    return dict(res)

# --- ACTUADORES ---
def get_estado_actuadores():
    conexion = conectar()
    estados = {}
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT uid, label, estado, mode FROM actuadores_estado")
        for fila in cursor.fetchall():
            estados[fila['uid']] = {"estado": fila['estado'], "label": fila['label'], "mode": fila['mode']}
        conexion.close()
    return estados

def get_log_historico_completo(dias=7):
    conexion = conectar()
    res = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        # Formateo manejado en Python
        cursor.execute("SELECT timestamp, uid as id, label, accion, usuario FROM historico_actuadores WHERE timestamp >= NOW() - INTERVAL %s DAY ORDER BY id DESC LIMIT 5000", (dias,))
        for r in cursor.fetchall():
            r['timestamp'] = _formatear_fecha(r['timestamp'])
            res.append(r)
        conexion.close()
    return res

def toggle_actuador(uid, user="sistema"):
    estados = get_estado_actuadores()
    curr = estados.get(uid, {}).get("estado", "cerrada")
    nuevo = "abierta" if curr == "cerrada" else "cerrada"
    return _actualizar_actuador(uid, nuevo, user)

def set_estado_actuador(uid, estado, user="sistema"):
    return _actualizar_actuador(uid, estado, user)

def set_modo_actuador(uid, modo):
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("UPDATE actuadores_estado SET mode = %s WHERE uid = %s", (modo, uid))
        conexion.commit()
        conexion.close()
        return True
    return False

def _actualizar_actuador(uid, estado, user):
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT label, estado FROM actuadores_estado WHERE uid = %s", (uid,))
        actuador = cursor.fetchone()

        if actuador and actuador['estado'] != estado:
            cursor.execute("UPDATE actuadores_estado SET estado = %s WHERE uid = %s", (estado, uid))

            lbl = actuador['label']
            if uid == "leds": lbl = "Iluminación"
            if uid == "fan": lbl = "Ventilación"

            cursor.execute("""
                INSERT INTO historico_actuadores (timestamp, uid, label, accion, usuario)
                VALUES (%s, %s, %s, %s, %s)
            """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), uid, lbl, estado, user))

            conexion.commit()
        conexion.close()
        return True
    return False

# --- CONSUMO ELÉCTRICO ---
def get_consumo_electrico():
    global _CACHE_CONSUMO
    tiempo_actual = time.time()
    if tiempo_actual - _CACHE_CONSUMO["timestamp"] < 5.0 and _CACHE_CONSUMO["data"]:
        return _CACHE_CONSUMO["data"]

    dispositivos = []
    total_watts = 0.0

    for nombre in ["DHT11 (Temp/Hum)", "LDR (Luz)", "MQ-2 (Gas)", "MQ-135 (Aire)", "Camara IP"]:
        consumo = round(random.uniform(2.0, 4.5), 2) if "Camara" in nombre else round(random.uniform(0.1, 0.6), 2)
        dispositivos.append({"nombre": nombre, "watts": consumo, "estado": "Activo"})
        total_watts += consumo

    actuadores = get_estado_actuadores()

    esp_w = round(random.uniform(0.8, 1.5), 2)
    dispositivos.append({"nombre": "Controlador ESP32", "watts": esp_w, "estado": "Online"})
    total_watts += esp_w

    estado_led = actuadores.get("leds", {}).get("estado", "off")
    if estado_led == "on":
        led_w, st_txt = round(random.uniform(8.0, 12.0), 2), "ON"
    else:
        led_w, st_txt = round(random.uniform(0.1, 0.3), 2), "Standby"
    dispositivos.append({"nombre": "Iluminación LED", "watts": led_w, "estado": st_txt})
    total_watts += led_w

    estado_fan = actuadores.get("fan", {}).get("estado", "off")
    if estado_fan == "on":
        fan_w, st_txt = round(random.uniform(3.5, 6.0), 2), "ON"
    else:
        fan_w, st_txt = 0.0, "OFF"
    dispositivos.append({"nombre": "Ventilador DC", "watts": fan_w, "estado": st_txt})
    total_watts += fan_w

    if random.random() > 0.8:
        motor_w, st_mot = round(random.uniform(4.0, 7.0), 2), "Moviendo"
    else:
        motor_w, st_mot = 0.1, "Reposo"
    dispositivos.append({"nombre": "Servos Puertas", "watts": motor_w, "estado": st_mot})
    total_watts += motor_w

    media_dia = total_watts * random.uniform(0.9, 1.1)
    media_mes = total_watts * random.uniform(0.8, 1.0)

    datos_finales = {
        "total_actual": round(total_watts, 2),
        "media_dia": round(media_dia, 2),
        "media_mes": round(media_mes, 2),
        "detalles": dispositivos
    }
    _CACHE_CONSUMO["timestamp"] = tiempo_actual
    _CACHE_CONSUMO["data"] = datos_finales
    return datos_finales

# --- USUARIOS/PRESOS ---
def validar_usuario(u, p):
    conexion = conectar()
    rol = None
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT rol FROM usuarios WHERE user = %s AND password = %s", (u, p))
        usuario = cursor.fetchone()
        if usuario: rol = usuario['rol']
        conexion.close()
    return rol

def get_usuarios():
    conexion = conectar()
    res = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT user, password, rol FROM usuarios")
        res = cursor.fetchall()
        conexion.close()
    return res

def add_usuario(u, p, r):
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (user, password, rol) VALUES (%s, %s, %s)", (u, p, r))
            conexion.commit()
            res = True
        except mysql.connector.IntegrityError:
            res = False
        conexion.close()
        return res
    return False

def get_presos():
    conexion = conectar()
    res = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, delito, celda, fecha_ingreso FROM presos")
        res = cursor.fetchall()
        conexion.close()
    return res

def add_preso(n, d, c):
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        cursor.execute("INSERT INTO presos (nombre, delito, celda, fecha_ingreso) VALUES (%s, %s, %s, %s)", (n, d, c, fecha))
        conexion.commit()
        conexion.close()
        return True
    return False

def update_preso(pid, dat):
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("UPDATE presos SET nombre=%s, delito=%s, celda=%s WHERE id=%s",
                       (dat.get('nombre'), dat.get('delito'), dat.get('celda'), pid))
        conexion.commit()
        conexion.close()
        return True
    return False

def delete_preso(pid):
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM presos WHERE id=%s", (pid,))
        conexion.commit()
        conexion.close()
        return True
    return False

# Exportar opcionalmente para evitar cuelgues si está asignado a un botón
def exportar_a_csv(nombre_archivo_json, ruta_destino):
    pass