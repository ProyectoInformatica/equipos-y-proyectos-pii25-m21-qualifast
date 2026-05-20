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
#define FAN_PIN 12    // Pin digital para Ventilador 5V
#define LEDS_PIN 13   // Pin digital para los LEDs
#define DOOR1_PIN 14  // Pin digital para Motor DC Puerta 1
#define DOOR2_PIN 15  // Pin digital para Motor DC Puerta 2
#define RX_PIN 16
#define TX_PIN 17

void inicializarSensor(int pin_rx, int pin_tx) {}

int* leerDatosOrdinarios() {
  static int d[2] = {42, 'A'};
  return d;
}
 
void databaseInsert(float temp, float hum, int luz, int gas, int sx_num, char sx_char) {
  StaticJsonDocument<300> doc;
  doc["temperatura"] = isnan(temp) ? 0 : temp;
  doc["humedad"] = isnan(hum) ? 0 : hum;
  doc["luz"] = luz;
  doc["mq2"] = gas;
  doc["sensorx_num"] = sx_num;
  doc["sensorx_char"] = String(sx_char);

  String respuesta;
  serializeJson(doc, respuesta);
  server.send(200, "application/json", respuesta);
}

void setup() {
  Serial.begin(115200);
  dht.begin();

  // Inicializar Pines de Actuadores
  pinMode(FAN_PIN, OUTPUT);
  pinMode(LEDS_PIN, OUTPUT);
  pinMode(DOOR1_PIN, OUTPUT);
  pinMode(DOOR2_PIN, OUTPUT);

  inicializarSensor(RX_PIN, TX_PIN); // Llamada obligatoria

  // Conexión WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConectado! IP: " + WiFi.localIP().toString());

  // --- RUTA 1: PYTHON PIDE LOS DATOS ---
  server.on("/sensores", HTTP_GET, []() {
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();

    int raw_luz = analogRead(LDR_PIN);
    int raw_gas = analogRead(MQ2_PIN);

    int luz_lux = map(raw_luz, 0, 4095, 0, 1000);
    if (luz_lux < 0) luz_lux = 0;

    int gas_ppm = map(raw_gas, 0, 4095, 0, 1000);
    if (gas_ppm < 0) gas_ppm = 0;

    // Inyección directa del sensor de la prueba en 3 líneas limpias
    int* sx = leerDatosOrdinarios();
    databaseInsert(temp, hum, luz_lux, gas_ppm, sx[0], (char)sx[1]);
  });

  // --- RUTA 2: PYTHON ENVÍA ÓRDENES A ACTUADORES ---
  server.on("/actuadores", HTTP_GET, []() {
    String dispositivo = server.arg("dispositivo");
    String estado = server.arg("estado");

    if (dispositivo == "leds") {
      digitalWrite(LEDS_PIN, estado == "on" ? HIGH : LOW);
    } else if (dispositivo == "fan") {
      digitalWrite(FAN_PIN, estado == "on" ? HIGH : LOW);
    } else if (dispositivo == "door-1") {
      digitalWrite(DOOR1_PIN, estado == "on" ? HIGH : LOW);
    } else if (dispositivo == "door-2") {
      digitalWrite(DOOR2_PIN, estado == "on" ? HIGH : LOW);
    }

    server.send(200, "text/plain", "OK");
  });

  server.begin();
}

void loop() {
  server.handleClient();
}