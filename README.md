# IIAAS software v1

Runs on the Raspberry Pi (or any laptop). Works offline, no cloud account needed.

## Run
```
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000                  # server + dashboard -> http://<pi-ip>:8000
python tools/simulator.py                                         # FAKE data, development only
python receiver/hub_poller.py --hub http://<hub-ip>               # REAL data from the existing ESP32 hub (ESP-NOW prototype)
python receiver/serial_receiver.py --port /dev/ttyACM0 --init     # REAL data from the Wio-E5 Dev Kit (LoRa, future)
```
Use only ONE data source at a time (simulator, hub poller or serial receiver). The dashboard shows "Simulated data" when fake readings are present.

## Packets the server accepts (POST /api/ingest)
1. Existing hub JSON
   `{"node":"ESP32_1","temperature":..,"humidity":..,"soil_percent":..,"water_level_raw":..,"mq135_raw":..,"eco2_ppm":..,"relay":..}`
   `{"node":"ESP32_2","temperature":..,"moisture":..,"ph":..,"nitrogen":..,"phosphorus":..,"potassium":..}`
2. Compact LoRa JSON
   `{"id":1,"seq":105,"temp":..,"hum":..,"soil":..,"water":..,"mq135":..}`
   `{"id":2,"seq":106,"soil":..,"soil_temp":..,"ph":..,"n":..,"p":..,"k":..}`

Missing fields are stored as empty. Extra keys are ignored.

## Other endpoints
GET /api/latest, /api/insights, /api/history?node=1&limit=100, /api/export.csv

## Still to confirm with the hardware team
- LoRa settings (frequency, SF, bandwidth) in receiver/serial_receiver.py must match the transmitter.
- Final packet keys and units (especially N, P, K). Fertilizer limits in app/main.py (CFG) are placeholders.
- The Dev Kit's USB port and baud rate (default /dev/ttyACM0, 9600).

## Hub poller notes
- The hub prints its IP in the Serial Monitor at start-up. The computer running this must be on the same Wi-Fi.
- It reads the hub's /api/status and /api/data, sends only new readings, and rebuilds each reading's real time from the hub's uptime clock.
- It works with the original hub code. If the revised hub code changed these endpoints, send us the new code.
