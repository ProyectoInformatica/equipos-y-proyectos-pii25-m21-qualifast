import time
import random
from datetime import datetime
import modelo.manejador_datos as modelo


def simular_datos():
    print("Iniciando simulador IoT (Directo a MySQL)...")

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

            for nombre_sensor in sensores_definidos:
                valor = ""
                if "Temperatura" in nombre_sensor:
                    valor = f"{round(random.uniform(20, 35), 1)} °C"
                elif "Humedad" in nombre_sensor:
                    valor = f"{random.randint(40, 60)} %"
                elif "Luz" in nombre_sensor:
                    valor = f"{random.randint(300, 800)} Lux"
                elif "Humo" in nombre_sensor:
                    valor = f"{random.randint(10, 30)} ppm"
                elif "Aire" in nombre_sensor:
                    valor = f"{random.randint(400, 480)} ppm"

                nuevos_datos.append({
                    "timestamp": timestamp_actual,
                    "sensor": nombre_sensor,
                    "valor": valor
                })

            # Inserción directa en MySQL (Cumple rúbrica)
            modelo.registrar_dato_sensor(nuevos_datos)

            print(f"--- Ciclo SQL completado: {len(nuevos_datos)} datos insertados ---")
            time.sleep(3)

        except KeyboardInterrupt:
            print("\nSimulador detenido.")
            break
        except Exception as e:
            print(f"Error en simulador: {e}")
            time.sleep(3)


if __name__ == "__main__":
    simular_datos()