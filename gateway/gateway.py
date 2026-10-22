"""MQTT -> Azure IoT Hub gateway (runs on the Raspberry Pi next to Mosquitto).

Subscribes to iot25/+/telemetry, keeps the latest reading per ESP32 and sends each one to
IoT Hub every SEND_EVERY seconds as {"deviceId","value","unit"} (the format the group's OPC UA
server reads). Also prints every MQTT message, so it doubles as the local consumer.

Env: IOTHUB_DEVICE_CONNECTION_STRING (required), MQTT_HOST, MQTT_USER, MQTT_PASS, SEND_EVERY (default 45)
"""
import json
import os
import threading
import time

import paho.mqtt.client as mqtt
from azure.iot.device import IoTHubDeviceClient, Message

CONN = os.environ["IOTHUB_DEVICE_CONNECTION_STRING"]
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
TOPIC = "iot25/+/telemetry"
# free IoT Hub = 8,000 msgs/day; 2 boards x (temp + humidity) every 45 s = 7,680/day
SEND_EVERY = float(os.getenv("SEND_EVERY", "45"))

latest = {}            # deviceId -> {"deviceId","value","unit"}
lock = threading.Lock()


def on_message(client, userdata, msg):
    try:
        d = json.loads(msg.payload)
        reading = {"deviceId": str(d["deviceId"]), "value": float(d["value"]), "unit": str(d.get("unit", ""))}
    except (ValueError, KeyError, TypeError):
        print("ignored bad payload on", msg.topic, msg.payload[:120], flush=True)
        return
    print(f"MQTT  {msg.topic}  {reading}", flush=True)
    with lock:
        latest[reading["deviceId"]] = reading


def on_connect(client, userdata, flags, rc):  # paho 1.x API (azure-iot-device pins paho<2)
    if rc != 0:
        print("MQTT refused, code", rc, flush=True)
        return
    print("MQTT connected, subscribing to", TOPIC, flush=True)
    client.subscribe(TOPIC)


m = mqtt.Client(client_id="mhmood-gateway")
if os.getenv("MQTT_USER"):
    m.username_pw_set(os.getenv("MQTT_USER"), os.getenv("MQTT_PASS"))
m.on_connect, m.on_message = on_connect, on_message
m.connect_async(MQTT_HOST, 1883, keepalive=30)
m.loop_start()

hub = IoTHubDeviceClient.create_from_connection_string(CONN, websockets=True)  # port 443, passes firewalls
hub.connect()
print(f"Azure IoT Hub connected, sending every {SEND_EVERY:g} s", flush=True)

while True:
    time.sleep(SEND_EVERY)
    with lock:
        batch = list(latest.values())
        latest.clear()          # only send fresh readings
    for reading in batch:
        msg = Message(json.dumps(reading))
        msg.content_type, msg.content_encoding = "application/json", "utf-8"
        try:
            hub.send_message(msg)
            print(f"AZURE sent {reading}", flush=True)
        except Exception as e:  # keep running if the internet drops
            print("AZURE send failed:", e, flush=True)
