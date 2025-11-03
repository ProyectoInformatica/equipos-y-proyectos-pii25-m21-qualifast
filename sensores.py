"""
Módulo de gestión de sensores y actuadores para el sistema IoT de comisaría
Proyecto: Estación de Policía - Qualifast Buildings
Curso: 2025-2026

Este módulo define las clases para manejar sensores (DHT, LDR, MQ2, MQ135)
y actuadores (Ventilador, LED) con simulación de datos realistas.
"""

import random
from datetime import datetime
from typing import Dict, Any, Optional


class Sensor:
    """
    Clase base para todos los sensores y actuadores del sistema.
    
    Attributes:
        id (str): Identificador único del sensor
        tipo (str): Tipo de sensor (DHT, LDR, MQ2, etc.)
        estado (bool): Estado del sensor (True=activo, False=inactivo)
        ubicacion (str): Ubicación física en la comisaría
        valor (Dict): Último valor registrado
    """
    
    def __init__(self, id: str, tipo: str, ubicacion: str = "Sin especificar"):
        """
        Inicializa un sensor base.
        
        Args:
            id: Identificador único del sensor
            tipo: Tipo de sensor
            ubicacion: Ubicación física del sensor en la comisaría
        """
        self.id = id
        self.tipo = tipo
        self.estado = True  # Activo por defecto
        self.ubicacion = ubicacion
        self.valor = {}
        self.timestamp = None
    
    def activar(self) -> None:
        """Activa el sensor."""
        self.estado = True
    
    def desactivar(self) -> None:
        """Desactiva el sensor."""
        self.estado = False
    
    def simular_dato(self) -> Dict[str, Any]:
        """
        Método base para simular datos. Debe ser sobrescrito en clases hijas.
        
        Returns:
            Diccionario con datos simulados
        """
        raise NotImplementedError("Este método debe ser implementado en la clase hija")
    
    def get_estado(self) -> Dict[str, Any]:
        """
        Obtiene el estado completo del sensor.
        
        Returns:
            Diccionario con toda la información del sensor
        """
        return {
            "id": self.id,
            "tipo": self.tipo,
            "estado": "activo" if self.estado else "inactivo",
            "ubicacion": self.ubicacion,
            "valor": self.valor,
            "timestamp": self.timestamp
        }


class DHT(Sensor):
    """
    Sensor de temperatura y humedad (DHT11/DHT22).
    Simula lecturas de temperatura (°C) y humedad relativa (%).
    """
    
    def __init__(self, id: str, ubicacion: str = "Sin especificar", modelo: str = "DHT22"):
        """
        Inicializa el sensor DHT.
        
        Args:
            id: Identificador único
            ubicacion: Ubicación en la comisaría (ej: "Sala de detención")
            modelo: Modelo del sensor (DHT11 o DHT22)
        """
        super().__init__(id, "DHT", ubicacion)
        self.modelo = modelo
        # DHT22 tiene mayor precisión que DHT11
        self.temp_min = 15.0 if modelo == "DHT22" else 20.0
        self.temp_max = 35.0 if modelo == "DHT22" else 30.0
    
    def simular_dato(self) -> Dict[str, float]:
        """
        Simula una lectura de temperatura y humedad.
        
        Returns:
            Diccionario con temperatura y humedad
        """
        if not self.estado:
            return {"temperatura": None, "humedad": None}
        
        # Simular temperatura con variación realista
        temperatura = round(random.uniform(self.temp_min, self.temp_max), 1)
        
        # Humedad relativa (30-70% es rango común en interiores)
        humedad = round(random.uniform(30.0, 70.0), 1)
        
        self.valor = {
            "temperatura": temperatura,
            "humedad": humedad,
            "unidad_temp": "°C",
            "unidad_hum": "%"
        }
        self.timestamp = datetime.now().isoformat()
        
        return self.valor


