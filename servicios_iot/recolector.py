import sys
import os
import time
import requests
import random
from datetime import datetime

# 1. TRUCO DE RUTAS (El GPS)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. IMPORT CORREGIDO
import modelo.manejador_datos as modelo


def iniciar_recoleccion():
    print(f"✅ Recolector IoT Iniciado. Escuchando al ESP32 en {modelo.ESP32_IP}...")

    while True:
        config = modelo.get_configuracion()
        segundos_espera = config.get("intervalo_muestreo", 5.0)
        url_sensores = f"http://{modelo.ESP32_IP}/sensores"

        try:
            respuesta = requests.get(url_sensores, timeout=3)

            if respuesta.status_code == 200:
                data = respuesta.json()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                mq2_val = data.get('mq2', 0)
                mq135_sim = int(400 + (mq2_val * 0.4) + random.uniform(-10, 15))
                if mq135_sim < 400: mq135_sim = 400

                # Ampliamos la lista de diccionarios (Añadido soporte valor_texto)
                datos = [
                    {"timestamp": timestamp, "sensor": "DHT11 - Temperatura", "valor": data.get('temperatura', 0), "valor_texto": None},
                    {"timestamp": timestamp, "sensor": "DHT11 - Humedad", "valor": data.get('humedad', 0), "valor_texto": None},
                    {"timestamp": timestamp, "sensor": "LDR - Luz", "valor": data.get('luz', 0), "valor_texto": None},
                    {"timestamp": timestamp, "sensor": "MQ-2 - Humo", "valor": mq2_val, "valor_texto": None},
                    {"timestamp": timestamp, "sensor": "MQ-135 - Aire", "valor": mq135_sim, "valor_texto": None},
                    # NUEVO SENSOR BIORDINARIO
                    {"timestamp": timestamp, "sensor": "Sensor Biordinario", "valor": data.get('bio_num', 0), "valor_texto": data.get('bio_alfa', "Sin datos")}
                ]

                # Importante: Tendrás que asegurarte de que tu 'modelo.registrar_dato_sensor()'
                # en manejador_datos.py soporta recibir la key 'valor_texto' y la inserta en SQL.
                modelo.registrar_dato_sensor(datos)
                print(f"[{timestamp}] Guardado. Intervalo actual: {segundos_espera}s")

        except Exception as e:
            pass

        time.sleep(segundos_espera)


if __name__ == "__main__":
    iniciar_recoleccion()