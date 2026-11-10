"""Runs on the Raspberry Pi. Reads LoRa P2P packets from the Wio-E5 Dev Kit (USB serial)
and forwards each JSON packet to the API. Unsent packets are kept in unsent.jsonl."""
import argparse, binascii, json, re, time, urllib.request
import serial

ap = argparse.ArgumentParser()
ap.add_argument("--port", default="/dev/ttyACM0")
ap.add_argument("--baud", type=int, default=9600)
ap.add_argument("--url", default="http://localhost:8000/api/ingest")
ap.add_argument("--init", action="store_true", help="send the receive-mode AT commands first")
a = ap.parse_args()
# Frequency / SF / BW must match the transmitter (hub + Wio-E5 Mini). To be confirmed with the hardware team.
INIT = ["AT", "AT+MODE=TEST", "AT+TEST=RFCFG,866,SF7,125,12,15,14,ON,OFF,OFF", "AT+TEST=RXLRPKT"]


def post(p):
    try:
        req = urllib.request.Request(a.url, json.dumps(p).encode(), {"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print("post failed, saved:", e)
        open("unsent.jsonl", "a").write(json.dumps(p) + "\n")


rssi = None
with serial.Serial(a.port, a.baud, timeout=1) as s:
    if a.init:
        for c in INIT:
            s.write((c + "\r\n").encode()); time.sleep(0.5)
    while True:
        line = s.readline().decode(errors="ignore").strip()
        if not line:
            continue
        print(line)
        m = re.search(r"RSSI:(-?\d+)", line)
        if m:
            rssi = float(m.group(1))
        m = re.search(r'RX "([0-9A-Fa-f]+)"', line)
        if m:
            try:
                p = json.loads(binascii.unhexlify(m.group(1)).decode())
            except Exception as e:
                print("skipped (not JSON):", e); continue
            p["rssi"] = rssi
            post(p)
