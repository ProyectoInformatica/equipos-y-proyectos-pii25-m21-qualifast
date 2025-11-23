# simulador_iot.py

import json
import time
import random
import os
from datetime import datetime
import cv2  

# --- CONFIGURACIÓN ---
SENSORES_FILE = 'modelo/sensores_log.json'

VIDEO_ORIGEN = 'assets/videoGato.mp4'

CARPETA_DESTINO = 'capturas_simuladas' 


if not os.path.exists(CARPETA_DESTINO):
    os.makedirs(CARPETA_DESTINO)

if not os.path.exists(SENSORES_FILE):
    try:
        with open(SENSORES_FILE, 'w') as f:
            json.dump([], f)
    except IOError:
        pass 



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
    Si el video termina, se reinicia solo.
    """
    

    ret, frame = captura_video.read()
    

    if not ret:
        print("-> CÁMARA: Video terminado. Reiniciando desde el fotograma 0...")
        # Vuelve al fotograma 0
        captura_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = captura_video.read()
        
        # Si sigue fallando (video corrupto o no se puede leer)
        if not ret:
            print("ERROR CÁMARA: No se pudo leer el fotograma después de reiniciar.")
            return

    # 3. Genera un nombre de archivo único con la fecha y hora
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_destino = f"camara_{timestamp}.jpg"
    ruta_destino = os.path.join(CARPETA_DESTINO, nombre_destino)

    try:
        # 4. Guarda el fotograma actual como un archivo JPG
        cv2.imwrite(ruta_destino, frame)
        print(f"-> CÁMARA: Fotograma guardado como '{ruta_destino}'")
    except Exception as e:
        print(f"Error al guardar fotograma de cámara: {e}")



def simular_datos():
    print("Iniciando simulador IoT... (Pulsa CTRL+C para detener)")
    
    sensores = ["DHT11", "MQ-2", "MQ-135", "LDR"]
    
    # Contador para simular la cámara cada X ciclos
    contador_camara = 0
    Frecuencia_Camara = 10 # Simular captura cada 10 ciclos de sensor
    

    captura_video = cv2.VideoCapture(VIDEO_ORIGEN)
    if not captura_video.isOpened():
        print(f"Error fatal: No se pudo abrir el video en {VIDEO_ORIGEN}")
        print("Asegúrate de que el archivo existe y OpenCV está instalado.")
        return
    else:
        print(f"Video '{VIDEO_ORIGEN}' cargado para simulación de cámara.")
    
    while True:
        try:
            # --- Lógica de simulación de sensores ---
            sensor_elegido = random.choice(sensores)
            
            if sensor_elegido == "DHT11":
                valor = round(random.uniform(18.0, 25.0), 1) # Temperatura
            elif sensor_elegido == "MQ-2":
                valor = random.randint(100, 300) # PPM Humo
            elif sensor_elegido == "MQ-135":
                valor = random.randint(50, 150) # PPM Calidad Aire
            elif sensor_elegido == "LDR":
                valor = random.randint(200, 1000) # Lux
            
            nueva_lectura = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sensor": sensor_elegido,
                "valor": valor
            }
            
            log_actual = _leer_json(SENSORES_FILE)
            log_actual.append(nueva_lectura)
            
            # Limita el log a 200 entradas
            if len(log_actual) > 200:
                log_actual = log_actual[-200:]
                
            _escribir_json(SENSORES_FILE, log_actual)
            print(f"-> Log guardado: {sensor_elegido} = {valor}")
            
            # --- Lógica de simulación de CÁMARA ---
            contador_camara += 1
            if contador_camara >= Frecuencia_Camara:
                # Le pasamos el objeto de captura a la función
                _simular_captura_camara(captura_video)
                contador_camara = 0

            # Espera
            time.sleep(random.randint(3, 8))
            
        except KeyboardInterrupt:
            print("\nSimulador detenido.")
            break
        except Exception as e:
            print(f"Error en el bucle del simulador: {e}")
            time.sleep(10)
    
    # Libera el video al salir
    captura_video.release()
    print("Captura de video liberada.")

if __name__ == "__main__":
    simular_datos()