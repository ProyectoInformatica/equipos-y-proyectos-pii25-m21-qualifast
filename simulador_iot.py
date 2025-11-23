# simulador_iot.py

import json
import time
import random
import os
from datetime import datetime
import cv2  # Necesario para la simulación de cámara

# --- CONFIGURACIÓN ---
SENSORES_FILE = 'modelo/sensores_log.json'
VIDEO_ORIGEN = 'assets/videoGato.mp4'  # Video fuente para simular la cámara
CARPETA_DESTINO = 'capturas_simuladas'

# Asegurar que existan los directorios y archivos necesarios
if not os.path.exists(CARPETA_DESTINO):
    os.makedirs(CARPETA_DESTINO)

if not os.path.exists(SENSORES_FILE):
    try:
        with open(SENSORES_FILE, 'w') as f:
            json.dump([], f)
    except IOError:
        pass

    # --- FUNCIONES AUXILIARES ---


def _leer_json(archivo):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def _escribir_json(archivo, data):
    try:
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error al escribir en {archivo}: {e}")


def _simular_captura_camara(captura_video):
    """
    Simula una captura de cámara leyendo el SIGUIENTE fotograma
    del video y guardándolo como un archivo JPG.
    Si el video termina, se reinicia.
    """
    if not captura_video or not captura_video.isOpened():
        return

    ret, frame = captura_video.read()

    if not ret:
        print("-> CÁMARA: Video terminado. Reiniciando...")
        captura_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = captura_video.read()
        if not ret:
            return

    # Genera un nombre único
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_destino = f"camara_{timestamp}.jpg"
    ruta_destino = os.path.join(CARPETA_DESTINO, nombre_destino)

    try:
        cv2.imwrite(ruta_destino, frame)
        # print(f"-> CÁMARA: Frame guardado en {ruta_destino}") # Descomentar para debug
    except Exception as e:
        print(f"Error al guardar fotograma: {e}")


# --- SIMULACIÓN PRINCIPAL ---

def simular_datos():
    print("Iniciando simulador IoT (Sensores + Cámara)... (Pulsa CTRL+C para detener)")

    sensores = ["DHT11", "MQ-2", "MQ-135", "LDR"]

    # Configuración de la cámara
    contador_camara = 0
    frecuencia_camara = 5  # Captura una foto cada 5 ciclos del bucle

    captura_video = cv2.VideoCapture(VIDEO_ORIGEN)
    if not captura_video.isOpened():
        print(f"ADVERTENCIA: No se pudo abrir '{VIDEO_ORIGEN}'. La simulación de cámara no funcionará.")
    else:
        print(f"Video cargado correctamente para simulación.")

    while True:
        try:
            # 1. SIMULACIÓN DE SENSORES (Tu código original)
            sensor_elegido = random.choice(sensores)
            
            if sensor_elegido == "DHT11":
                valor = round(random.uniform(18.0, 25.0), 1)
            elif sensor_elegido == "MQ-2":
                valor = random.randint(100, 300)
            elif sensor_elegido == "MQ-135":
                valor = random.randint(50, 150)
            elif sensor_elegido == "LDR":
                valor = random.randint(200, 1000)

            nueva_lectura = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sensor": sensor_elegido,
                "valor": valor
            }

            log_actual = _leer_json(SENSORES_FILE)
            log_actual.append(nueva_lectura)

            if len(log_actual) > 200:
                log_actual = log_actual[-200:]

            _escribir_json(SENSORES_FILE, log_actual)
            print(f"-> Sensor: {sensor_elegido} = {valor}")

            # 2. SIMULACIÓN DE CÁMARA (Integración necesaria)
            contador_camara += 1
            if contador_camara >= frecuencia_camara:
                _simular_captura_camara(captura_video)
                contador_camara = 0

            # Espera aleatoria
            time.sleep(random.randint(3, 8))
            
        except KeyboardInterrupt:
            print("\nSimulador detenido.")
            break
        except Exception as e:
            print(f"Error en el simulador: {e}")
            time.sleep(5)

    if captura_video:
        captura_video.release()


if __name__ == "__main__":
    simular_datos()