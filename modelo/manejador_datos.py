import glob
import json
import os

# --- Ubicaciones de los archivos JSON ---
USUARIOS_FILE = 'modelo/usuarios.json'
PRESOS_FILE = 'modelo/presos.json'
ACTUADORES_FILE = 'modelo/actuadores_estado.json'
SENSORES_FILE = 'modelo/sensores_log.json'

# --- Funciones de Inicialización (para que no falle si no existen) ---
def inicializar_archivos_json():
    """Crea los archivos JSON si no existen para evitar errores al inicio."""
    if not os.path.exists(USUARIOS_FILE):
        # ¡CAMBIADO! Guarda la contraseña en texto plano
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

# --- Funciones Auxiliares de JSON ---
def _leer_json(archivo):
    """Función genérica para leer un archivo JSON."""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Error o archivo no encontrado: {archivo}, devolviendo lista vacía o dict.")
        return [] if 'lista' in archivo or 'log' in archivo or 'usuarios' in archivo else {}

def _escribir_json(archivo, data):
    """Función genérica para escribir en un archivo JSON."""
    try:
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error al escribir en {archivo}: {e}")

# --- LÓGICA DE USUARIOS ---
def validar_usuario(username, password_plana):
    """
    ¡CAMBIADO! Valida al usuario contra el JSON (VERSIÓN INSEGURA, TEXTO PLANO).
    Devuelve el ROL si es exitoso, o None si falla.
    """
    usuarios = _leer_json(USUARIOS_FILE)
    
    for user in usuarios:
        # Compara el usuario y la contraseña en texto plano
        if user['user'] == username and user['password'] == password_plana:
            return user['rol']
    return None

def get_usuarios():
    """Devuelve la lista de todos los usuarios (sin la contraseña)."""
    usuarios = _leer_json(USUARIOS_FILE)
    # Ocultamos la contraseña por seguridad antes de enviarla a la vista
    return [{"user": u["user"], "rol": u["rol"]} for u in usuarios]

def add_usuario(username, password_plana, rol):
    """¡CAMBIADO! Añade un nuevo usuario (VERSIÓN INSEGURA, TEXTO PLANO)."""
    if not username or not password_plana or not rol:
        return False
        
    usuarios = _leer_json(USUARIOS_FILE)
    
    # Comprobar si el usuario ya existe
    if any(u['user'] == username for u in usuarios):
        print(f"Error: El usuario {username} ya existe.")
        return False
        
    # Guarda la contraseña en texto plano
    nuevo_usuario = {
        "user": username,
        "password": password_plana, # <-- Cambio de 'hash' a 'password'
        "rol": rol
    }
    usuarios.append(nuevo_usuario)
    _escribir_json(USUARIOS_FILE, usuarios)
    return True

# --- LÓGICA DE PRESOS ---
def get_presos():
    """Devuelve la lista completa de presos."""
    return _leer_json(PRESOS_FILE)

def add_preso(nombre, delito):
    """Añade un nuevo preso."""
    presos = _leer_json(PRESOS_FILE)
    nuevo_preso = {
        "id": len(presos) + 1, # ID simple
        "nombre": nombre,
        "delito": delito
    }
    presos.append(nuevo_preso)
    _escribir_json(PRESOS_FILE, presos)
    return True

# --- LÓGICA DE SENSORES Y ACTUADORES ---
def get_log_sensores(limite=50):
    """Devuelve las últimas N lecturas de sensores."""
    log = _leer_json(SENSORES_FILE)
    return log[-limite:] # Devuelve los últimos 50 registros

def get_estado_actuadores():
    """Devuelve el estado actual de todas las puertas, luces, etc."""
    return _leer_json(ACTUADORES_FILE)

def set_estado_actuador(actuador_id, nuevo_estado):
    """Cambia el estado de un actuador (ej. 'door-1' a 'abierta')."""
    estados = _leer_json(ACTUADORES_FILE)
    if actuador_id in estados:
        estados[actuador_id]['estado'] = nuevo_estado
        _escribir_json(ACTUADORES_FILE, estados)
        return True
    return False

# --- SIMULACIÓN DE CÁMARA ---

CAM_FOLDER = 'capturas_simuladas'
# (Opcional) Crea una imagen 'assets/no_signal.png' para usarla si no hay capturas
PLACEHOLDER_IMAGE = 'assets/no_signal.png' 

def get_latest_camera_image():
    """
    Encuentra la imagen .jpg más reciente en la carpeta de capturas.
    Devuelve la ruta (path) a esa imagen o None si no encuentra.
    """
    try:
        # 1. Busca todos los archivos .jpg en la carpeta
        list_of_files = glob.glob(os.path.join(CAM_FOLDER, '*.jpg'))
        
        if not list_of_files:
            # Si no hay archivos, devuelve None
            print("Modelo: No se encontraron imágenes de cámara.")
            return None # <--- CAMBIADO

        # 2. Encuentra el archivo más reciente (por fecha de modificación)
        latest_file = max(list_of_files, key=os.path.getctime)
        
        # 3. Devuelve la ruta al archivo
        return latest_file
    
    except Exception as e:
        print(f"Error al obtener último frame de cámara: {e}")
        return None # <--- CAMBIADO

# Inicializa los archivos al cargar el módulo por primera vez
inicializar_archivos_json()