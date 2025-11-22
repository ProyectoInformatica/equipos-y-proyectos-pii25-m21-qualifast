import json
import os
import time
import random
from datetime import datetime

SENSORES_FILE = 'modelo/sensores_log.json'

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

def simular_datos():
    print("Iniciando simulador IoT... (Pulsa CTRL+C para detener)")
    
    sensores = ["DHT11", "MQ-2", "MQ-135", "LDR"]
    
    while True:
        try:
            # Elegir un sensor al azar para actualizar
            sensor_elegido = random.choice(sensores)
            valor = 0
            
            if sensor_elegido == "DHT11":
                valor = round(random.uniform(18.0, 25.0), 1) # Temperatura
            elif sensor_elegido == "MQ-2":
                valor = random.randint(100, 300) # PPM Humo
            elif sensor_elegido == "MQ-135":
                valor = random.randint(50, 150) # PPM Calidad Aire
            elif sensor_elegido == "LDR":
                valor = random.randint(200, 1000) # Lux
            
            # Formato de la nueva lectura
            nueva_lectura = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sensor": sensor_elegido,
                "valor": valor
            }
            
            # Leer el log actual, añadir el nuevo y guardarlo
            log_actual = _leer_json(SENSORES_FILE)
            log_actual.append(nueva_lectura)
            
            # Para que el archivo no crezca indefinidamente, lo limitamos
            if len(log_actual) > 200:
                log_actual = log_actual[-200:] # Mantiene solo los últimos 200
                
            _escribir_json(SENSORES_FILE, log_actual)
            
            print(f"-> Log guardado: {sensor_elegido} = {valor}")
            
            # Espera entre 3 y 8 segundos
            time.sleep(random.randint(3, 8))
            
        except KeyboardInterrupt:
            print("\nSimulador detenido.")
            break
        except Exception as e:
            print(f"Error en el simulador: {e}")
            time.sleep(10)

if __name__ == "__main__":
    # Asegúrate de que el archivo existe antes de empezar
    if not os.path.exists(SENSORES_FILE):
        _escribir_json(SENSORES_FILE, [])
        
    simular_datos()