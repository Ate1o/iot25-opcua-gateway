// ESP32 sensor node: reads a DHT sensor and publishes JSON over MQTT.
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include "secrets.h"   // copy secrets.example.h to secrets.h and fill in

#define DHT_PIN 4
#define DHT_TYPE DHT11

DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient net;
PubSubClient mqtt(net);
unsigned long lastSend = 0;

void setup() {
  Serial.begin(115200);
  dht.begin();

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println(WiFi.localIP());

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
}

void loop() {
  if (!mqtt.connected()) {
    mqtt.connect(DEVICE_ID, MQTT_USER, MQTT_PASS);
    delay(1000);
    return;
  }
  mqtt.loop();

  if (millis() - lastSend < 5000) return;
  lastSend = millis();

  float t = dht.readTemperature();
  if (isnan(t)) return;

  char topic[64];
  snprintf(topic, sizeof(topic), "iot25/%s/telemetry", DEVICE_ID);
  char payload[128];
  snprintf(payload, sizeof(payload), "{\"deviceId\":\"%s\",\"value\":%.1f,\"unit\":\"C\"}", DEVICE_ID, t);
  mqtt.publish(topic, payload);
  Serial.println(payload);
}
