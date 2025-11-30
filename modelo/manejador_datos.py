import json
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict

# --- Ubicaciones de los archivos JSON ---
USUARIOS_FILE = 'modelo/usuarios.json'
PRESOS_FILE = 'modelo/presos.json'
ACTUADORES_FILE = 'modelo/actuadores_estado.json'
SENSORES_FILE = 'modelo/sensores_log.json'
HISTORICO_ACTUADORES_FILE = 'modelo/puertas_log.json'


# --- Funciones de Inicialización (Sin cambios) ---
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


# --- Funciones Auxiliares ---
def _leer_json(archivo):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return [] if 'lista' in archivo or 'log' in archivo or 'usuarios' in archivo or 'presos' in archivo else {}


def _escribir_json(archivo, data):
    try:
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error al escribir en {archivo}: {e}")


# --- LÓGICA DE USUARIOS Y PRESOS (Sin cambios significativos) ---
def validar_usuario(username, password_plana):
    usuarios = _leer_json(USUARIOS_FILE)
    for user in usuarios:
        if user['user'] == username and user['password'] == password_plana:
            return user['rol']
    return None


def get_usuarios(): return _leer_json(USUARIOS_FILE)


def add_usuario(username, password_plana, rol):
    usuarios = _leer_json(USUARIOS_FILE)
    if any(u['user'] == username for u in usuarios): return False
    usuarios.append({"user": username, "password": password_plana, "rol": rol})
    _escribir_json(USUARIOS_FILE, usuarios)
    return True


def get_presos(): return _leer_json(PRESOS_FILE)


def add_preso(nombre, delito, celda="Sin asignar"):
    presos = _leer_json(PRESOS_FILE)
    nuevo_id = (max(p["id"] for p in presos) + 1) if presos else 1
    presos.append({
        "id": nuevo_id, "nombre": nombre, "delito": delito, "celda": celda,
        "fecha_ingreso": datetime.now().strftime("%d/%m/%Y %H:%M")
    })
    _escribir_json(PRESOS_FILE, presos)
    return True


def delete_preso(id_preso):
    presos = _leer_json(PRESOS_FILE)
    filtrados = [p for p in presos if p['id'] != id_preso]
    if len(presos) == len(filtrados): return False
    _escribir_json(PRESOS_FILE, filtrados)
    return True


def update_preso(id_preso, datos_nuevos):
    presos = _leer_json(PRESOS_FILE)
    for p in presos:
        if p['id'] == id_preso:
            p.update(datos_nuevos)
            _escribir_json(PRESOS_FILE, presos)
            return True
    return False


# --- LÓGICA SENSORES ---
def registrar_dato_sensor(datos_nuevos):
    """Añade nuevos registros al log de sensores."""
    log_actual = _leer_json(SENSORES_FILE)
    log_actual.extend(datos_nuevos)
    # Limitar tamaño para no saturar (últimos 1000)
    if len(log_actual) > 1000:
        log_actual = log_actual[-1000:]
    _escribir_json(SENSORES_FILE, log_actual)


def get_log_sensores_filtrado(horas=24):
    todos = _leer_json(SENSORES_FILE)
    filtrados = []
    limite = datetime.now() - timedelta(hours=horas)
    for log in todos:
        try:
            if datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S") >= limite:
                filtrados.append(log)
        except ValueError:
            continue
    return filtrados


def get_promedio_sensores_por_hora():
    logs = _leer_json(SENSORES_FILE)
    agrupacion = defaultdict(list)
    for log in logs:
        try:
            dt = datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S")
            key = (log['sensor'], dt.strftime("%Y-%m-%d %H:00"))
            # Extraer número: "23.5 °C" -> 23.5
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


# --- LÓGICA ACTUADORES ---
def get_log_historico_completo(dias=7):
    return _leer_json(HISTORICO_ACTUADORES_FILE)  # (simplificado, filtro opcional)


def get_estado_actuadores():
    return _leer_json(ACTUADORES_FILE)


def set_estado_actuador(actuador_id, nuevo_estado, usuario="sistema"):
    """Fuerza un estado específico (para leds/fan)."""
    return _actualizar_actuador(actuador_id, nuevo_estado, usuario)


def toggle_actuador(actuador_id, usuario="sistema"):
    """
    Invierte el estado actual (para puertas).
    SOLUCIÓN BUG: Lee el archivo, verifica estado REAL y lo cambia.
    """
    estados = _leer_json(ACTUADORES_FILE)
    if actuador_id not in estados: return False

    estado_actual = estados[actuador_id]['estado']
    nuevo_estado = "cerrada" if estado_actual == "abierta" else "abierta"

    return _actualizar_actuador(actuador_id, nuevo_estado, usuario)


def _actualizar_actuador(actuador_id, nuevo_estado, usuario):
    estados = _leer_json(ACTUADORES_FILE)
    if actuador_id in estados:
        # Solo guardar si hay cambio real o si queremos registrar todo click
        # Para puertas queremos registrar cada interacción:
        estados[actuador_id]['estado'] = nuevo_estado
        _escribir_json(ACTUADORES_FILE, estados)

        # Log
        log = _leer_json(HISTORICO_ACTUADORES_FILE)
        label = estados[actuador_id].get("label", actuador_id)
        if actuador_id == "leds": label = "Iluminación"
        if actuador_id == "fan": label = "Ventilación"

        log.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "id": actuador_id, "label": label, "accion": nuevo_estado, "usuario": usuario
        })
        _escribir_json(HISTORICO_ACTUADORES_FILE, log)
        return True
    return False


inicializar_archivos_json()