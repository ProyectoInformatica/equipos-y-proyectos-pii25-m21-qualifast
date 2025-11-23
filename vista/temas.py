import flet as ft

COLORS = {
    'bg': '#0f1724',         # Fondo principal muy oscuro
    'card': '#1f2937',       # Fondo de tarjetas (gris azulado oscuro)
    'room_bg': '#374151',    # Fondo de habitaciones en el mapa
    'text': '#f3f4f6',       # Texto blanco/gris claro
    'muted': '#9ca3af',      # Texto secundario
    'accent': '#38bdf8',     # Azul brillante para acentos
    'bad': '#ef4444',        # Rojo para errores/borrar
    'good': '#22c55e',       # Verde para éxito
    'glass': '#374151',      # Color semitransparente (simulado sólido por ahora)
    'door_open': '#22c55e',  # Verde
    'door_closed': '#ef4444' # Rojo
}

DEVICE_ICONS = {
    'dht': '🌡️',
    'mq2': '🔥',
    'mq135': '💨',
    'ldr': '☀️',
    'leds': '💡',
    'fan': '❄️',
    'cam': '📷'
}