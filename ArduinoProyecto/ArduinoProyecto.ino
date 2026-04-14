#include <WiFi.h>
#include <WebServer.h>
#include <DHT.h>
#include <ArduinoJson.h>

// --- CONFIGURACIÓN WIFI ---
const char* ssid = "TU_NOMBRE_DE_WIFI";
const char* password = "TU_CONTRASENA_WIFI";

WebServer server(80); // Servidor en el puerto 80 para datos

// --- MAPEO DE PINES (Ajustar según tu cableado) ---
// Entradas (Sensores)
#define DHTPIN 4      // Pin digital para el DHT22
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

#define LDR_PIN 32    // Pin analógico para LDR (Luz)
#define MQ2_PIN 33    // Pin analógico para MQ-2 (Humo/Aire)

// Salidas (Actuadores)
#define FAN_PIN 12    // Pin digital para Ventilador 5V (Usar relé o transistor)
#define LEDS_PIN 13   // Pin digital para los 5 LEDs (En paralelo)
#define DOOR1_PIN 14  // Pin digital para Motor DC Puerta 1 (Vía Driver L298N)
#define DOOR2_PIN 15  // Pin digital para Motor DC Puerta 2 

void setup() {
  Serial.begin(115200);
  
  // Inicializar Sensores
  dht.begin();
  
  // Inicializar Pines de Actuadores
  pinMode(FAN_PIN, OUTPUT);
  pinMode(LEDS_PIN, OUTPUT);
  pinMode(DOOR1_PIN, OUTPUT);
  pinMode(DOOR2_PIN, OUTPUT);
  
  // Conectar a Wi-Fi
  Serial.print("Conectando a WiFi..");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Conectado!");
  Serial.print("Dirección IP del ESP32: ");
  Serial.println(WiFi.localIP());

  // --- RUTA 1: PYTHON PIDE DATOS DE SENSORES ---
  server.on("/sensores", HTTP_GET, []() {
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();
    int luz = analogRead(LDR_PIN);
    int gas = analogRead(MQ2_PIN);

    // Creamos un JSON con la librería ArduinoJson
    StaticJsonDocument<200> doc;
    doc["temperatura"] = isnan(temp) ? 0 : temp;
    doc["humedad"] = isnan(hum) ? 0 : hum;
    doc["luz"] = luz;
    doc["mq2"] = gas;

    String respuesta;
    serializeJson(doc, respuesta);
    server.send(200, "application/json", respuesta);
  });

  // --- RUTA 2: PYTHON ENVÍA ÓRDENES A ACTUADORES ---
  server.on("/actuadores", HTTP_GET, []() {
    String dispositivo = server.arg("dispositivo");
    String estado = server.arg("estado");
    
    int pinDestino = -1;
    
    // Identificar a qué componente se refiere Python
    if(dispositivo == "fan") pinDestino = FAN_PIN;
    else if(dispositivo == "leds") pinDestino = LEDS_PIN;
    else if(dispositivo == "door-1") pinDestino = DOOR1_PIN;
    else if(dispositivo == "door-2") pinDestino = DOOR2_PIN;

    if(pinDestino != -1) {
      // Si la orden es "on" o "abierta", encendemos. Si no, apagamos.
      bool encender = (estado == "on" || estado == "abierta");
      digitalWrite(pinDestino, encender ? HIGH : LOW);
      server.send(200, "application/json", "{\"status\":\"ok\"}");
    } else {
      server.send(400, "application/json", "{\"status\":\"error\", \"msg\":\"Dispositivo no encontrado\"}");
    }
  });

  server.begin();
}

void loop() {
  server.handleClient(); // Mantener el servidor escuchando
}