CREATE DATABASE IF NOT EXISTS comisaria_db DEFAULT CHARACTER SET utf8mb4;
USE comisaria_db;

-- ==========================================
-- 1. CATÁLOGOS Y CONFIGURACIÓN
-- ==========================================
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS configuracion (
    clave VARCHAR(50) PRIMARY KEY,
    valor VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS celdas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    capacidad INT NOT NULL DEFAULT 1,
    activo BOOLEAN DEFAULT 1 NOT NULL
);

-- ==========================================
-- 2. HERENCIA: PERSONAS -> (USUARIOS / PRESOS)
-- ==========================================
CREATE TABLE IF NOT EXISTS personas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dni VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    foto MEDIUMBLOB NULL,
    tipo_persona ENUM('USUARIO', 'PRESO') NOT NULL,
    fecha_alta DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_baja DATETIME NULL,
    activo BOOLEAN DEFAULT 1 NOT NULL
);

CREATE TABLE IF NOT EXISTS usuarios (
    persona_id INT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol_id INT NOT NULL,
    FOREIGN KEY (persona_id) REFERENCES personas(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS presos (
    persona_id INT PRIMARY KEY,
    delito VARCHAR(255) NOT NULL,
    FOREIGN KEY (persona_id) REFERENCES personas(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ==========================================
-- 3. ENTIDAD DÉBIL / RELACIÓN TEMPORAL (PRESOS-CELDAS)
-- ==========================================
CREATE TABLE IF NOT EXISTS asignacion_celdas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    preso_id INT NOT NULL,
    celda_id INT NOT NULL,
    fecha_ingreso DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_salida DATETIME NULL,
    activo BOOLEAN DEFAULT 1 NOT NULL,
    FOREIGN KEY (preso_id) REFERENCES presos(persona_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (celda_id) REFERENCES celdas(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ==========================================
-- 4. IOT: SENSORES Y ACTUADORES
-- ==========================================
CREATE TABLE IF NOT EXISTS sensores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    unidad VARCHAR(10) NOT NULL,
    activo BOOLEAN DEFAULT 1 NOT NULL
);

CREATE TABLE IF NOT EXISTS sensores_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT NOT NULL,
    valor FLOAT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (sensor_id) REFERENCES sensores(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_timestamp (timestamp)
);

CREATE TABLE IF NOT EXISTS actuadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uid VARCHAR(50) UNIQUE NOT NULL,
    label VARCHAR(50) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'cerrada',
    mode VARCHAR(20) NOT NULL DEFAULT 'manual',
    activo BOOLEAN DEFAULT 1 NOT NULL
);

CREATE TABLE IF NOT EXISTS historico_actuadores (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    actuador_id INT NOT NULL,
    usuario_id INT NULL,
    accion VARCHAR(50) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (actuador_id) REFERENCES actuadores(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(persona_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_act_time (actuador_id, timestamp)
);

CREATE TABLE IF NOT EXISTS mensajes_chat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emisor VARCHAR(50) NOT NULL,
    receptor VARCHAR(50) NOT NULL,
    texto TEXT NOT NULL,
    estado VARCHAR(20) DEFAULT 'RECIBIDO',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_chat_participantes (emisor, receptor)
);

-- ==========================================
-- 5. CONJUNTO DE DATOS DE PRUEBA
-- ==========================================
INSERT IGNORE INTO roles (id, nombre) VALUES (1, 'comisario'), (2, 'inspector'), (3, 'policia');
INSERT IGNORE INTO configuracion (clave, valor) VALUES ('temp_max', '28.0'), ('luz_min', '400.0');
INSERT IGNORE INTO celdas (id, codigo, capacidad) VALUES (1, 'Celda 1', 2), (2, 'Celda 2', 2), (3, 'Celda 3', 1), (4, 'Celda 4', 1);

INSERT IGNORE INTO personas (id, dni, nombre, apellidos, tipo_persona) VALUES (1, '00000000A', 'Admin', 'Principal', 'USUARIO');
INSERT IGNORE INTO usuarios (persona_id, username, password, rol_id) VALUES (1, 'comisario', '1234', 1);

INSERT IGNORE INTO personas (id, dni, nombre, apellidos, tipo_persona) VALUES
(2, '12345678X', 'Juan', 'Pérez Gómez', 'PRESO'),
(3, '87654321Y', 'María', 'López Díaz', 'PRESO');

INSERT IGNORE INTO presos (persona_id, delito) VALUES
(2, 'Robo con fuerza en cajero automático'),
(3, 'Fraude fiscal y blanqueo de capitales');

INSERT IGNORE INTO asignacion_celdas (preso_id, celda_id, fecha_ingreso) VALUES
(2, 1, DATE_SUB(NOW(), INTERVAL 5 DAY)),
(3, 2, DATE_SUB(NOW(), INTERVAL 2 DAY));

INSERT IGNORE INTO sensores (id, codigo, nombre, unidad) VALUES
(1, 'dht_temp', 'DHT11 - Temperatura', '°C'),
(2, 'dht_hum', 'DHT11 - Humedad', '%'),
(3, 'ldr_luz', 'LDR - Luz', 'Lux'),
(4, 'mq2_humo', 'MQ-2 - Humo', 'ppm'),
(5, 'mq135_aire', 'MQ-135 - Aire', 'ppm');

INSERT IGNORE INTO actuadores (id, uid, label, estado, mode) VALUES
(1, 'door-1', 'P1', 'cerrada', 'manual'), (2, 'door-2', 'P2', 'cerrada', 'manual'),
(3, 'door-3', 'P3', 'cerrada', 'manual'), (4, 'door-4', 'P4', 'cerrada', 'manual'),
(5, 'leds', 'Iluminación', 'off', 'auto'), (6, 'fan', 'Ventilación', 'off', 'auto');

INSERT IGNORE INTO sensores_log (sensor_id, valor, timestamp) VALUES
(1, 24.5, DATE_SUB(NOW(), INTERVAL 15 MINUTE)),
(1, 24.8, DATE_SUB(NOW(), INTERVAL 10 MINUTE)),
(3, 450.0, DATE_SUB(NOW(), INTERVAL 15 MINUTE)),
(3, 410.0, DATE_SUB(NOW(), INTERVAL 10 MINUTE));

INSERT IGNORE INTO historico_actuadores (actuador_id, usuario_id, accion, timestamp) VALUES
(1, 1, 'abierta', DATE_SUB(NOW(), INTERVAL 2 HOUR)),
(1, 1, 'cerrada', DATE_SUB(NOW(), INTERVAL 1 HOUR)),
(5, NULL, 'on', DATE_SUB(NOW(), INTERVAL 30 MINUTE));

-- ==========================================
-- 6. EVENTO LIMPIEZA
-- ==========================================
SET GLOBAL event_scheduler = ON;
CREATE EVENT IF NOT EXISTS limpiar_sensores_antiguos
ON SCHEDULE EVERY 1 DAY
DO DELETE FROM sensores_log WHERE timestamp < NOW() - INTERVAL 30 DAY;

-- ==========================================
-- 7. AMPLIACIÓN DE DATOS PARA EVALUACIÓN (RÚBRICA)
-- ==========================================

-- 7.A CREACIÓN DE 5 COMISARIOS
INSERT IGNORE INTO personas (id, dni, nombre, apellidos, tipo_persona) VALUES
(4, '00000004C', 'Laura', 'García', 'USUARIO'),
(5, '00000005C', 'Carlos', 'Martínez', 'USUARIO'),
(6, '00000006C', 'Elena', 'Sánchez', 'USUARIO'),
(7, '00000007C', 'Javier', 'Gómez', 'USUARIO');

INSERT IGNORE INTO usuarios (persona_id, username, password, rol_id) VALUES
(4, 'comisario2', '1234', 1), (5, 'comisario3', '1234', 1),
(6, 'comisario4', '1234', 1), (7, 'comisario5', '1234', 1);

-- 7.B CREACIÓN DE 5 INSPECTORES
INSERT IGNORE INTO personas (id, dni, nombre, apellidos, tipo_persona) VALUES
(8, '00000008I', 'Sofía', 'Ruiz', 'USUARIO'), (9, '00000009I', 'Diego', 'Hernández', 'USUARIO'),
(10, '00000010I', 'Ana', 'Díaz', 'USUARIO'), (11, '00000011I', 'David', 'Moreno', 'USUARIO'),
(12, '00000012I', 'Lucía', 'Muñoz', 'USUARIO');

INSERT IGNORE INTO usuarios (persona_id, username, password, rol_id) VALUES
(8, 'inspector1', '1234', 2), (9, 'inspector2', '1234', 2),
(10, 'inspector3', '1234', 2), (11, 'inspector4', '1234', 2),
(12, 'inspector5', '1234', 2);

-- 7.C CREACIÓN DE 9 POLICÍAS (Rol principal)
INSERT IGNORE INTO personas (id, dni, nombre, apellidos, tipo_persona) VALUES
(13, '00000013P', 'Mario', 'Álvarez', 'USUARIO'), (14, '00000014P', 'Paula', 'Romero', 'USUARIO'),
(15, '00000015P', 'Hugo', 'Alonso', 'USUARIO'), (16, '00000016P', 'Carmen', 'Gutiérrez', 'USUARIO'),
(17, '00000017P', 'Pablo', 'Navarro', 'USUARIO'), (18, '00000018P', 'Julia', 'Torres', 'USUARIO'),
(19, '00000019P', 'Alejandro', 'Domínguez', 'USUARIO'), (20, '00000020P', 'Alba', 'Vázquez', 'USUARIO'),
(21, '00000021P', 'Daniel', 'Ramos', 'USUARIO');

INSERT IGNORE INTO usuarios (persona_id, username, password, rol_id) VALUES
(13, 'policia1', '1234', 3), (14, 'policia2', '1234', 3), (15, 'policia3', '1234', 3),
(16, 'policia4', '1234', 3), (17, 'policia5', '1234', 3), (18, 'policia6', '1234', 3),
(19, 'policia7', '1234', 3), (20, 'policia8', '1234', 3), (21, 'policia9', '1234', 3);

-- 7.D RELACIONES BIDIRECCIONALES (CHATS ENTRE ROLES)
INSERT IGNORE INTO mensajes_chat (emisor, receptor, texto, estado, timestamp) VALUES
('policia1', 'comisario', 'Novedades en la celda 1, el preso está alterado.', 'LEIDO', DATE_SUB(NOW(), INTERVAL 2 DAY)),
('comisario', 'policia1', 'Entendido, manda a inspector1 a revisar.', 'LEIDO', DATE_SUB(NOW(), INTERVAL 47 HOUR)),
('policia1', 'inspector1', 'El comisario pide revisión en Celda 1.', 'LEIDO', DATE_SUB(NOW(), INTERVAL 46 HOUR)),

('policia2', 'comisario2', 'Luces de recepción fallando.', 'ENTREGADO', DATE_SUB(NOW(), INTERVAL 1 DAY)),
('policia2', 'inspector2', 'Reporte de guardia enviado por mail.', 'LEIDO', DATE_SUB(NOW(), INTERVAL 20 HOUR)),

('policia3', 'comisario3', 'Solicito permiso de acceso a armería.', 'LEIDO', DATE_SUB(NOW(), INTERVAL 15 HOUR)),
('policia3', 'inspector3', 'Armería asegurada.', 'RECIBIDO', DATE_SUB(NOW(), INTERVAL 5 HOUR)),

('policia4', 'comisario4', 'Temperatura del servidor estable.', 'LEIDO', DATE_SUB(NOW(), INTERVAL 12 HOUR)),
('policia4', 'inspector4', 'Turno finalizado sin incidencias.', 'LEIDO', DATE_SUB(NOW(), INTERVAL 10 HOUR)),

('policia5', 'comisario5', 'Problema con la cámara exterior.', 'LEIDO', DATE_SUB(NOW(), INTERVAL 8 HOUR)),
('policia5', 'inspector5', 'Cámara exterior revisada.', 'ENTREGADO', DATE_SUB(NOW(), INTERVAL 7 HOUR)),

('policia6', 'comisario', 'Necesitamos refuerzos en zona celdas.', 'LEIDO', DATE_SUB(NOW(), INTERVAL 6 HOUR)),
('policia6', 'inspector1', 'Atentos a la celda 3.', 'RECIBIDO', DATE_SUB(NOW(), INTERVAL 5 HOUR)),

('policia7', 'comisario2', 'Alarma de humo activada en pasillo, falsa alarma.', 'LEIDO', DATE_SUB(NOW(), INTERVAL 4 HOUR)),
('policia7', 'inspector2', 'Falsa alarma registrada en log.', 'LEIDO', DATE_SUB(NOW(), INTERVAL 3 HOUR)),

('policia8', 'comisario3', 'Preso 12345678X trasladado.', 'ENTREGADO', DATE_SUB(NOW(), INTERVAL 2 HOUR)),
('policia8', 'inspector3', 'Traslado completado.', 'LEIDO', DATE_SUB(NOW(), INTERVAL 90 MINUTE)),

('policia9', 'comisario4', 'Fin de la ronda perimetral.', 'LEIDO', DATE_SUB(NOW(), INTERVAL 1 HOUR)),
('policia9', 'inspector4', 'Ronda sin novedad.', 'RECIBIDO', DATE_SUB(NOW(), INTERVAL 30 MINUTE));

-- 7.E HISTORIAL DE ACTUADORES (ACTIVIDAD DE USUARIOS)
INSERT IGNORE INTO historico_actuadores (actuador_id, usuario_id, accion, timestamp) VALUES
(1, 13, 'abierta', DATE_SUB(NOW(), INTERVAL 48 HOUR)), (1, 13, 'cerrada', DATE_SUB(NOW(), INTERVAL 47 HOUR)),
(2, 14, 'abierta', DATE_SUB(NOW(), INTERVAL 36 HOUR)), (2, 15, 'cerrada', DATE_SUB(NOW(), INTERVAL 35 HOUR)),
(3, 8, 'abierta', DATE_SUB(NOW(), INTERVAL 24 HOUR)), (3, 8, 'cerrada', DATE_SUB(NOW(), INTERVAL 23 HOUR)),
(4, 4, 'abierta', DATE_SUB(NOW(), INTERVAL 12 HOUR)), (4, 4, 'cerrada', DATE_SUB(NOW(), INTERVAL 11 HOUR)),
(5, 1, 'on', DATE_SUB(NOW(), INTERVAL 5 HOUR)), (5, 16, 'off', DATE_SUB(NOW(), INTERVAL 4 HOUR)),
(6, 17, 'on', DATE_SUB(NOW(), INTERVAL 3 HOUR)), (6, 18, 'off', DATE_SUB(NOW(), INTERVAL 2 HOUR));

-- 7.F PERFIL DE SENSORES RICOS
INSERT IGNORE INTO sensores_log (sensor_id, valor, timestamp) VALUES
(1, 21.0, DATE_SUB(NOW(), INTERVAL 24 HOUR)), (2, 45.0, DATE_SUB(NOW(), INTERVAL 24 HOUR)), (3, 300.0, DATE_SUB(NOW(), INTERVAL 24 HOUR)), (4, 15.0, DATE_SUB(NOW(), INTERVAL 24 HOUR)), (5, 410.0, DATE_SUB(NOW(), INTERVAL 24 HOUR)),
(1, 21.5, DATE_SUB(NOW(), INTERVAL 20 HOUR)), (2, 44.5, DATE_SUB(NOW(), INTERVAL 20 HOUR)), (3, 350.0, DATE_SUB(NOW(), INTERVAL 20 HOUR)), (4, 16.0, DATE_SUB(NOW(), INTERVAL 20 HOUR)), (5, 415.0, DATE_SUB(NOW(), INTERVAL 20 HOUR)),
(1, 22.1, DATE_SUB(NOW(), INTERVAL 16 HOUR)), (2, 43.0, DATE_SUB(NOW(), INTERVAL 16 HOUR)), (3, 400.0, DATE_SUB(NOW(), INTERVAL 16 HOUR)), (4, 17.5, DATE_SUB(NOW(), INTERVAL 16 HOUR)), (5, 420.0, DATE_SUB(NOW(), INTERVAL 16 HOUR)),
(1, 23.5, DATE_SUB(NOW(), INTERVAL 12 HOUR)), (2, 42.0, DATE_SUB(NOW(), INTERVAL 12 HOUR)), (3, 600.0, DATE_SUB(NOW(), INTERVAL 12 HOUR)), (4, 20.0, DATE_SUB(NOW(), INTERVAL 12 HOUR)), (5, 435.0, DATE_SUB(NOW(), INTERVAL 12 HOUR)),
(1, 24.8, DATE_SUB(NOW(), INTERVAL 8 HOUR)),  (2, 40.5, DATE_SUB(NOW(), INTERVAL 8 HOUR)),  (3, 850.0, DATE_SUB(NOW(), INTERVAL 8 HOUR)),  (4, 22.0, DATE_SUB(NOW(), INTERVAL 8 HOUR)),  (5, 450.0, DATE_SUB(NOW(), INTERVAL 8 HOUR)),
(1, 25.2, DATE_SUB(NOW(), INTERVAL 4 HOUR)),  (2, 39.0, DATE_SUB(NOW(), INTERVAL 4 HOUR)),  (3, 900.0, DATE_SUB(NOW(), INTERVAL 4 HOUR)),  (4, 23.5, DATE_SUB(NOW(), INTERVAL 4 HOUR)),  (5, 460.0, DATE_SUB(NOW(), INTERVAL 4 HOUR)),
(1, 25.0, DATE_SUB(NOW(), INTERVAL 1 HOUR)),  (2, 39.5, DATE_SUB(NOW(), INTERVAL 1 HOUR)),  (3, 880.0, DATE_SUB(NOW(), INTERVAL 1 HOUR)),  (4, 21.0, DATE_SUB(NOW(), INTERVAL 1 HOUR)),  (5, 455.0, DATE_SUB(NOW(), INTERVAL 1 HOUR));

-- SELECT * FROM sensores_log ORDER BY timestamp DESC LIMIT 10;