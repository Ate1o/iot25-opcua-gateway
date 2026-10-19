"""MQTT -> OPC UA gateway on the Raspberry Pi.

Subscribes to the device topic and keeps the latest value in an OPC UA node.
"""
import asyncio
import json
import os

from asyncua import Server
import paho.mqtt.client as mqtt

DEVICE_ID = os.getenv("DEVICE_ID", "esp32-01")
TOPIC = f"iot25/{DEVICE_ID}/telemetry"


async def main():
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/")
    ns = await server.register_namespace("urn:iot25:group:gateway")
    device = await server.nodes.objects.add_object(ns, DEVICE_ID)
    value = await device.add_variable(ns, "Value", 0.0)

    loop = asyncio.get_running_loop()

    def on_message(client, userdata, msg):
        data = json.loads(msg.payload)
        asyncio.run_coroutine_threadsafe(value.write_value(float(data["value"])), loop)
        print("value", data["value"])

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.connect(os.getenv("MQTT_HOST", "localhost"), 1883)
    client.subscribe(TOPIC)
    client.loop_start()

    # TODO: Unit, MeasuredAtUtc, Status nodes (agreed group structure)
    async with server:
        while True:
            await asyncio.sleep(1)


asyncio.run(main())
