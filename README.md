# IOT25 group project – MQTT telemetry via OPC UA

My part of the group solution: ESP32 sensor node, Raspberry Pi gateway, and the web app.

```
ESP32 + DHT11 > Mosquitto (Raspberry Pi) > gateway > Azure IoT Hub
   > group OPC UA server + REST API (https://github.com/Filip-Mat/LocalOpcUaServer) > web app / desktop app
```

## Parts
| Folder | What |
|---|---|
| `esp32/sensor_node` | ESP32 sketch: DHT11 temperature + humidity > MQTT (`iot25/<deviceId>/telemetry`) |
| `gateway` | Python gateway on the Pi: MQTT in, Azure IoT Hub out, in the group's format `{"deviceId","value","unit"}` |
| `web` | Web app: `index.html`, served by the group REST API from its `web/` folder |

## Web app
- Reads `/api/devices` every 3 seconds and shows one card per device (value, unit, time since update).
- Status per device: online, stale, offline.
- Works with camelCase and PascalCase field names.
- `index.html?api=mock` shows test data without a backend.

To run it with the group API: copy `web/index.html` into the API repo's `web/` folder, start `azure_opcua_server.py` and `rest_api.py`, then open http://127.0.0.1:8000.

## Status
- [x] ESP32 publishes temperature and humidity (tested with a real DHT11)
- [x] Gateway on the Pi forwards to Azure IoT Hub (systemd service)
- [x] Web app shows live devices from the group API (tested end to end: Pi > Azure > OPC UA server > REST API > web page)

## Update notes
- **2026-10-22:** Gateway now goes through Azure IoT Hub, matching the group's OPC UA server. First working version of the web app added in `web/`.
- **Possible next steps for the web app:** one card per ESP32 (temperature and humidity together), a history chart per device, mobile layout.
