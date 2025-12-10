import json
import os
import re
import time
from datetime import datetime, timedelta
from collections import defaultdict

# --- Ubicaciones de los archivos JSON ---
USUARIOS_FILE = 'modelo/usuarios.json'
PRESOS_FILE = 'modelo/presos.json'
ACTUADORES_FILE = 'modelo/actuadores_estado.json'
SENSORES_FILE = 'modelo/sensores_log.json'
HISTORICO_ACTUADORES_FILE = 'modelo/puertas_log.json'
CONFIG_FILE = 'modelo/configuracion.json'


# --- Funciones de Inicialización ---
def inicializar_archivos_json():
    if not os.path.exists(USUARIOS_FILE):
        usuarios_default = [{"user": "comisario", "password": "1234", "rol": "comisario"}]
        _escribir_json(USUARIOS_FILE, usuarios_default)
    if not os.path.exists(PRESOS_FILE): _escribir_json(PRESOS_FILE, [])
    if not os.path.exists(ACTUADORES_FILE):
        actuadores_default = {
            "door-1": {"estado": "cerrada", "label": "P1"},
            "door-2": {"estado": "cerrada", "label": "P2"},
            "door-3": {"estado": "cerrada", "label": "P3"},
            "door-4": {"estado": "cerrada", "label": "P4"},
            "leds": {"estado": "off"},
            "fan": {"estado": "off"}
        }
        _escribir_json(ACTUADORES_FILE, actuadores_default)
    if not os.path.exists(SENSORES_FILE): _escribir_json(SENSORES_FILE, [])
    if not os.path.exists(HISTORICO_ACTUADORES_FILE): _escribir_json(HISTORICO_ACTUADORES_FILE, [])

    if not os.path.exists(CONFIG_FILE):
        config_default = {"temp_max": 28.0, "luz_min": 400.0}
        _escribir_json(CONFIG_FILE, config_default)


# --- Funciones Auxiliares ---
def _leer_json(archivo):
    intentos = 3
    while intentos > 0:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read().strip()
                if not contenido: return []
                return json.loads(contenido)
        except (json.JSONDecodeError, IOError):
            time.sleep(0.1)
            intentos -= 1
        except FileNotFoundError:
            return [] if 'lista' in archivo or 'log' in archivo else {}
    return [] if 'lista' in archivo or 'log' in archivo else {}


def _escribir_json(archivo, data):
    try:
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except IOError:
        pass


# --- LOGICA USUARIOS/PRESOS ---
def validar_usuario(u, p):
    for user in _leer_json(USUARIOS_FILE):
        if user['user'] == u and user['password'] == p: return user['rol']
    return None


def get_usuarios(): return _leer_json(USUARIOS_FILE)


def add_usuario(u, p, r):
    users = _leer_json(USUARIOS_FILE)
    if any(x['user'] == u for x in users): return False
    users.append({"user": u, "password": p, "rol": r})
    _escribir_json(USUARIOS_FILE, users)
    return True


def get_presos(): return _leer_json(PRESOS_FILE)


def add_preso(n, d, c="Sin asignar"):
    presos = _leer_json(PRESOS_FILE)
    nid = (max(p["id"] for p in presos) + 1) if presos else 1
    presos.append(
        {"id": nid, "nombre": n, "delito": d, "celda": c, "fecha_ingreso": datetime.now().strftime("%d/%m/%Y %H:%M")})
    _escribir_json(PRESOS_FILE, presos)
    return True


def delete_preso(pid):
    presos = [p for p in _leer_json(PRESOS_FILE) if p['id'] != pid]
    _escribir_json(PRESOS_FILE, presos)
    return True


def update_preso(pid, datos):
    presos = _leer_json(PRESOS_FILE)
    for p in presos:
        if p['id'] == pid:
            p.update(datos)
            _escribir_json(PRESOS_FILE, presos)
            return True
    return False


# --- CONFIGURACIÓN Y AUTOMATIZACIÓN ---
def get_configuracion(): return _leer_json(CONFIG_FILE)


def save_configuracion(nuevos_datos):
    _escribir_json(CONFIG_FILE, nuevos_datos)
    return True


