# IOT25 group project – MQTT telemetry via OPC UA

```
ESP32 -> Mosquitto (Raspberry Pi) -> gateway / OPC UA server -> web app + desktop app
```

## Parts
| Folder | What |
|---|---|
| `esp32/sensor_node` | ESP32 sketch, publishes to `iot25/<deviceId>/telemetry` |
| `gateway` | Python gateway: MQTT in, OPC UA server out (port 4840) |

## Run the gateway
```
pip install asyncua paho-mqtt
DEVICE_ID=esp32-01 python3 gateway/gateway.py
```
Test with UaExpert: `opc.tcp://<pi-ip>:4840`

## Status
- [x] ESP32 -> MQTT
- [x] OPC UA server with a `Value` node
- [ ] Full node structure (DeviceId, Unit, MeasuredAtUtc, Status)
- [ ] Run as a service on the Pi
- [ ] Web app
