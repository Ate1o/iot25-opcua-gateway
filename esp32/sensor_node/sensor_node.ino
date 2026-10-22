// ESP32 sensor node: reads a DHT11 and publishes temperature and humidity as JSON over MQTT.
// Topic: iot25/<deviceId>/telemetry   Payload: {"deviceId","sensor","value","unit"}
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include "secrets.h"   // copy secrets.example.h to secrets.h and fill in

#define DHT_PIN D4      // Arduino Nano ESP32 pin D4
#define DHT_TYPE DHT11

DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient net;
PubSubClient mqtt(net);
unsigned long lastSend = 0;

void connectWifi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("WiFi");
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.printf("\nIP: %s\n", WiFi.localIP().toString().c_str());
}

void connectMqtt() {
  while (!mqtt.connected()) {
    Serial.print("MQTT...");
    if (mqtt.connect(DEVICE_ID, MQTT_USER, MQTT_PASS)) Serial.println("connected");
    else { Serial.printf("failed rc=%d, retry in 3 s\n", mqtt.state()); delay(3000); }
  }
}

void publishReading(const char* id, const char* sensor, float value, const char* unit) {
  char topic[96], payload[192];
  snprintf(topic, sizeof(topic), "iot25/%s/telemetry", id);
  snprintf(payload, sizeof(payload),
           "{\"deviceId\":\"%s\",\"sensor\":\"%s\",\"value\":%.2f,\"unit\":\"%s\"}", id, sensor, value, unit);
  mqtt.publish(topic, payload);
  Serial.printf("%s %s\n", topic, payload);
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  connectWifi();
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) connectWifi();
  if (!mqtt.connected()) connectMqtt();
  mqtt.loop();

  if (millis() - lastSend < 5000) return;
  lastSend = millis();

  float t = dht.readTemperature();
  float h = dht.readHumidity();
  if (isnan(t) || isnan(h)) { Serial.println("DHT read failed"); return; }

  publishReading(DEVICE_ID, "temperature", t, "°C");
  // humidity gets its own deviceId: the gateway keeps one latest value per deviceId
  char humId[64];
  snprintf(humId, sizeof(humId), "%s-humidity", DEVICE_ID);
  publishReading(humId, "humidity", h, "%");
}
