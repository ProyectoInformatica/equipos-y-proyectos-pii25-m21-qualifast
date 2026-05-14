import time
import requests
import random
from datetime import datetime
import modelo.manejador_datos as modelo


def iniciar_recoleccion():
    print(f"✅ Recolector IoT Iniciado. Escuchando al ESP32 en {modelo.ESP32_IP}...")
    url_sensores = f"http://{modelo.ESP32_IP}/sensores"

    while True:
        try:
            respuesta = requests.get(url_sensores, timeout=3)

            if respuesta.status_code == 200:
                data = respuesta.json()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Simulación de Calidad de Aire basada en humo
                mq2_val = data.get('mq2', 0)
                mq135_sim = int(400 + (mq2_val * 0.4) + random.uniform(-10, 15))
                if mq135_sim < 400: mq135_sim = 400

                datos = [
                    {"timestamp": timestamp, "sensor": "DHT11 - Temperatura",
                     "valor": f"{data.get('temperatura', 0)} °C"},
                    {"timestamp": timestamp, "sensor": "DHT11 - Humedad", "valor": f"{data.get('humedad', 0)} %"},
                    {"timestamp": timestamp, "sensor": "LDR - Luz", "valor": f"{data.get('luz', 0)} Lux"},
                    {"timestamp": timestamp, "sensor": "MQ-2 - Humo", "valor": f"{mq2_val} ppm"},
                    {"timestamp": timestamp, "sensor": "MQ-135 - Aire", "valor": f"{mq135_sim} ppm"}
                ]

                # Guardar en Base de Datos MySQL de forma silenciosa
                modelo.registrar_dato_sensor(datos)
                print(f"[{timestamp}] Datos guardados correctamente en MySQL.")

        except Exception as e:
            # Si el ESP32 está apagado o no hay Wi-Fi, falla silenciosamente y vuelve a intentar luego
            pass

        time.sleep(5)  # Lee cada 5 segundos


if __name__ == "__main__":
    iniciar_recoleccion()