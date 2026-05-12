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

-- ==========================================
-- 5. CHAT INTERNO (NUEVO)
-- ==========================================
CREATE TABLE IF NOT EXISTS mensajes_chat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emisor VARCHAR(50) NOT NULL,
    receptor VARCHAR(50) NOT NULL,
    texto TEXT NOT NULL,
    estado VARCHAR(20) DEFAULT 'RECIBIDO', -- 'RECIBIDO', 'LEIDO'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_chat_participantes (emisor, receptor)
);

-- ==========================================
-- 6. CONJUNTO DE DATOS DE PRUEBA (MAX. PUNTUACIÓN)
-- ==========================================
-- Insertar Roles y Configuración
INSERT IGNORE INTO roles (id, nombre) VALUES (1, 'comisario'), (2, 'inspector'), (3, 'policia');
INSERT IGNORE INTO configuracion (clave, valor) VALUES ('temp_max', '28.0'), ('luz_min', '400.0');
INSERT IGNORE INTO celdas (id, codigo, capacidad) VALUES (1, 'Celda 1', 2), (2, 'Celda 2', 2), (3, 'Celda 3', 1), (4, 'Celda 4', 1);

-- Insertar Usuario Comisario
-- Lo ponemos en texto plano. Como no empieza por "$2b$", Python activará el modo compatibilidad.
INSERT IGNORE INTO personas (id, dni, nombre, apellidos, tipo_persona) VALUES (1, '00000000A', 'Admin', 'Principal', 'USUARIO');
INSERT IGNORE INTO usuarios (persona_id, username, password, rol_id) VALUES (1, 'comisario', '1234', 1);

-- Insertar Presos de Prueba
INSERT IGNORE INTO personas (id, dni, nombre, apellidos, tipo_persona) VALUES
(2, '12345678X', 'Juan', 'Pérez Gómez', 'PRESO'),
(3, '87654321Y', 'María', 'López Díaz', 'PRESO');

INSERT IGNORE INTO presos (persona_id, delito) VALUES
(2, 'Robo con fuerza en cajero automático'),
(3, 'Fraude fiscal y blanqueo de capitales');

-- Insertar Asignaciones de Celda de los presos
INSERT IGNORE INTO asignacion_celdas (preso_id, celda_id, fecha_ingreso) VALUES
(2, 1, DATE_SUB(NOW(), INTERVAL 5 DAY)),
(3, 2, DATE_SUB(NOW(), INTERVAL 2 DAY));

-- Insertar Sensores
INSERT IGNORE INTO sensores (id, codigo, nombre, unidad) VALUES
(1, 'dht_temp', 'DHT11 - Temperatura', '°C'),
(2, 'dht_hum', 'DHT11 - Humedad', '%'),
(3, 'ldr_luz', 'LDR - Luz', 'Lux'),
(4, 'mq2_humo', 'MQ-2 - Humo', 'ppm'),
(5, 'mq135_aire', 'MQ-135 - Aire', 'ppm');

-- Insertar Actuadores
INSERT IGNORE INTO actuadores (id, uid, label, estado, mode) VALUES
(1, 'door-1', 'P1', 'cerrada', 'manual'), (2, 'door-2', 'P2', 'cerrada', 'manual'),
(3, 'door-3', 'P3', 'cerrada', 'manual'), (4, 'door-4', 'P4', 'cerrada', 'manual'),
(5, 'leds', 'Iluminación', 'off', 'auto'), (6, 'fan', 'Ventilación', 'off', 'auto');

-- Insertar Logs Históricos de Sensores y Actuadores
INSERT IGNORE INTO sensores_log (sensor_id, valor, timestamp) VALUES
(1, 24.5, DATE_SUB(NOW(), INTERVAL 15 MINUTE)),
(1, 24.8, DATE_SUB(NOW(), INTERVAL 10 MINUTE)),
(3, 450.0, DATE_SUB(NOW(), INTERVAL 15 MINUTE)),
(3, 410.0, DATE_SUB(NOW(), INTERVAL 10 MINUTE));

INSERT IGNORE INTO historico_actuadores (actuador_id, usuario_id, accion, timestamp) VALUES
(1, 1, 'abierta', DATE_SUB(NOW(), INTERVAL 2 HOUR)),
(1, 1, 'cerrada', DATE_SUB(NOW(), INTERVAL 1 HOUR)),
(5, NULL, 'on', DATE_SUB(NOW(), INTERVAL 30 MINUTE));

-- EVENTO LIMPIEZA
SET GLOBAL event_scheduler = ON;
CREATE EVENT IF NOT EXISTS limpiar_sensores_antiguos
ON SCHEDULE EVERY 1 DAY
DO DELETE FROM sensores_log WHERE timestamp < NOW() - INTERVAL 30 DAY;

USE comisaria_db;

CREATE TABLE IF NOT EXISTS mensajes_chat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emisor VARCHAR(50) NOT NULL,
    receptor VARCHAR(50) NOT NULL,
    texto TEXT NOT NULL,
    estado VARCHAR(20) DEFAULT 'RECIBIDO',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_chat_participantes (emisor, receptor)
);