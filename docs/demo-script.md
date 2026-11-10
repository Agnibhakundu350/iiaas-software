# IIAAS Field Monitor — Demo Script

**Version:** 1.0
**Duration:** ~10–15 minutes
**Audience:** Supervisors, stakeholders, hardware team

---

## Prerequisites

Before starting the demo, complete these steps on the demo machine:

```bash
cd iiaas-software-main
pip install -r requirements.txt
```

Open two terminal windows.

---

## Step 1 — Start the Server (Terminal 1)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Say:** "IIAAS runs entirely on a Raspberry Pi — no cloud, no subscription. This command starts the server in one line."

---

## Step 2 — Start the Simulator (Terminal 2)

```bash
python tools/simulator.py --every 2
```

**Say:** "While we're waiting for the hardware team to finalise the LoRa settings, we use this simulator to generate realistic sensor readings. The dashboard clearly labels simulated data."

Open `http://localhost:8000` in a browser.

**Point out:**
- 🟡 **"Simulated data"** badge in the top bar — the system is honest about data source.
- The green field-condition cards populating with values.
- Both Node 1 and Node 2 show "Updated X s ago" in green.

---

## Step 3 — Walk Through the Field Conditions Cards

**Say:** "The top row shows real-time conditions measured by the two sensor nodes."

Point to each section:

1. **Air Conditions (Node 1):** Temperature, humidity, CO₂ estimate, soil moisture, water tank level, MQ-135 gas reading.
   - *"All values come from on-field sensors. There's no external weather API — this is ground truth."*

2. **Soil Chemistry (Node 2):** pH, NPK levels, soil temperature.
   - *"NPK thresholds are currently placeholders — we need the hardware team to confirm sensor units before we can give fertilizer advice."*

3. **Irrigation Card:** Shows pump relay state (On/Off).

---

## Step 4 — Show the Recommendations Panel

**Say:** "Below the cards is the rule engine. It evaluates the latest readings every 5 seconds and gives actionable guidance."

If soil moisture drops below 40% (the simulator eventually triggers this):
- 🚨 "Node 1: soil moisture XX% is below 40%. Irrigate." appears.

**Say:** "These rules match the firmware threshold already programmed into Node 1."

---

## Step 5 — Demonstrate the Active Alert Banner and Sound

Wait for a "bad" or "warn" insight to appear (soil moisture usually drops within 2–3 minutes of simulator start, since `m1` starts at 58 and drifts downward).

**Show:**
- The red **alert banner** at the top of the page.
- *"The banner plays a chime the first time it fires, but not on every refresh — so it won't annoy you every 5 seconds."*
- Click **🔔 Mute** — *"You can silence the audio while keeping the visual banner."*
- Click **✕ Dismiss** — *"Or dismiss the banner entirely. It comes back only if a new, different alert appears."*

---

## Step 6 — Chart with Time Filters

**Say:** "The chart shows soil moisture history for both nodes."

Click the time filter buttons:
- **1 Hour** — zooms in on the last hour of simulated readings.
- **24 Hours** — wider view (default).
- **All** — shows all readings since the database was created.

**Point out:** The red dashed line at 40% — the irrigation threshold that also triggers recommendations.

---

## Step 7 — Pump ON/OFF History

**Say:** "The pump relay state is recorded with every reading. We automatically detect state transitions to build an event log."

Scroll down to **Pump ON/OFF History**.

- Shows timestamps when the pump switched on and off.
- Shows soil moisture at the moment of switching.
- **OFF events** show how long the pump ran (duration in minutes/seconds).

*"This is built entirely from the existing relay field in the database — no new hardware or sensors needed."*

---

## Step 8 — Alerts Tab

Click **🔔 Alerts** in the navigation.

**Show:**
- **Active** filter: unacknowledged alerts from the last 30 minutes.
- Click **Dismiss** on one alert row.
  - Row fades out. *"This writes to the database — it won't reappear as 'active' next time."*
- **All** filter: complete history with timestamps, node numbers, and delivery channel (log / email / telegram).

**Say:** "In production, the alert worker sends these to Telegram or email. During this demo it's logging only."

---

## Step 9 — PWA Installation (mobile)

(Show on a phone, or use Chrome DevTools mobile emulation.)

1. Open `http://<pi-ip>:8000` in Chrome on Android.
2. Tap ⋮ menu → **Add to Home screen → Install**.
3. Open the installed app.

**Say:** "Field workers can install this on their phone with one tap. It works offline for the cached shell and live when connected to the field Wi-Fi."

---

## Step 10 — Data Export

Scroll to the bottom of the dashboard. Click **⬇ Download CSV**.

**Say:** "All readings can be exported as CSV for analysis in Excel or any data tool."

---

## Step 11 — API Overview (for technical audience)

Open a new browser tab and show:

| URL | Description |
|-----|-------------|
| `http://localhost:8000/api/latest` | JSON: most recent reading per node |
| `http://localhost:8000/api/insights` | JSON: current recommendations |
| `http://localhost:8000/api/history?node=1&hours=1` | JSON: last hour of Node 1 data |
| `http://localhost:8000/api/pump-events` | JSON: pump state-transition log |
| `http://localhost:8000/api/alerts?active=1` | JSON: unacknowledged active alerts |

**Say:** "Every piece of data the dashboard shows is available as a JSON API. The hub poller, LoRa receiver, and alert worker all use the same API."

---

## Demo Conclusion

**Key points to leave the audience with:**

1. **Fully offline** — works without internet, runs on a Pi.
2. **Dual hardware path** — existing ESP32 hub works today; LoRa path is ready when the hardware team confirms the radio settings.
3. **No invented data** — the dashboard shows only what sensors report; thresholds match the firmware.
4. **Installable PWA** — field workers use it like a native app.
5. **Alert system** — automatic detection, dashboard banner, audio alert, Telegram/email notification, and a full dismissal workflow.

---

## Features That Require Real Hardware or External Config

The following features cannot be fully demonstrated with the simulator:

| Feature | Requirement |
|---------|-------------|
| LoRa packet reception | Wio-E5 Dev Kit + confirmed radio settings from hardware team |
| Telegram/email alerts | `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`, or `GMAIL_*` environment variables |
| Actual NPK readings | Confirmed sensor units and calibration |
| Actual pH readings | Sensor calibration confirmation |
| Real pump relay events | Physical pump wired to Node 1 relay |
