# =====================================================================
# PATRÓN FACHADA (Facade Pattern)
# Este archivo actúa como un enrutador central. Agrupa los módulos DAO
# para que el resto de la aplicación (main.py y vistas) no tenga que
# cambiar sus imports.
# =====================================================================

# 1. Motor de Base de Datos y Red
from modelo.dao.conexion_db import (
    LOCAL_CONFIG,
    ESP32_IP,
    ESP32_CAM_IP,
    probar_conexion,
    load_local_config,
    save_local_config
)

# 2. Módulo de Gestión de Personal y Presos
from modelo.dao.dao_usuarios import (
    validar_usuario,
    get_usuarios,
    add_usuario,
    update_usuario,
    delete_usuario,
    get_presos,
    add_preso,
    update_preso,
    delete_preso
)

# 3. Módulo de Hardware IoT y Configuración
from modelo.dao.dao_iot import (
    get_all_sensores_log_csv,
    get_all_actuadores_log_csv,
    obtener_estado_esp32,
    registrar_dato_sensor,
    get_configuracion,
    save_configuracion,
    get_estado_actuadores,
    toggle_actuador,
    set_estado_actuador,
    toggle_modo_actuador,
    get_ultimos_sensores_raw,
    get_promedio_sensores_por_hora,
    get_consumo_electrico,
    get_log_actuadores_paginado
)

# 4. Módulo de Mensajería Interna
from modelo.dao.dao_chat import (
    enviar_mensaje,
    get_contactos_chat,
    get_mensajes_chat,
    marcar_mensajes_entregados,
    marcar_mensajes_leidos,
    get_all_chats_csv
)