
<p align="center">
  <img src="assets/logo_qualifast.png" alt="Qualifast Buildings Logo" width="180" />
</p>

<h1 align="center">🏢 Qualifast Buildings – Estación de Policía Inteligente</h1>
<p align="center">
  <em>Proyecto IoT para la gestión automatizada y sostenible de una comisaría</em><br>
  <strong>Universidad Europea de Madrid – Grado en Ingeniería Informática</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white" alt="Python Badge"/>
  <img src="https://img.shields.io/badge/Flet-0.28.3-orange?logo=flet" alt="Flet Badge"/>
  <img src="https://img.shields.io/badge/MySQL-Database-blue?logo=mysql" alt="MySQL Badge"/>
  <img src="https://img.shields.io/badge/ESP32-IoT-green?logo=espressif" alt="ESP32 Badge"/>
  <img src="https://img.shields.io/github/license/alvarolopez/qualifast-buildings?color=lightgrey" alt="License Badge"/>
</p>

---

## 🧭 Descripción del proyecto

**Qualifast Buildings** desarrolla una solución **IoT** para optimizar la gestión de una **comisaría de policía inteligente**, integrando sensores y actuadores en una única plataforma de grado de producción.

El sistema permite **monitorizar condiciones ambientales en tiempo real**, controlar iluminación y ventilación de forma automática o manual, y gestionar las credenciales de los agentes mediante cifrado seguro. Cada usuario accede a una **interfaz gráfica interactiva y concurrente** personalizada según su rol (comisario, inspector o policía).

> 🎯 **Objetivo:** Mejorar la seguridad, eficiencia energética y sostenibilidad en instalaciones policiales mediante tecnologías IoT, bases de datos relacionales y control centralizado.

---

## 🧠 Tecnologías y Arquitectura

El proyecto ha evolucionado hacia una infraestructura modular altamente escalable:

| Tipo | Tecnología |
|------|-------------|
| 💻 Lógica y UI | Python 3 + Flet (Interfaces Concurrentes UI/UX Glassmorphism) |
| ⚙️ Hardware IoT | ESP32 (Control) y ESP32-CAM (CCTV MJPEG) |
| 💾 Base de Datos | MySQL (Pool de Conexiones persistentes) |
| 🔒 Seguridad | BCrypt (Cifrado asimétrico de credenciales y prevención doble cifrado) |
| 🧩 Arquitectura | MVC (Modelo-Vista-Controlador) + DAO (Data Access Object) + Facade |
| ⏱️ Concurrencia | Multithreading (Hilos independientes para UI, Recolección y Heartbeat IoT) |

---

## 🔌 Esquema Físico y Conexiones de Hardware

El sistema interactúa con un circuito físico gobernado por un microcontrolador ESP32 programado en Arduino C++. El mapeo de pines implementado es el siguiente:

| Componente | Tipo | GPIO | Alimentación | Función |
|------------|------|------|--------------|---------|
| **DHT22 / DHT11** | Entrada Digital | GPIO 4 | 3.3 V | Temperatura y Humedad |
| **LDR** | Entrada Analógica | GPIO 32 | 3.3 V (Div. tensión) | Luminosidad del entorno |
| **MQ-2** | Entrada Analógica | GPIO 33 | 5 V (VIN) | Detección de Humo y Gas |
| **LEDs** | Salida Digital | GPIO 13 | Desde el pin | Iluminación de pasillos/celdas |
| **Ventilador DC** | Salida Digital | GPIO 12 | 5 V (Vía transistor) | Climatización / Extracción |
| **Motor Cerraduras** | Salida Digital | GPIO 14 | 12 V (Vía relé) | *Reservado infraestructura acceso* |

> ⚠️ **Nota de Hardware:** Los componentes de 5V y 12V están aislados galvánicamente mediante transistores NPN (ej. 2N2222) y módulos relé. El ESP32 solo proporciona la señal lógica (3.3V).

### 📡 Configuración de Red IoT (Hotspot)
Para garantizar la portabilidad del proyecto durante demostraciones (y evitar configuraciones estáticas engorrosas dependientes del router de la universidad), el ESP32 y la cámara (ESP32-CAM) están configurados para conectarse a una **red Wi-Fi móvil (Hotspot) compartida desde el ordenador principal**. 
* Las IPs dinámicas asignadas por el Hotspot pueden modificarse en caliente en la pestaña de **Ajustes** de la aplicación Python sin necesidad de recompilar el código C++ de Arduino, guardándose automáticamente de forma persistente.

---

## ⚙️ Requisitos e Instalación

### 1️⃣ Base de Datos MySQL
1. Instala MySQL Server y asegúrate de que el servicio está en ejecución (puerto por defecto `3306`).
2. Ejecuta el script `Script SQL.sql` adjunto en la raíz del proyecto para generar la base de datos `comisaria_db`, sus tablas estructuradas y los datos genéricos de prueba (roles, administradores, celdas y sensores).

### 2️⃣ Entorno Python y Dependencias
Clona el repositorio y configura un entorno virtual para evitar conflictos de versiones:


git clone https://github.com/alvarolofra/qualifast-buildings.git
cd qualifast-buildings

# Crear entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

Instala las dependencias estrictas requeridas para garantizar la estabilidad visual y lógica de la versión de producción:

pip install -r requirements.txt

(O de forma manual):

pip install flet==0.28.3 flet-video==0.1.1 mysql-connector-python==9.6.0 bcrypt==5.0.0 requests==2.33.1

### 3️⃣ Ejecución del Sistema

Arranca el Controlador Principal. El recolector de datos IoT en segundo plano se lanzará automáticamente para consultar al hardware.

python main.py

**Credenciales por defecto:**
- Usuario: `comisario` | Contraseña: `1234`

## 📂 Estructura del Repositorio

📦 qualifast-buildings/

    ├── main.py                 # Enrutador Flet y bucles concurrentes principales 
    ├── Script SQL.sql          # Script de despliegue de base de datos MySQL 
    ├── modelo/ 
    │   └── dao/                # Objetos de Acceso a Datos (BD, Usuarios, IoT, Chat)
    │   └── manejador_datos.py  # Patrón Fachada centralizado 
    ├── vista/                  # Controladores de UI (Login, Dashboard, Chat, etc.)
    ├── servicios_iot/          # Microservicios de recolección en segundo plano (Daemon)
    ├── assets/                 # Recursos gráficos y multimedia 
    └── README.md


## 👥 Equipo de desarrollo

| Rol | Integrante | Funciones principales |
|-----|------------|----------------------|
| 🧭 Scrum Master | Nicolás Ramírez | Gestión ágil del equipo y coordinación de tareas |
| 🧩 Product Owner | Álvaro López | Definición del backlog y prioridades del producto |
| 💻 Desarrollador IoT | Fernando Fernández | Integración de sensores, actuadores y pruebas en ESP32 |
| 🧪 QA / Documentación | Daniel Vicente | Validación, testing, documentación técnica y control de calidad |

---

## 🧱 Licencia

Proyecto académico desarrollado en el marco del Grado en Ingeniería Informática (Universidad Europea de Madrid).

El código puede reutilizarse citando la fuente original y manteniendo esta licencia.