class LDR(Sensor):
    """
    Fotorresistor (Light Dependent Resistor).
    Simula niveles de luz ambiental para control de iluminación automática.
    """
    
    def __init__(self, id: str, ubicacion: str = "Sin especificar"):
        """
        Inicializa el sensor LDR.
        
        Args:
            id: Identificador único
            ubicacion: Ubicación en la comisaría (ej: "Pasillo principal")
        """
        super().__init__(id, "LDR", ubicacion)
        self.umbral_oscuridad = 200  # Valor bajo indica oscuridad
    
    def simular_dato(self) -> Dict[str, Any]:
        """
        Simula una lectura de intensidad lumínica.
        
        Returns:
            Diccionario con nivel de luz y clasificación
        """
        if not self.estado:
            return {"luz": None, "condicion": None}
        
        # Valor analógico (0-1023, donde 0 es muy oscuro y 1023 es muy brillante)
        nivel_luz = random.randint(0, 1023)
        
        # Clasificar la condición de luz
        if nivel_luz < 200:
            condicion = "Oscuro"
        elif nivel_luz < 500:
            condicion = "Penumbra"
        elif nivel_luz < 800:
            condicion = "Iluminado"
        else:
            condicion = "Muy brillante"
        
        self.valor = {
            "luz": nivel_luz,
            "condicion": condicion,
            "unidad": "valor analógico (0-1023)",
            "requiere_luz": nivel_luz < self.umbral_oscuridad
        }
        self.timestamp = datetime.now().isoformat()
        
        return self.valor


class MQ2(Sensor):
    """
    Sensor de humo y gases combustibles.
    Detecta presencia de humo para sistema de alarma contra incendios.
    """
    
    def __init__(self, id: str, ubicacion: str = "Sin especificar"):
        """
        Inicializa el sensor MQ-2.
        
        Args:
            id: Identificador único
            ubicacion: Ubicación en la comisaría (ej: "Oficinas")
        """
        super().__init__(id, "MQ2", ubicacion)
        self.umbral_peligro = 400  # ppm - nivel de alerta
    
    def simular_dato(self) -> Dict[str, Any]:
        """
        Simula una lectura de concentración de humo/gas.
        
        Returns:
            Diccionario con nivel de humo y alerta
        """
        if not self.estado:
            return {"humo": None, "alerta": None}
        
        # Simular concentración de gas en ppm (partes por millón)
        # Normalmente bajo, ocasionalmente picos para simular eventos
        if random.random() < 0.95:  # 95% del tiempo: valores normales
            concentracion = random.randint(50, 200)
        else:  # 5% del tiempo: valores elevados (simulación de evento)
            concentracion = random.randint(300, 800)
        
        # Determinar nivel de alerta
        if concentracion < 200:
            nivel_alerta = "Normal"
            peligro = False
        elif concentracion < 400:
            nivel_alerta = "Precaución"
            peligro = False
        else:
            nivel_alerta = "PELIGRO - Evacuar"
            peligro = True
        
        self.valor = {
            "humo": concentracion,
            "nivel_alerta": nivel_alerta,
            "unidad": "ppm",
            "peligro": peligro
        }
        self.timestamp = datetime.now().isoformat()
        
        return self.valor


class MQ135(Sensor):
    """
    Sensor de calidad del aire.
    Detecta CO2, NH3, NOx y otros contaminantes atmosféricos.
    """
    
    def __init__(self, id: str, ubicacion: str = "Sin especificar"):
        """
        Inicializa el sensor MQ-135.
        
        Args:
            id: Identificador único
            ubicacion: Ubicación en la comisaría (ej: "Sala de interrogatorios")
        """
        super().__init__(id, "MQ135", ubicacion)
        self.umbral_mala_calidad = 600  # ppm - nivel de mala calidad
    
    def simular_dato(self) -> Dict[str, Any]:
        """
        Simula una lectura de calidad del aire.
        
        Returns:
            Diccionario con nivel de CO2 y calidad del aire
        """
        if not self.estado:
            return {"co2": None, "calidad": None}
        
        # Simular concentración de CO2 en ppm (400-2000 ppm es rango típico)
        co2 = random.randint(400, 1500)
        
        # Clasificar calidad del aire
        if co2 < 600:
            calidad = "Excelente"
        elif co2 < 800:
            calidad = "Buena"
        elif co2 < 1000:
            calidad = "Aceptable"
        elif co2 < 1500:
            calidad = "Mala"
        else:
            calidad = "Muy mala"
        
        self.valor = {
            "co2": co2,
            "calidad_aire": calidad,
            "unidad": "ppm",
            "ventilacion_requerida": co2 > self.umbral_mala_calidad
        }
        self.timestamp = datetime.now().isoformat()
        
        return self.valor


