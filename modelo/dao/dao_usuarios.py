import bcrypt
import random
import base64
from modelo.dao.conexion_db import conectar

def _convertir_a_base64(blob):
    if blob:
        return base64.b64encode(blob).decode('utf-8')
    return None

def validar_usuario(u, p):
    conexion = conectar()
    rol, user_id, foto_b64 = None, None, None
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = """
                    SELECT u.password, r.nombre as rol, p.id, p.foto
                    FROM usuarios u
                             JOIN personas p ON u.persona_id = p.id
                             JOIN roles r ON u.rol_id = r.id
                    WHERE u.username = %s AND p.activo = 1
                    """
            cursor.execute(query, (u,))
            usuario = cursor.fetchone()

            if usuario:
                hash_db = usuario['password']
                match = False
                if hash_db.startswith('$2b$') or hash_db.startswith('$2a$'):
                    if bcrypt.checkpw(p.encode('utf-8'), hash_db.encode('utf-8')):
                        match = True
                elif p == hash_db:
                    match = True

                if match:
                    rol, user_id = usuario['rol'], usuario['id']
                    foto_b64 = _convertir_a_base64(usuario['foto'])
        finally:
            conexion.close()
    return rol, user_id, foto_b64

def get_usuarios():
    conexion = conectar()
    res = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = """
                    SELECT p.id, u.username as user, u.password, r.nombre as rol, p.foto
                    FROM usuarios u
                        JOIN personas p ON u.persona_id = p.id
                        JOIN roles r ON u.rol_id = r.id
                    WHERE p.activo = 1
                    ORDER BY p.fecha_alta DESC
                    """
            cursor.execute(query)
            datos = cursor.fetchall()
            for d in datos:
                d['foto'] = _convertir_a_base64(d['foto'])
                res.append(d)
        finally:
            conexion.close()
    return res

def add_usuario(u, p, r, foto_bytes=None):
    conexion = conectar()
    if conexion:
        try:
            conexion.start_transaction()
            cursor = conexion.cursor()
            dni = f"U{random.randint(1000, 9999)}X"
            cursor.execute(
                "INSERT INTO personas (dni, nombre, apellidos, tipo_persona, foto) VALUES (%s, %s, %s, 'USUARIO', %s)",
                (dni, u, 'Personal', foto_bytes))
            persona_id = cursor.lastrowid
            cursor.execute("SELECT id FROM roles WHERE nombre = %s", (r,))
            rol_id = cursor.fetchone()[0]
            hashed = bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("INSERT INTO usuarios (persona_id, username, password, rol_id) VALUES (%s, %s, %s, %s)",
                           (persona_id, u, hashed, rol_id))
            conexion.commit()
            return True
        except:
            conexion.rollback()
        finally:
            conexion.close()
    return False

def update_usuario(uid, user, password, rol, foto_bytes=None):
    conexion = conectar()
    if conexion:
        try:
            conexion.start_transaction()
            cursor = conexion.cursor()
            if foto_bytes:
                cursor.execute("UPDATE personas SET nombre=%s, foto=%s WHERE id=%s", (user, foto_bytes, uid))
            else:
                cursor.execute("UPDATE personas SET nombre=%s WHERE id=%s", (user, uid))

            cursor.execute("SELECT id FROM roles WHERE nombre = %s", (rol,))
            rol_id = cursor.fetchone()[0]
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("UPDATE usuarios SET username=%s, password=%s, rol_id=%s WHERE persona_id=%s",
                           (user, hashed, rol_id, uid))
            conexion.commit()
            return True
        except:
            conexion.rollback()
        finally:
            conexion.close()
    return False

def delete_usuario(uid):
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("UPDATE personas SET activo = 0, fecha_baja = NOW() WHERE id=%s", (uid,))
            conexion.commit()
            return True
        finally:
            conexion.close()
    return False

