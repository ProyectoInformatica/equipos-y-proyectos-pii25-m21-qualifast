#include <WiFi.h>
#include <WebServer.h>
#include <DHT.h>
#include <ArduinoJson.h>

// --- CONFIGURACIÓN WIFI ---
const char* ssid = "PC LOFRA";
const char* password = "12345678";

WebServer server(80); // Servidor en el puerto 80 para datos

// --- MAPEO DE PINES ---
#define DHTPIN 4      // Pin digital para el DHT11
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

#define LDR_PIN 32    // Pin analógico para LDR (Luz)
#define MQ2_PIN 33    // Pin analógico para MQ-2 (Humo/Aire)

// Salidas (Actuadores)
#define FAN_PIN 12    // Pin digital para Ventilador 5V (Usar relé o transistor)
#define LEDS_PIN 13   // Pin digital para los LEDs
#define DOOR1_PIN 14  // Pin digital para Motor DC Puerta 1
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

  // Todo apagado por defecto
  digitalWrite(FAN_PIN, LOW);
  digitalWrite(LEDS_PIN, LOW);
  digitalWrite(DOOR1_PIN, LOW);
  digitalWrite(DOOR2_PIN, LOW);
  
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
    int raw_luz = analogRead(LDR_PIN);
    int raw_gas = analogRead(MQ2_PIN);

    // Mapeo a valores reales y humanos
    // Luz: De voltaje (0-4095) a Lux simulados (0-1000).
    int luz_lux = map(raw_luz, 0, 4095, 0, 1000);
    if (luz_lux < 0) luz_lux = 0;

    // Humo: De voltaje (0-4095) a ppm (0-1000)
    int gas_ppm = map(raw_gas, 0, 4095, 0, 1000);
    if (gas_ppm < 0) gas_ppm = 0;

    // Creamos un JSON
    StaticJsonDocument<200> doc;
    doc["temperatura"] = isnan(temp) ? 0 : temp;
    doc["humedad"] = isnan(hum) ? 0 : hum;
    doc["luz"] = luz_lux;
    doc["mq2"] = gas_ppm;

    String respuesta;
    serializeJson(doc, respuesta);
    server.send(200, "application/json", respuesta);
  });

  // --- RUTA 2: PYTHON ENVÍA ÓRDENES A ACTUADORES ---
  server.on("/actuadores", HTTP_GET, []() {
    String dispositivo = server.arg("dispositivo");
    String estado = server.arg("estado");
    
    int pinDestino = -1;
    
    // Identificar componente
    if(dispositivo == "fan") pinDestino = FAN_PIN;
    else if(dispositivo == "leds") pinDestino = LEDS_PIN;
    else if(dispositivo == "door-1") pinDestino = DOOR1_PIN;
    else if(dispositivo == "door-2") pinDestino = DOOR2_PIN;

    if(pinDestino != -1) {
      bool encender = (estado == "on" || estado == "abierta");
      digitalWrite(pinDestino, encender ? HIGH : LOW);
      server.send(200, "application/json", "{\"status\":\"ok\"}");
    } else {
      server.send(400, "application/json", "{\"status\":\"error\"}");
    }
  });

  server.begin();
}

void loop() {
  server.handleClient();
}