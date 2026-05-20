#include <WiFi.h>
#include <WebServer.h>
#include <DHT.h>
#include <ArduinoJson.h>

// --- (SIMULACIÓN DE TU LIBRERÍA BIORDINARIO) ---
// Asumimos que estas funciones existen en la librería que vayas a importar
void inicializarSensor(int rx, int tx);
bool comprobarDatosDisponibles();
// En C++ no se puede devolver un array de tipos mixtos directamente.
// Usaremos una estructura para representar el retorno de "leerSensor()".
struct DatosBiordinario {
  int num;
  char alfa[50];
};
DatosBiordinario leerSensorBiordinario(); // Supuesta función que lee el sensor

// --- CONFIGURACIÓN WIFI ---
const char* ssid = "PC LOFRA";
const char* password = "12345678";
WebServer server(80);

// --- MAPEO DE PINES ---
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);
#define LDR_PIN 32
#define MQ2_PIN 33
#define BIO_RX_PIN 16 // Pin RX para el sensor Biordinario
#define BIO_TX_PIN 17 // Pin TX para el sensor Biordinario

// Salidas (Actuadores)
#define FAN_PIN 12
#define LEDS_PIN 13
#define DOOR1_PIN 14
#define DOOR2_PIN 15

// --- VARIABLES GLOBALES DEL SENSOR BIORDINARIO ---
int global_bio_num = 0;
String global_bio_alfa = "Sin datos";

// --- FUNCIÓN SOLICITADA ---
// Almacena los datos generados para que Python los inserte en la BBDD
void DataBaseInsert(int valorNumerico, const char* valorAlfanumerico) {
  global_bio_num = valorNumerico;
  global_bio_alfa = String(valorAlfanumerico);
  Serial.println("Datos biordinarios listos para inserción en BBDD.");
}

void setup() {
  Serial.begin(115200);

  // Inicializar Sensores
  dht.begin();
  inicializarSensor(BIO_RX_PIN, BIO_TX_PIN); // Inicialización del nuevo sensor

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
  Serial.println(WiFi.localIP());

  // --- RUTA 1: PYTHON PIDE DATOS DE SENSORES ---
  server.on("/sensores", HTTP_GET, []() {
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();
    int raw_luz = analogRead(LDR_PIN);
    int raw_gas = analogRead(MQ2_PIN);

    int luz_lux = map(raw_luz, 0, 4095, 0, 1000);
    if (luz_lux < 0) luz_lux = 0;

    int gas_ppm = map(raw_gas, 0, 4095, 0, 1000);
    if (gas_ppm < 0) gas_ppm = 0;

    // Creamos un JSON ampliado
    StaticJsonDocument<300> doc;
    doc["temperatura"] = isnan(temp) ? 0 : temp;
    doc["humedad"] = isnan(hum) ? 0 : hum;
    doc["luz"] = luz_lux;
    doc["mq2"] = gas_ppm;

    // Inyectamos los datos del sensor biordinario
    doc["bio_num"] = global_bio_num;
    doc["bio_alfa"] = global_bio_alfa;

    String respuesta;
    serializeJson(doc, respuesta);
    server.send(200, "application/json", respuesta);
  });

  // --- RUTA 2: PYTHON ENVÍA ÓRDENES ---
  server.on("/actuadores", HTTP_GET, []() {
    String dispositivo = server.arg("dispositivo");
    String estado = server.arg("estado");

    int pinDestino = -1;
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

  // Lectura continua del sensor ordinario
  if (comprobarDatosDisponibles()) {
    DatosBiordinario nuevosDatos = leerSensorBiordinario();
    DataBaseInsert(nuevosDatos.num, nuevosDatos.alfa);
  }
}