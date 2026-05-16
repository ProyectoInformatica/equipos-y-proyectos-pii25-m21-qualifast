import re
import requests
import random
from datetime import datetime
from collections import defaultdict
from modelo.dao.conexion_db import conectar, LOCAL_CONFIG

def get_all_sensores_log_csv():
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = "SELECT sl.timestamp, s.nombre, sl.valor, s.unidad FROM sensores_log sl JOIN sensores s ON sl.sensor_id = s.id ORDER BY sl.timestamp ASC"
            cursor.execute(query)
            res = []
            for r in cursor.fetchall():
                if r['timestamp']: r['timestamp'] = r['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                res.append(r)
            return res
        finally: conexion.close()
    return []

def get_all_actuadores_log_csv():
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = "SELECT ha.timestamp, a.label as componente, ha.accion as estado, IFNULL(p.nombre, 'sistema') as usuario FROM historico_actuadores ha JOIN actuadores a ON ha.actuador_id = a.id LEFT JOIN personas p ON ha.usuario_id = p.id ORDER BY ha.timestamp ASC"
            cursor.execute(query)
            res = []
            for r in cursor.fetchall():
                if r['timestamp']: r['timestamp'] = r['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                res.append(r)
            return res
        finally: conexion.close()
    return []


def obtener_estado_esp32():
    # 1. Leemos la configuración para saber el delay esperado
    config = get_configuracion()
    intervalo_segundos = config.get("intervalo_muestreo", 5.0)

    # Le damos un margen de gracia de 10 segundos extra por si hay lag en el WiFi
    margen_gracia = intervalo_segundos + 10.0

    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT MAX(timestamp) as ultimo FROM sensores_log")
            res = cursor.fetchone()
            if res and res['ultimo']:
                diferencia = datetime.now() - res['ultimo']
                # Si el tiempo transcurrido es menor que nuestro margen, sigue online
                return diferencia.total_seconds() < margen_gracia
        except:
            pass
        finally:
            conexion.close()
    return False

def registrar_dato_sensor(datos):
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
    config = {"temp_max": 28.0, "luz_min": 400.0, "intervalo_muestreo": 5.0}
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT clave, valor FROM configuracion")
            for fila in cursor.fetchall():
                config[fila['clave']] = float(fila['valor'])
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
        finally:
            conexion.close()
    return estados

def toggle_actuador(uid, user_id=None):
    estados = get_estado_actuadores()
    curr = estados.get(uid, {}).get("estado", "cerrada")
    nuevo = "abierta" if curr == "cerrada" else "cerrada"
    return _actualizar_actuador(uid, nuevo, user_id)

def set_estado_actuador(uid, estado, user_id=None):
    return _actualizar_actuador(uid, estado, user_id)

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
                cursor.execute("INSERT INTO historico_actuadores (actuador_id, usuario_id, accion, timestamp) VALUES (%s, %s, %s, NOW())",
                               (actuador_id, user_id, estado))
                conexion.commit()

                try:
                    ip = LOCAL_CONFIG.get("esp32_ip", "")
                    requests.get(f"http://{ip}/actuadores", params={"dispositivo": uid, "estado": estado}, timeout=2)
                except: pass
            return True
        finally:
            conexion.close()
    return False

def toggle_modo_actuador(uid):
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
        finally:
            conexion.close()
    return False

def get_ultimos_sensores_raw():
    conexion = conectar()
    res = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT sl.timestamp, s.nombre as sensor, sl.valor, s.unidad FROM sensores_log sl JOIN sensores s ON sl.sensor_id = s.id ORDER BY sl.id DESC LIMIT 20")
            for r in cursor.fetchall():
                res.append({"timestamp": r['timestamp'].strftime('%Y-%m-%d %H:%M:%S'), "sensor": r['sensor'],
                            "valor": f"{r['valor']} {r['unidad']}"})
        finally:
            conexion.close()
    return res[::-1]

def get_promedio_sensores_por_hora():
    conexion = conectar()
    res_dict = defaultdict(list)
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT s.nombre as sensor, DATE_FORMAT(sl.timestamp, '%Y-%m-%d %H:00') as hora, AVG(sl.valor) as promedio, MAX(s.unidad) as unidad FROM sensores_log sl JOIN sensores s ON sl.sensor_id = s.id GROUP BY s.nombre, hora ORDER BY hora ASC")
            for r in cursor.fetchall():
                res_dict[r['sensor']].append({"hora": r['hora'], "valor": f"{r['promedio']:.1f} {r['unidad']}"})
        finally:
            conexion.close()
    return dict(res_dict)

def get_consumo_electrico():
    # 1. Obtenemos configuración para el delay
    config = get_configuracion()
    intervalo_segundos = config.get("intervalo_muestreo", 5.0)
    margen_gracia = intervalo_segundos + 10.0

    actuadores = get_estado_actuadores()
    esp32_activo = obtener_estado_esp32()

    consumo_total = 0.0
    detalles = []

    # 2. Consumo exclusivo de la Placa ESP32
    if esp32_activo:
        consumo_total += 1.5
        detalles.append({"nombre": "Placa Controlador ESP32", "consumo": "1.5 W", "estado": "Activo"})
    else:
        detalles.append({"nombre": "Placa Controlador ESP32", "consumo": "0.0 W", "estado": "Inactivo"})

    # 3. Consumo de Actuadores (Luces y Ventilador)
    if actuadores.get("leds", {}).get("estado") == "on":
        consumo_total += 15.0
        detalles.append({"nombre": "Iluminación Central (LEDs)", "consumo": "15.0 W", "estado": "ON"})
    else:
        detalles.append({"nombre": "Iluminación Central (LEDs)", "consumo": "0.0 W", "estado": "OFF"})

    if actuadores.get("fan", {}).get("estado") == "on":
        consumo_total += 5.5
        detalles.append({"nombre": "Ventilación (Motor DC)", "consumo": "5.5 W", "estado": "ON"})
    else:
        detalles.append({"nombre": "Ventilación (Motor DC)", "consumo": "0.0 W", "estado": "OFF"})

    # 4. Consumo Individual de Sensores (Comprobación en tiempo real)
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            # LEFT JOIN para asegurar que listamos todos los sensores, incluso si no tienen datos
            query = "SELECT s.nombre, MAX(sl.timestamp) as ultimo FROM sensores s LEFT JOIN sensores_log sl ON s.id = sl.sensor_id GROUP BY s.nombre"
            cursor.execute(query)
            estado_sensores = cursor.fetchall()

            # Definimos el consumo estimado en vatios (W) para cada tipo de sensor
            consumo_por_sensor = {
                "DHT11 - Temperatura": 0.1,
                "DHT11 - Humedad": 0.1,
                "LDR - Luz": 0.05,
                "MQ-2 - Humo": 0.8,
                "MQ-135 - Aire": 0.8
            }

            for s in estado_sensores:
                nombre = s['nombre']
                ultimo_dato = s['ultimo']
                is_online = False

                if ultimo_dato:
                    diferencia = datetime.now() - ultimo_dato
                    if diferencia.total_seconds() < margen_gracia:
                        is_online = True

                w_sensor = consumo_por_sensor.get(nombre, 0.2)  # 0.2W por defecto si hay alguno nuevo

                if is_online:
                    consumo_total += w_sensor
                    detalles.append({"nombre": f"Sensor: {nombre}", "consumo": f"{w_sensor} W", "estado": "Activo"})
                else:
                    detalles.append({"nombre": f"Sensor: {nombre}", "consumo": "0.0 W", "estado": "Inactivo"})
        except Exception as e:
            print(f"[ERROR BD] Fallo calculando consumo individual de sensores: {e}")
        finally:
            conexion.close()

    return {
        "total_actual": round(consumo_total, 2),
        "media_dia": round(consumo_total * 0.85, 2),
        "media_mes": round(consumo_total * 0.70, 2),
        "detalles": detalles
    }


def get_log_actuadores_paginado(uid_parcial, limit=50, ultimo_timestamp=None):
    conexion = conectar()
    res = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            if ultimo_timestamp:
                # ALGORITMO DE AVANCE RÁPIDO (Keyset Pagination)
                query = "SELECT ha.timestamp, a.uid as id, a.label, ha.accion, IFNULL(p.nombre, 'sistema') as usuario FROM historico_actuadores ha JOIN actuadores a ON ha.actuador_id = a.id LEFT JOIN personas p ON ha.usuario_id = p.id WHERE a.uid LIKE %s AND ha.timestamp < %s ORDER BY ha.timestamp DESC LIMIT %s"
                cursor.execute(query, (f"%{uid_parcial}%", ultimo_timestamp, limit))
            else:
                query = "SELECT ha.timestamp, a.uid as id, a.label, ha.accion, IFNULL(p.nombre, 'sistema') as usuario FROM historico_actuadores ha JOIN actuadores a ON ha.actuador_id = a.id LEFT JOIN personas p ON ha.usuario_id = p.id WHERE a.uid LIKE %s ORDER BY ha.timestamp DESC LIMIT %s"
                cursor.execute(query, (f"%{uid_parcial}%", limit))

            for r in cursor.fetchall():
                r['timestamp'] = r['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                res.append(r)
        except Exception as e:
            print(f"[ERROR BD] Fallo en avance rápido: {e}")
        finally:
            conexion.close()
    return res