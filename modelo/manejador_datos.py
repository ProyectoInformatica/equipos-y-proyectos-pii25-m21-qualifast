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

# --- CACHÉ EN MEMORIA ---
_CACHE_ACTUADORES = {}
_CACHE_SENSORES = []


# --- Funciones de Inicialización ---
def inicializar_archivos_json():
    global _CACHE_ACTUADORES, _CACHE_SENSORES

    if not os.path.exists(USUARIOS_FILE):
        _escribir_json(USUARIOS_FILE, [{"user": "comisario", "password": "1234", "rol": "comisario"}])
    if not os.path.exists(PRESOS_FILE): _escribir_json(PRESOS_FILE, [])

    if not os.path.exists(ACTUADORES_FILE):
        # AHORA INCLUYEN "mode": "auto" POR DEFECTO
        actuadores_default = {
            "door-1": {"estado": "cerrada", "label": "P1", "mode": "manual"},  # Puertas suelen ser manuales/rfid
            "door-2": {"estado": "cerrada", "label": "P2", "mode": "manual"},
            "door-3": {"estado": "cerrada", "label": "P3", "mode": "manual"},
            "door-4": {"estado": "cerrada", "label": "P4", "mode": "manual"},
            "leds": {"estado": "off", "mode": "auto"},
            "fan": {"estado": "off", "mode": "auto"}
        }
        _escribir_json(ACTUADORES_FILE, actuadores_default)

    if not os.path.exists(SENSORES_FILE): _escribir_json(SENSORES_FILE, [])
    if not os.path.exists(HISTORICO_ACTUADORES_FILE): _escribir_json(HISTORICO_ACTUADORES_FILE, [])
    if not os.path.exists(CONFIG_FILE):
        _escribir_json(CONFIG_FILE, {"temp_max": 28.0, "luz_min": 400.0})

    # Cargar caché inicial desde disco
    _CACHE_ACTUADORES = _leer_json(ACTUADORES_FILE)
    _CACHE_SENSORES = _leer_json(SENSORES_FILE)
    if len(_CACHE_SENSORES) > 200:
        _CACHE_SENSORES = _CACHE_SENSORES[-200:]


# --- Funciones Auxiliares ---
def _leer_json(archivo):
    intentos = 3
    while intentos > 0:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read().strip()
                if not contenido: return [] if 'lista' in archivo or 'log' in archivo else {}
                return json.loads(contenido)
        except (json.JSONDecodeError, IOError):
            time.sleep(0.05)
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


# --- AUTOMATIZACIÓN ---
def get_configuracion(): return _leer_json(CONFIG_FILE)


def save_configuracion(data):
    _escribir_json(CONFIG_FILE, data)
    return True


def verificar_automatizacion(ultimos_datos):
    """Lógica de control automático revisada."""
    config = get_configuracion()
    umbral_temp = float(config.get("temp_max", 28.0))
    umbral_luz = float(config.get("luz_min", 400.0))

    global _CACHE_ACTUADORES
    actuadores = _CACHE_ACTUADORES

    temp_val, luz_val = None, None
    for d in ultimos_datos:
        try:
            val_str = str(d['valor'])
            match = re.search(r"([0-9\.]+)", val_str)
            if match:
                num = float(match.group(1))
                if "Temperatura" in d['sensor']:
                    temp_val = num
                elif "Luz" in d['sensor']:
                    luz_val = num
        except:
            continue

    cambio = False

    # Ventilador - SOLO SI ESTÁ EN MODO AUTO
    modo_fan = actuadores.get('fan', {}).get('mode', 'auto')
    if modo_fan == "auto" and temp_val is not None:
        estado_fan = actuadores.get('fan', {}).get('estado', 'off')
        if temp_val > umbral_temp and estado_fan == "off":
            set_estado_actuador("fan", "on", "AUTO-SISTEMA")
            cambio = True
        elif temp_val <= umbral_temp and estado_fan == "on":
            set_estado_actuador("fan", "off", "AUTO-SISTEMA")
            cambio = True

    # Luces - SOLO SI ESTÁ EN MODO AUTO
    modo_led = actuadores.get('leds', {}).get('mode', 'auto')
    if modo_led == "auto" and luz_val is not None:
        estado_led = actuadores.get('leds', {}).get('estado', 'off')
        if luz_val < umbral_luz and estado_led == "off":
            set_estado_actuador("leds", "on", "AUTO-SISTEMA")
            cambio = True
        elif luz_val >= umbral_luz and estado_led == "on":
            set_estado_actuador("leds", "off", "AUTO-SISTEMA")
            cambio = True


# --- SENSORES ---
def registrar_dato_sensor(datos):
    global _CACHE_SENSORES
    _CACHE_SENSORES.extend(datos)
    if len(_CACHE_SENSORES) > 200:
        _CACHE_SENSORES = _CACHE_SENSORES[-200:]

    log_disco = _leer_json(SENSORES_FILE)
    log_disco.extend(datos)
    if len(log_disco) > 1000: log_disco = log_disco[-1000:]
    _escribir_json(SENSORES_FILE, log_disco)

    verificar_automatizacion(datos)


