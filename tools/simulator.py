"""Sends FAKE readings (source=sim) in the existing hub JSON format, so the software can be built and demoed
before real data arrives. Remove once the hardware team sends real data."""
import argparse, json, random, time, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("--url", default="http://localhost:8000/api/ingest")
ap.add_argument("--count", type=int, default=0, help="0 = run forever")
ap.add_argument("--every", type=float, default=5)
a = ap.parse_args()


def post(p):
    req = urllib.request.Request(a.url, json.dumps(p).encode(), {"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=5)


m1, m2, i = 58.0, 52.0, 0
while a.count == 0 or i < a.count:
    i += 1
    m1 += random.uniform(-3, 1); m2 += random.uniform(-2, 1)
    if m1 < 33: m1 = 70
    if m2 < 30: m2 = 65
    post(dict(node="ESP32_1", temperature=round(random.uniform(28, 33), 1), humidity=round(random.uniform(55, 75)),
              soil_percent=int(m1), water_level_raw=random.randint(1500, 2500), mq135_raw=random.randint(600, 900),
              eco2_ppm=random.randint(420, 650), relay=m1 < 40, source="sim"))
    post(dict(node="ESP32_2", temperature=round(random.uniform(25, 29), 1), moisture=round(m2, 1),
              ph=round(6.4 + random.uniform(-.3, .3), 1), nitrogen=random.randint(30, 90),
              phosphorus=random.randint(10, 40), potassium=random.randint(80, 160), count=i * 5, source="sim"))
    time.sleep(a.every)