def verificar_automatizacion(ultimos_datos_sensores):
    config = get_configuracion()
    umbral_temp = float(config.get("temp_max", 28.0))
    umbral_luz = float(config.get("luz_min", 400.0))
    actuadores = _leer_json(ACTUADORES_FILE)

    temp_val = None
    luz_val = None

    for dato in ultimos_datos_sensores:
        try:
            match = re.search(r"([0-9\.]+)", str(dato['valor']))
            if match:
                val_num = float(match.group(1))
                if "Temperatura" in dato['sensor']:
                    temp_val = val_num
                elif "Luz" in dato['sensor']:
                    luz_val = val_num
        except:
            continue

    if temp_val is not None:
        estado_fan_actual = actuadores.get('fan', {}).get('estado', 'off')
        if temp_val > umbral_temp and estado_fan_actual == "off":
            set_estado_actuador("fan", "on", "AUTO-SISTEMA")
        elif temp_val <= umbral_temp and estado_fan_actual == "on":
            set_estado_actuador("fan", "off", "AUTO-SISTEMA")

    if luz_val is not None:
        estado_led_actual = actuadores.get('leds', {}).get('estado', 'off')
        if luz_val < umbral_luz and estado_led_actual == "off":
            set_estado_actuador("leds", "on", "AUTO-SISTEMA")
        elif luz_val >= umbral_luz and estado_led_actual == "on":
            set_estado_actuador("leds", "off", "AUTO-SISTEMA")


# --- SENSORES ---
def registrar_dato_sensor(datos_nuevos):
    log_actual = _leer_json(SENSORES_FILE)
    log_actual.extend(datos_nuevos)
    if len(log_actual) > 1000: log_actual = log_actual[-1000:]
    _escribir_json(SENSORES_FILE, log_actual)
    verificar_automatizacion(datos_nuevos)


def get_log_sensores_filtrado(horas=24):
    todos = _leer_json(SENSORES_FILE)
    filtrados = []
    limite = datetime.now() - timedelta(hours=horas)
    for log in todos:
        try:
            if datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S") >= limite:
                filtrados.append(log)
        except:
            continue
    return filtrados


def get_ultimos_sensores_raw():
    """
    NUEVA FUNCIÓN: Obtiene los últimos 100 registros SIN filtrar por fecha.
    Esto asegura que siempre lleguen datos al dashboard.
    """
    todos = _leer_json(SENSORES_FILE)
    if not todos: return []
    # Devolvemos los últimos 100
    return todos[-100:]


def get_promedio_sensores_por_hora():
    logs = _leer_json(SENSORES_FILE)
    agrupacion = defaultdict(list)
    for log in logs:
        try:
            dt = datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S")
            key = (log['sensor'], dt.strftime("%Y-%m-%d %H:00"))
            match = re.match(r"([0-9\.]+)\s*(.*)", str(log['valor']))
            if match: agrupacion[(*key, match.group(2))].append(float(match.group(1)))
        except:
            continue
    res = defaultdict(list)
    for (sensor, hora, unidad), vals in sorted(agrupacion.items(), key=lambda x: x[0][1]):
        prom = sum(vals) / len(vals)
        val_fmt = f"{int(prom) if prom.is_integer() else f'{prom:.1f}'} {unidad}"
        res[sensor].append({"hora": hora, "valor": val_fmt})
    return dict(res)


# --- ACTUADORES ---
def get_log_historico_completo(dias=7): return _leer_json(HISTORICO_ACTUADORES_FILE)


def get_estado_actuadores(): return _leer_json(ACTUADORES_FILE)


def set_estado_actuador(actuador_id, nuevo_estado, usuario="sistema"):
    return _actualizar_actuador(actuador_id, nuevo_estado, usuario)


def toggle_actuador(actuador_id, usuario="sistema"):
    estados = _leer_json(ACTUADORES_FILE)
    if actuador_id not in estados: return False
    nuevo = "cerrada" if estados[actuador_id]['estado'] == "abierta" else "abierta"
    return _actualizar_actuador(actuador_id, nuevo, usuario)


def _actualizar_actuador(actuador_id, nuevo_estado, usuario):
    estados = _leer_json(ACTUADORES_FILE)
    if actuador_id in estados:
        if estados[actuador_id]['estado'] == nuevo_estado: return True
        estados[actuador_id]['estado'] = nuevo_estado
        _escribir_json(ACTUADORES_FILE, estados)
        log = _leer_json(HISTORICO_ACTUADORES_FILE)
        lbl = estados[actuador_id].get("label", actuador_id)
        if actuador_id == "leds": lbl = "Iluminación"
        if actuador_id == "fan": lbl = "Ventilación"
        log.append({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "id": actuador_id, "label": lbl,
                    "accion": nuevo_estado, "usuario": usuario})
        _escribir_json(HISTORICO_ACTUADORES_FILE, log)
        return True
    return False


inicializar_archivos_json()