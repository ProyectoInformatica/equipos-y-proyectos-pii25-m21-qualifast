import json
import os
from datetime import datetime

# --- Ubicaciones de los archivos JSON ---
USUARIOS_FILE = 'modelo/usuarios.json'
PRESOS_FILE = 'modelo/presos.json'
ACTUADORES_FILE = 'modelo/actuadores_estado.json'
SENSORES_FILE = 'modelo/sensores_log.json'


# --- Funciones de Inicialización ---
def inicializar_archivos_json():
    if not os.path.exists(USUARIOS_FILE):
        usuarios_default = [
            {"user": "comisario", "password": "1234", "rol": "comisario"},
            {"user": "inspector", "password": "1234", "rol": "inspector"},
            {"user": "policia", "password": "1234", "rol": "policia"}
        ]
        _escribir_json(USUARIOS_FILE, usuarios_default)

    if not os.path.exists(PRESOS_FILE):
        _escribir_json(PRESOS_FILE, [])

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

    if not os.path.exists(SENSORES_FILE):
        _escribir_json(SENSORES_FILE, [])


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


# --- LÓGICA DE USUARIOS ---
def validar_usuario(username, password_plana):
    usuarios = _leer_json(USUARIOS_FILE)
    for user in usuarios:
        if user['user'] == username and user['password'] == password_plana:
            return user['rol']
    return None


def get_usuarios():
    usuarios = _leer_json(USUARIOS_FILE)
    return [{"user": u["user"], "rol": u["rol"]} for u in usuarios]


def add_usuario(username, password_plana, rol):
    if not username or not password_plana or not rol:
        return False
    usuarios = _leer_json(USUARIOS_FILE)
    if any(u['user'] == username for u in usuarios):
        return False
    nuevo_usuario = {"user": username, "password": password_plana, "rol": rol}
    usuarios.append(nuevo_usuario)
    _escribir_json(USUARIOS_FILE, usuarios)
    return True


# --- LÓGICA DE PRESOS ---
def get_presos():
    """Devuelve la lista completa de presos."""
    return _leer_json(PRESOS_FILE)


def add_preso(nombre, delito, celda):
    """
    Añade un nuevo preso con fecha de ingreso automática.
    """
    presos = _leer_json(PRESOS_FILE)

    # Generación de ID robusta
    if presos:
        nuevo_id = max(p["id"] for p in presos) + 1
    else:
        nuevo_id = 1

    # Fecha actual formato: DD/MM/YYYY HH:MM
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")

    nuevo_preso = {
        "id": nuevo_id,
        "nombre": nombre,
        "delito": delito,
        "celda": celda,
        "fecha_ingreso": fecha_actual
    }
    presos.append(nuevo_preso)
    _escribir_json(PRESOS_FILE, presos)
    return True


def delete_preso(id_preso):
    """Elimina un preso por su ID."""
    presos = _leer_json(PRESOS_FILE)
    presos_filtrados = [p for p in presos if p['id'] != id_preso]

    if len(presos) == len(presos_filtrados):
        return False  # No se encontró el ID

    _escribir_json(PRESOS_FILE, presos_filtrados)
    return True


def update_preso(id_preso, datos_nuevos):
    """Actualiza los datos de un preso existente."""
    presos = _leer_json(PRESOS_FILE)
    encontrado = False

    for preso in presos:
        if preso['id'] == id_preso:
            preso.update(datos_nuevos)  # Actualiza campos pasados en el dict
            encontrado = True
            break

    if encontrado:
        _escribir_json(PRESOS_FILE, presos)
        return True
    return False


# --- LÓGICA DE SENSORES Y ACTUADORES ---
def get_log_sensores(limite=50):
    log = _leer_json(SENSORES_FILE)
    return log[-limite:]


def get_estado_actuadores():
    return _leer_json(ACTUADORES_FILE)


def set_estado_actuador(actuador_id, nuevo_estado):
    estados = _leer_json(ACTUADORES_FILE)
    if actuador_id in estados:
        estados[actuador_id]['estado'] = nuevo_estado
        _escribir_json(ACTUADORES_FILE, estados)
        return True
    return False


inicializar_archivos_json()