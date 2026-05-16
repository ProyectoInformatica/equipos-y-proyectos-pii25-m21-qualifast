import base64
from modelo.dao.conexion_db import conectar

def _convertir_a_base64(blob):
    if blob:
        return base64.b64encode(blob).decode('utf-8')
    return None

def enviar_mensaje(emisor, receptor, texto):
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            query = "INSERT INTO mensajes_chat (emisor, receptor, texto, estado) VALUES (%s, %s, %s, 'RECIBIDO')"
            cursor.execute(query, (emisor, receptor, texto))
            conexion.commit()
            return True
        finally:
            conexion.close()
    return False

def get_contactos_chat(mi_usuario):
    conexion = conectar()
    contactos = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            # AÑADIDO: LEFT JOIN roles r para obtener r.nombre as rol
            query = """
                    SELECT 
                        c.contacto,
                        c.no_leidos,
                        p.foto,
                        r.nombre as rol
                    FROM (
                        SELECT CASE WHEN emisor = %s THEN receptor ELSE emisor END as contacto,
                               SUM(CASE WHEN receptor = %s AND estado IN ('RECIBIDO', 'ENTREGADO') THEN 1 ELSE 0 END) as no_leidos,
                               MAX(timestamp) as m_time
                        FROM mensajes_chat WHERE emisor = %s OR receptor = %s
                        GROUP BY contacto
                    ) c
                    LEFT JOIN usuarios u ON u.username = c.contacto
                    LEFT JOIN personas p ON p.id = u.persona_id
                    LEFT JOIN roles r ON u.rol_id = r.id
                    ORDER BY c.m_time DESC
                    """
            cursor.execute(query, (mi_usuario, mi_usuario, mi_usuario, mi_usuario))
            for r in cursor.fetchall():
                if r['foto']:
                    r['foto'] = _convertir_a_base64(r['foto'])
                contactos.append(r)
        except Exception as e:
            print(f"[ERROR BD] Fallo en get_contactos_chat: {e}")
        finally:
            conexion.close()
    return contactos

def get_mensajes_chat(usuario1, usuario2):
    conexion = conectar()
    mensajes = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = """
                    SELECT emisor, receptor, texto, estado, timestamp
                    FROM mensajes_chat WHERE (emisor = %s AND receptor = %s) OR (emisor = %s AND receptor = %s)
                    ORDER BY timestamp ASC
                    """
            cursor.execute(query, (usuario1, usuario2, usuario2, usuario1))
            resultados = cursor.fetchall()
            for r in resultados:
                r['fecha'] = r['timestamp'].strftime('%H:%M')
                mensajes.append(r)
        finally:
            conexion.close()
    return mensajes

def marcar_mensajes_entregados(mi_usuario):
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            query = "UPDATE mensajes_chat SET estado = 'ENTREGADO' WHERE receptor = %s AND estado = 'RECIBIDO'"
            cursor.execute(query, (mi_usuario,))
            conexion.commit()
        except Exception as e:
            print(f"[ERROR BD] Fallo marcando entregados: {e}")
        finally:
            conexion.close()

def marcar_mensajes_leidos(emisor_contacto, mi_usuario):
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            query = "UPDATE mensajes_chat SET estado = 'LEIDO' WHERE emisor = %s AND receptor = %s AND estado IN ('RECIBIDO', 'ENTREGADO')"
            cursor.execute(query, (emisor_contacto, mi_usuario))
            conexion.commit()
        finally:
            conexion.close()

def eliminar_conversacion(usuario1, usuario2):
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            query = """
                    DELETE FROM mensajes_chat 
                    WHERE (emisor = %s AND receptor = %s) OR (emisor = %s AND receptor = %s)
                    """
            cursor.execute(query, (usuario1, usuario2, usuario2, usuario1))
            conexion.commit()
            return True
        except Exception as e:
            print(f"[ERROR BD] Fallo al vaciar historial de chat: {e}")
        finally:
            conexion.close()
    return False

def get_all_chats_csv():
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = "SELECT timestamp, emisor, receptor, texto, estado FROM mensajes_chat ORDER BY emisor, receptor, timestamp ASC"
            cursor.execute(query)
            res = []
            for r in cursor.fetchall():
                if r['timestamp']: r['timestamp'] = r['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                res.append(r)
            return res
        finally: conexion.close()
    return []