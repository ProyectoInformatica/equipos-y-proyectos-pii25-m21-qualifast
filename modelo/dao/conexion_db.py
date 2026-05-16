import mysql.connector
from mysql.connector import pooling
import os
import json

CONFIG_FILE = "ajustes_locales.json"

LOCAL_CONFIG = {
    "db_host": "127.0.0.1",
    "db_port": "3306",
    "db_user": "root",
    "db_pass": "123456",
    "db_name": "comisaria_db",
    "esp32_ip": "10.197.123.128",
    "esp32_cam_ip": "10.197.123.146",
    "heartbeat_timeout": 5
}

ESP32_IP = ""
ESP32_CAM_IP = ""
db_pool = None

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
        print(f"[ERROR BD] Fallo crítico al inicializar Pool de BD: {e}")
        db_pool = None

def probar_conexion():
    try:
        if db_pool:
            conn = db_pool.get_connection()
            conn.close()
            return True
        return False
    except:
        return False

def conectar():
    try:
        return db_pool.get_connection() if db_pool else None
    except:
        return None

# Al importar este archivo, se inicializa automáticamente la conexión
load_local_config()
inicializar_pool()