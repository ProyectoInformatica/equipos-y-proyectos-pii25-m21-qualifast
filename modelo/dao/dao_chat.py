from modelo.dao.conexion_db import conectar

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
            query = """
                    SELECT CASE WHEN emisor = %s THEN receptor ELSE emisor END as contacto,
                           SUM(CASE WHEN receptor = %s AND estado IN ('RECIBIDO', 'ENTREGADO') THEN 1 ELSE 0 END) as no_leidos
                    FROM mensajes_chat WHERE emisor = %s OR receptor = %s
                    GROUP BY contacto ORDER BY MAX(timestamp) DESC
                    """
            cursor.execute(query, (mi_usuario, mi_usuario, mi_usuario, mi_usuario))
            contactos = cursor.fetchall()
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
                r['fecha'] = r['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
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