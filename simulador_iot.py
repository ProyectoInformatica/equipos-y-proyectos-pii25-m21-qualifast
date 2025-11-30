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
    print("Iniciando simulador IoT (Generando datos cada 3s)...")

    # Lista de sensores definidos en el sistema
    sensores_definidos = [
        "DHT11 - Temperatura",
        "DHT11 - Humedad",
        "LDR - Luz",
        "MQ-2 - Humo",
        "MQ-135 - Aire"
    ]

    while True:
        try:
            nuevos_datos = []
            timestamp_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Generamos un dato para CADA sensor en este ciclo
            for nombre_sensor in sensores_definidos:
                valor = ""

                if "Temperatura" in nombre_sensor:
                    valor = f"{round(random.uniform(20.0, 30.0), 1)} °C"
                elif "Humedad" in nombre_sensor:
                    valor = f"{random.randint(40, 60)} %"
                elif "Luz" in nombre_sensor:
                    valor = f"{random.randint(300, 800)} Lux"
                elif "Humo" in nombre_sensor:
                    # Ocasionalmente simular picos
                    base = random.randint(10, 30)
                    if random.random() > 0.95: base += 100
                    valor = f"{base} ppm"
                elif "Aire" in nombre_sensor:
                    valor = f"{random.randint(400, 480)} ppm"

                nuevos_datos.append({
                    "timestamp": timestamp_actual,
                    "sensor": nombre_sensor,
                    "valor": valor
                })
                print(f"-> Generado: {nombre_sensor} = {valor}")

            # Guardamos el bloque completo
            log_actual = _leer_json(SENSORES_FILE)
            log_actual.extend(nuevos_datos)

            # Limitamos el histórico para no saturar el archivo (últimos 500 registros)
            if len(log_actual) > 500:
                log_actual = log_actual[-500:]

            _escribir_json(SENSORES_FILE, log_actual)

            print("--- Ciclo completado, esperando 3s ---")
            time.sleep(3)

        except KeyboardInterrupt:
            print("\nSimulador detenido.")
            break
        except Exception as e:
            print(f"Error simulador: {e}")
            time.sleep(1)


if __name__ == "__main__":
    if not os.path.exists(SENSORES_FILE):
        _escribir_json(SENSORES_FILE, [])
    simular_datos()