def get_presos():
    conexion = conectar()
    res = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = """
                    SELECT p.id, CONCAT(p.nombre, ' ', p.apellidos) as nombre, pr.delito, c.codigo as celda,
                           DATE_FORMAT(ac.fecha_ingreso, '%d/%m/%Y %H:%M') as fecha_ingreso, p.foto
                    FROM personas p
                             JOIN presos pr ON p.id = pr.persona_id
                             LEFT JOIN asignacion_celdas ac ON pr.persona_id = ac.preso_id AND ac.activo = 1
                             LEFT JOIN celdas c ON ac.celda_id = c.id
                    WHERE p.activo = 1 ORDER BY p.fecha_alta DESC
                    """
            cursor.execute(query)
            datos = cursor.fetchall()
            for d in datos:
                d['foto'] = _convertir_a_base64(d['foto'])
                res.append(d)
        finally:
            conexion.close()
    return res

def add_preso(nombre_completo, delito, celda_codigo, foto_bytes=None):
    conexion = conectar()
    if conexion:
        try:
            conexion.start_transaction()
            cursor = conexion.cursor()
            partes = nombre_completo.split(" ", 1)
            nombre = partes[0]
            apellidos = partes[1] if len(partes) > 1 else "Desconocido"
            dni = f"P{random.randint(10000, 99999)}Z"
            cursor.execute(
                "INSERT INTO personas (dni, nombre, apellidos, tipo_persona, foto) VALUES (%s, %s, %s, 'PRESO', %s)",
                (dni, nombre, apellidos, foto_bytes))
            persona_id = cursor.lastrowid
            cursor.execute("INSERT INTO presos (persona_id, delito) VALUES (%s, %s)", (persona_id, delito))
            cursor.execute("SELECT id FROM celdas WHERE codigo = %s", (celda_codigo,))
            row = cursor.fetchone()
            celda_id = row[0] if row else 1
            cursor.execute("INSERT INTO asignacion_celdas (preso_id, celda_id) VALUES (%s, %s)", (persona_id, celda_id))
            conexion.commit()
            return True
        except:
            conexion.rollback()
        finally:
            conexion.close()
    return False

def update_preso(pid, dat, foto_bytes=None):
    conexion = conectar()
    if conexion:
        try:
            conexion.start_transaction()
            cursor = conexion.cursor()
            partes = dat.get('nombre', '').split(" ", 1)
            nombre = partes[0]
            apellidos = partes[1] if len(partes) > 1 else "Desconocido"

            if foto_bytes:
                cursor.execute("UPDATE personas SET nombre=%s, apellidos=%s, foto=%s WHERE id=%s",
                               (nombre, apellidos, foto_bytes, pid))
            else:
                cursor.execute("UPDATE personas SET nombre=%s, apellidos=%s WHERE id=%s", (nombre, apellidos, pid))

            cursor.execute("UPDATE presos SET delito=%s WHERE persona_id=%s", (dat.get('delito'), pid))
            cursor.execute("SELECT id FROM celdas WHERE codigo = %s", (dat.get('celda'),))
            nueva_celda_id = cursor.fetchone()[0]
            cursor.execute(
                "UPDATE asignacion_celdas SET activo = 0, fecha_salida = NOW() WHERE preso_id = %s AND activo = 1",
                (pid,))
            cursor.execute("INSERT INTO asignacion_celdas (preso_id, celda_id) VALUES (%s, %s)", (pid, nueva_celda_id))
            conexion.commit()
            return True
        except:
            conexion.rollback()
        finally:
            conexion.close()
    return False

def delete_preso(pid):
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("UPDATE personas SET activo = 0, fecha_baja = NOW() WHERE id=%s", (pid,))
            cursor.execute(
                "UPDATE asignacion_celdas SET activo = 0, fecha_salida = NOW() WHERE preso_id=%s AND activo=1", (pid,))
            conexion.commit()
            return True
        finally:
            conexion.close()
    return False