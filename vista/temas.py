import flet as ft

COLORS = {
    'bg': '#0f1724',         # Fondo principal
    'card': '#1f2937',       # Fondo tarjetas
    'room_bg': '#374151',    # Habitaciones
    'text': '#f3f4f6',       # Texto principal
    'muted': '#9ca3af',      # Texto secundario
    'accent': '#38bdf8',     # Azul cian
    'bad': '#ef4444',        # Rojo error
    'good': '#22c55e',       # Verde éxito
    'ok': '#22c55e',         # Alias verde
    'glass': '#374151',      # Fondo semitransparente
    'door_open': '#22c55e',
    'door_closed': '#ef4444'
}

# --- NUEVOS ICONOS SEGÚN ESPECIFICACIONES ---
DEVICE_ICONS = {
    'dht11': '🌡️',      # Temperatura/Humedad
    'dht22': '🌡️',      # (Variante precisión)
    'ldr': '☀️',        # Fotorresistor
    'mq-2': '🔥',       # Humo/Gas
    'mq-135': '☣️',     # Calidad Aire
    'leds': '💡',       # Diodos LED
    'motor': '⚙️',      # Motor DC (Puertas)
    'fan': '❄️',        # Ventilador
    'esp32': '📶',      # Placa Controladora
    'cam': '📷'         # Cámara OV2640
}