class Ventilador(Sensor):
    """
    Actuador: Ventilador de 5V.
    Controla la ventilación en respuesta a temperatura o calidad del aire.
    """
    
    def __init__(self, id: str, ubicacion: str = "Sin especificar"):
        """
        Inicializa el ventilador.
        
        Args:
            id: Identificador único
            ubicacion: Ubicación en la comisaría (ej: "Sala de servidores")
        """
        super().__init__(id, "Ventilador", ubicacion)
        self.velocidad = 0  # Velocidad 0-100%
        self.modo_auto = False
    
    def simular_dato(self) -> Dict[str, Any]:
        """
        Simula el estado actual del ventilador.
        
        Returns:
            Diccionario con velocidad y estado del ventilador
        """
        # En modo simulación, variar ligeramente la velocidad
        if self.estado and self.velocidad > 0:
            variacion = random.randint(-5, 5)
            self.velocidad = max(0, min(100, self.velocidad + variacion))
        
        self.valor = {
            "velocidad": self.velocidad,
            "rpm_estimado": int(self.velocidad * 30),  # Conversión aproximada a RPM
            "modo_automatico": self.modo_auto,
            "consumo_estimado": round(self.velocidad * 0.05, 2)  # Watts
        }
        self.timestamp = datetime.now().isoformat()
        
        return self.valor
    
    def set_velocidad(self, velocidad: int) -> None:
        """
        Establece la velocidad del ventilador.
        
        Args:
            velocidad: Velocidad de 0 a 100%
        """
        if 0 <= velocidad <= 100:
            self.velocidad = velocidad
            if velocidad > 0:
                self.estado = True
            else:
                self.estado = False


class LED(Sensor):
    """
    Actuador: Diodo LED.
    Controla iluminación de emergencia o indicadores de estado.
    """
    
    def __init__(self, id: str, ubicacion: str = "Sin especificar", color: str = "blanco"):
        """
        Inicializa el LED.
        
        Args:
            id: Identificador único
            ubicacion: Ubicación en la comisaría (ej: "Entrada principal")
            color: Color del LED (blanco, rojo, verde, azul, amarillo)
        """
        super().__init__(id, "LED", ubicacion)
        self.color = color
        self.brillo = 0  # Brillo 0-100%
        self.intermitente = False
    
    def simular_dato(self) -> Dict[str, Any]:
        """
        Simula el estado actual del LED.
        
        Returns:
            Diccionario con brillo y estado del LED
        """
        self.valor = {
            "brillo": self.brillo,
            "color": self.color,
            "intermitente": self.intermitente,
            "encendido": self.estado and self.brillo > 0,
            "consumo_estimado": round(self.brillo * 0.01, 2)  # Watts
        }
        self.timestamp = datetime.now().isoformat()
        
        return self.valor
    
    def set_brillo(self, brillo: int) -> None:
        """
        Establece el brillo del LED.
        
        Args:
            brillo: Brillo de 0 a 100%
        """
        if 0 <= brillo <= 100:
            self.brillo = brillo
            if brillo > 0:
                self.estado = True
            else:
                self.estado = False
    
    def parpadear(self, activar: bool = True) -> None:
        """
        Activa o desactiva el modo intermitente del LED.
        
        Args:
            activar: True para activar parpadeo, False para desactivar
        """
        self.intermitente = activar


# Ejemplo de uso y pruebas
if __name__ == "__main__":
    print("=== Sistema de Sensores IoT - Comisaría de Policía ===\n")
    
    # Crear instancias de sensores
    dht_sala = DHT("DHT_001", "Sala de detención", "DHT22")
    ldr_pasillo = LDR("LDR_001", "Pasillo principal")
    mq2_oficina = MQ2("MQ2_001", "Oficinas")
    mq135_interrogatorio = MQ135("MQ135_001", "Sala de interrogatorios")
    ventilador_servidor = Ventilador("VENT_001", "Sala de servidores")
    led_entrada = LED("LED_001", "Entrada principal", "blanco")
    
    # Configurar actuadores
    ventilador_servidor.set_velocidad(75)
    led_entrada.set_brillo(100)
    
    # Simular y mostrar datos
    sensores = [dht_sala, ldr_pasillo, mq2_oficina, mq135_interrogatorio, 
                ventilador_servidor, led_entrada]
    
    for sensor in sensores:
        print(f"Sensor: {sensor.tipo} ({sensor.id})")
        print(f"Ubicación: {sensor.ubicacion}")
        sensor.simular_dato()
        estado = sensor.get_estado()
        print(f"Estado: {estado['estado']}")
        print(f"Valores: {estado['valor']}")
        print(f"Timestamp: {estado['timestamp']}")
        print("-" * 60)