def get_ultimos_sensores_raw():
    global _CACHE_SENSORES
    return list(_CACHE_SENSORES[-20:])


def get_log_sensores_filtrado(horas=24):
    todos = _leer_json(SENSORES_FILE)
    res = []
    limite = datetime.now() - timedelta(hours=horas)
    for l in todos:
        try:
            if datetime.strptime(l['timestamp'], "%Y-%m-%d %H:%M:%S") >= limite:
                res.append(l)
        except:
            continue
    return res


def get_promedio_sensores_por_hora():
    logs = _leer_json(SENSORES_FILE)
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
    global _CACHE_ACTUADORES
    return dict(_CACHE_ACTUADORES)


def get_log_historico_completo(dias=7): return _leer_json(HISTORICO_ACTUADORES_FILE)


def toggle_actuador(uid, user="sistema"):
    global _CACHE_ACTUADORES
    curr = _CACHE_ACTUADORES.get(uid, {}).get("estado", "cerrada")
    nuevo = "abierta" if curr == "cerrada" else "cerrada"
    return _actualizar_actuador(uid, nuevo, user)


def set_estado_actuador(uid, estado, user="sistema"):
    return _actualizar_actuador(uid, estado, user)


def set_modo_actuador(uid, modo):
    """Cambia entre 'auto' y 'manual'."""
    global _CACHE_ACTUADORES

    # 1. Actualizar RAM
    if uid in _CACHE_ACTUADORES:
        _CACHE_ACTUADORES[uid]['mode'] = modo

    # 2. Actualizar Disco
    actuadores_disco = _leer_json(ACTUADORES_FILE)
    if uid in actuadores_disco:
        actuadores_disco[uid]['mode'] = modo
        _escribir_json(ACTUADORES_FILE, actuadores_disco)
        return True
    return False


def _actualizar_actuador(uid, estado, user):
    global _CACHE_ACTUADORES

    # 1. Actualizar RAM
    if uid in _CACHE_ACTUADORES:
        # Aseguramos que existe la clave mode si no estaba
        if 'mode' not in _CACHE_ACTUADORES[uid]:
            _CACHE_ACTUADORES[uid]['mode'] = 'manual'

        if _CACHE_ACTUADORES[uid]['estado'] == estado: return True
        _CACHE_ACTUADORES[uid]['estado'] = estado

    # 2. Actualizar DISCO
    actuadores_disco = _leer_json(ACTUADORES_FILE)
    if uid in actuadores_disco:
        actuadores_disco[uid]['estado'] = estado
        # Si venía de una versión vieja sin 'mode', lo preservamos o ponemos default
        if 'mode' not in actuadores_disco[uid]:
            actuadores_disco[uid]['mode'] = 'manual'

        _escribir_json(ACTUADORES_FILE, actuadores_disco)

        hist = _leer_json(HISTORICO_ACTUADORES_FILE)
        lbl = actuadores_disco[uid].get("label", uid)
        if uid == "leds": lbl = "Iluminación"
        if uid == "fan": lbl = "Ventilación"

        hist.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "id": uid, "label": lbl, "accion": estado, "usuario": user
        })
        _escribir_json(HISTORICO_ACTUADORES_FILE, hist)
        return True
    return False


# --- USUARIOS/PRESOS ---
def validar_usuario(u, p):
    for x in _leer_json(USUARIOS_FILE):
        if x['user'] == u and x['password'] == p: return x['rol']
    return None


def get_usuarios(): return _leer_json(USUARIOS_FILE)


def add_usuario(u, p, r):
    lst = _leer_json(USUARIOS_FILE)
    if any(x['user'] == u for x in lst): return False
    lst.append({"user": u, "password": p, "rol": r})
    _escribir_json(USUARIOS_FILE, lst)
    return True


def get_presos(): return _leer_json(PRESOS_FILE)


def add_preso(n, d, c):
    lst = _leer_json(PRESOS_FILE)
    nid = (max(x['id'] for x in lst) + 1) if lst else 1
    lst.append(
        {"id": nid, "nombre": n, "delito": d, "celda": c, "fecha_ingreso": datetime.now().strftime("%d/%m/%Y %H:%M")})
    _escribir_json(PRESOS_FILE, lst)
    return True


def update_preso(pid, dat):
    lst = _leer_json(PRESOS_FILE)
    for p in lst:
        if p['id'] == pid:
            p.update(dat)
            _escribir_json(PRESOS_FILE, lst)
            return True
    return False


def delete_preso(pid):
    lst = [p for p in _leer_json(PRESOS_FILE) if p['id'] != pid]
    _escribir_json(PRESOS_FILE, lst)
    return True


inicializar_archivos_json()