<!-- Banner o logo del proyecto -->
<p align="center">
  <img src="assets/logo_qualifast.png" alt="Qualifast Buildings Logo" width="180" />
</p>

<h1 align="center">🏢 Qualifast Buildings – Estación de Policía Inteligente</h1>
<p align="center">
  <em>Proyecto IoT para la gestión automatizada y sostenible de una comisaría</em><br>
  <strong>Universidad Europea de Madrid – Grado en Ingeniería Informática</strong>
</p>

<p align="center">
  <!-- Badges -->
  <img src="https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white" alt="Python Badge"/>
  <img src="https://img.shields.io/badge/Flet-Framework-orange?logo=flet" alt="Flet Badge"/>
  <img src="https://img.shields.io/badge/Scrum-Agile_Methodology-green?logo=trello" alt="Scrum Badge"/>
  <img src="https://img.shields.io/badge/IDE-PyCharm-green?logo=jetbrains" alt="PyCharm Badge"/>
  <img src="https://img.shields.io/github/license/alvarolopez/qualifast-buildings?color=lightgrey" alt="License Badge"/>
</p>

---

## 🧭 Descripción del proyecto

**Qualifast Buildings** desarrolla una solución **IoT** para optimizar la gestión de una **comisaría de policía inteligente**, integrando sensores y actuadores en una única plataforma.

El sistema permite **monitorizar condiciones ambientales**, controlar iluminación, ventilación y accesos, y recibir alertas automáticas ante incidencias.  
Cada usuario accede a una **interfaz personalizada según su rol** (administrador, jefe o agente), visualizando datos en tiempo real desde cualquier dispositivo.

> 🎯 **Objetivo:** Mejorar la seguridad, eficiencia y sostenibilidad en instalaciones policiales mediante tecnologías IoT y control centralizado.

---

## 🧠 Tecnologías principales

| Tipo | Tecnología |
|------|-------------|
| 💻 Lógica de sistema | Python 3 |
| 🎨 Interfaz gráfica | Flet |
| ⚙️ Hardware IoT | ESP32, sensores DHT22, MQ-2, MQ-135, LDR |
| 💾 Datos | JSON (estructura portable y escalable) |
| 🧩 Arquitectura | Modelo-Vista-Controlador (MVC) |
| 📋 Gestión ágil | Scrum + Trello |
| 🧠 IDE principal | PyCharm |
| 🌐 Control de versiones | GitHub |

---

## 📂 Estructura del repositorio

```plaintext
📦 qualifast-buildings/
├── src/ # Código fuente principal
├── assets/ # Imágenes, iconos, logotipos
├── docs/ # Documentación técnica y mockups
├── tests/ # Scripts y pruebas unitarias
├── requirements.txt # Dependencias del proyecto
├── .gitignore
└── README.md

---

## ⚙️ Instalación y ejecución

```bash
# 1️⃣ Clonar el repositorio
git clone https://github.com/alvarolofra/qualifast-buildings.git
cd qualifast-buildings

# 2️⃣ Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3️⃣ Instalar dependencias
pip install -r requirements.txt

# 4️⃣ Ejecutar el programa
python main.py
```

---

## 🧩 Flujo de trabajo con Git

### 🌿 Convención para ramas
Cada rama nueva debe seguir el formato:

```
feature/issueX_Y_[usuario]_[descripcion_corta]
```

Ejemplos:

```
feature/issue2_Y_Daniel_sensor_humo
feature/issue5_Y_Alvaro_UI_login
```

📘 Donde:

- issueX_Y → número y subnúmero de la historia de usuario en Trello
- [usuario] → nombre o alias del desarrollador
- [descripcion_corta] → resumen breve de la tarea

### 🔁 Pull Requests

- Los PR deben mantener el nombre de la tarea en Trello.  
  Ejemplo: HU3-2: Implementar interfaz para control de sensores

- Añadir una breve descripción de los cambios

- Indicar si requiere pruebas de hardware o integración

- Solicitar revisión al Scrum Master antes de fusionar

---

## 👥 Equipo de desarrollo

| Rol | Integrante | Funciones principales |
|-----|------------|-----------------------|
| 🧭 Scrum Master | Nicolás Ramírez | Gestión ágil del equipo y coordinación de tareas |
| 🧩 Product Owner | Álvaro López | Definición del backlog y prioridades del producto |
| 💻 Desarrollador IoT | Fernando Fernández | Integración de sensores, actuadores y pruebas en ESP32 |
| 🧪 QA / Documentación | Daniel Vicente | Validación, testing, documentación y control de calidad |

---

## 📋 Metodología de trabajo

- Enfoque: Ágil – Scrum Framework
- Sprints: de 2 semanas
- Herramientas: Trello + GitHub + Visual Studio Code
- Revisiones: al final de cada sprint con demo funcional
- Documentación: actualizada en /docs y actas de reunión

📅 Los avances del proyecto pueden consultarse en el tablero Trello: [enlace al tablero]

---

## 🚀 Objetivos del sistema

- 🌡️ Integrar sensores ambientales (temperatura, humo, luz, calidad del aire)
- 💡 Controlar actuadores (luces, ventiladores, motores) desde la interfaz
- 👥 Ofrecer vistas personalizadas según el rol del usuario
- 🔔 Generar alertas automáticas ante valores críticos
- 💾 Usar JSON para garantizar portabilidad y escalabilidad
- 🧱 Aplicar arquitectura MVC para un desarrollo modular y mantenible

---

## 📊 Planificación (resumen de sprints)

| Sprint | Enfoque | Entregables |
|--------|---------|-------------|
| Sprint 1 | Diseño y prototipado | Interfaz inicial + login adaptable |
| Sprint 2 | Integración base IoT | Sensores y gestión de usuarios |
| Sprint 3 | Actuadores y responsividad | Control remoto + UI adaptable |
| Sprint 4 | Integración final y testing | Panel de control + alertas + documentación |

---

## 🧱 Licencia
Proyecto académico desarrollado en el marco del Grado en Ingeniería Informática (UEM).  
El código puede reutilizarse citando la fuente original y manteniendo esta licencia.

<p align="center">
  <img src="https://img.shields.io/badge/Licencia-Académica-lightgrey" alt="Licencia Badge"/>
</p>

---

## 📫 Contacto
📧 Equipo Qualifast Buildings:  
Álvaro López • Nicolás Ramírez • Daniel Vicente • Fernando Fernández

🏫 Universidad Europea de Madrid  
🌐 Página del proyecto (mockup) https://qualifastbuildings.neocities.org/

💬 Repositorio en GitHub

<p align="center">
  <sub>✨ Proyecto desarrollado con esfuerzo, coordinación y mucha cafeína ☕</sub>
</p>
````
