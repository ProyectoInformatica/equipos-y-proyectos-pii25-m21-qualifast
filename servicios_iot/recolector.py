import sys
import os
import time
import requests
import random
from datetime import datetime

# 1. TRUCO DE RUTAS (El GPS): Le decimos a Python que la raíz del proyecto
# está una carpeta más atrás, para que pueda encontrar la carpeta "modelo"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. IMPORT CORREGIDO: Usamos nuestra nueva fachada limpia en lugar del viejo
import modelo.manejador_datos as modelo


def iniciar_recoleccion():
    print(f"✅ Recolector IoT Iniciado. Escuchando al ESP32 en {modelo.ESP32_IP}...")

    while True:
        # 1. Obtenemos el intervalo actual de la BD en cada ciclo
        config = modelo.get_configuracion()
        segundos_espera = config.get("intervalo_muestreo", 5.0)
        url_sensores = f"http://{modelo.ESP32_IP}/sensores"

        try:
            respuesta = requests.get(url_sensores, timeout=3)

            if respuesta.status_code == 200:
                data = respuesta.json()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # MQ-2 envía humo y simulamos calidad de aire basada en ese valor
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

                modelo.registrar_dato_sensor(datos)
                print(f"[{timestamp}] Guardado. Intervalo actual: {segundos_espera}s")

        except Exception:
            # Si el ESP32 falla, esperamos un poco antes de reintentar
            pass

        time.sleep(segundos_espera)


if __name__ == "__main__":
    iniciar_recoleccion()