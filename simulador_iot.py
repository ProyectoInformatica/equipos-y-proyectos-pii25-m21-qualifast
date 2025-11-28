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
    print("Iniciando simulador IoT (DHT11, MQ-2, MQ-135, LDR)...")

    # Lista exacta basada en tu descripción técnica
    sensores_disponibles = [
        "DHT11 - Temperatura",
        "DHT11 - Humedad",
        "LDR - Luz",
        "MQ-2 - Humo",
        "MQ-135 - Aire"
    ]

    while True:
        try:
            sensor_elegido = random.choice(sensores_disponibles)
            valor = ""

            if "Temperatura" in sensor_elegido:
                valor = f"{round(random.uniform(20.0, 26.0), 1)} °C"
            elif "Humedad" in sensor_elegido:
                valor = f"{random.randint(40, 60)} %"
            elif "Luz" in sensor_elegido:
                # LDR varía resistencia según luz
                valor = f"{random.randint(300, 800)} Lux"
            elif "Humo" in sensor_elegido:
                # MQ-2 Gases combustibles
                val_int = random.randint(10, 50) # Normal bajo
                valor = f"{val_int} ppm"
            elif "Aire" in sensor_elegido:
                # MQ-135 Calidad aire (CO2, etc)
                val_int = random.randint(400, 450)
                valor = f"{val_int} ppm"

            nueva_lectura = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sensor": sensor_elegido,
                "valor": valor
            }

            log_actual = _leer_json(SENSORES_FILE)
            log_actual.append(nueva_lectura)

            # Limitamos el log para que no sea infinito
            if len(log_actual) > 300:
                log_actual = log_actual[-300:]

            _escribir_json(SENSORES_FILE, log_actual)

            print(f"-> Dato generado: {sensor_elegido} = {valor}")
            time.sleep(random.randint(3, 6))

        except KeyboardInterrupt:
            print("\nSimulador detenido.")
            break
        except Exception as e:
            print(f"Error simulador: {e}")
            time.sleep(5)

if __name__ == "__main__":
    if not os.path.exists(SENSORES_FILE):
        _escribir_json(SENSORES_FILE, [])
    simular_datos()