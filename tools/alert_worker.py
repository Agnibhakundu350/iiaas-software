"""Free alerts. Watches /api/insights and sends ONE Telegram message when a problem starts.
Run it next to the server:  python tools/alert_worker.py

Environment variables (never put these in the code or the repo):
  TELEGRAM_TOKEN, TELEGRAM_CHAT_ID   leave unset to only log alerts (shown at /api/alerts)
  ALERT_COOLDOWN_S (default 1800)    same problem is not sent again within this time
  ALERT_EVERY_S    (default 20)      how often to check
  IIAAS_API        (default http://localhost:8000)
"""
import json, os, re, sqlite3, sys, time, urllib.parse, urllib.request
from pathlib import Path
import smtplib, ssl
from email.message import EmailMessage

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.alerts import DB, ensure

API = os.getenv("IIAAS_API", "http://localhost:8000")
COOLDOWN = int(os.getenv("ALERT_COOLDOWN_S", 1800))
EVERY = int(os.getenv("ALERT_EVERY_S", 20))
TOKEN, CHAT = os.getenv("TELEGRAM_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
ALERT_TO = os.getenv("ALERT_TO") or GMAIL_USER


def send_email(text):
    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = "IIAAS alert", GMAIL_USER, ALERT_TO
    msg.set_content(text)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context(), timeout=20) as s:
        s.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        s.send_message(msg)

def send(text):
    if GMAIL_USER and GMAIL_APP_PASSWORD:
        try:
            send_email(text)
            return "email"
        except Exception as e:
            print("email failed:", type(e).__name__)
    if TOKEN and CHAT:
        try:
            data = urllib.parse.urlencode({"chat_id": CHAT, "text": text}).encode()
            urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data, timeout=10)
            return "telegram"
        except Exception as e:
            print("telegram failed:", type(e).__name__)  # not the full error: it can contain the token
    return "failed" if (GMAIL_USER and GMAIL_APP_PASSWORD) or (TOKEN and CHAT) else "log"


def log(item, channel):
    m = re.match(r"Node (\d)", item["msg"])
    with sqlite3.connect(DB) as c:
        ensure(c)
        c.execute("INSERT INTO alerts(ts,node,level,msg,channel,sent) VALUES(?,?,?,?,?,?)",
                  (time.time(), int(m.group(1)) if m else None, item["level"], item["msg"], channel,
                   int(channel in ("email", "telegram"))))


active, last_sent = set(), {}
print("alert worker running; Telegram", "ON" if TOKEN and CHAT else "OFF (log only)")
while True:
    try:
        items = json.load(urllib.request.urlopen(API + "/api/insights", timeout=5))
        now, keys = time.time(), set()
        for i in items:
            if i["level"] not in ("bad", "warn") or "no data yet" in i["msg"]:
                continue
            key = re.sub(r"[\d.]+", "#", i["msg"])  # same problem with changing numbers = one key
            keys.add(key)
            if key not in active and now - last_sent.get(key, 0) >= COOLDOWN:
                channel = send("IIAAS alert: " + i["msg"])
                log(i, channel)
                last_sent[key] = now
                print(channel, "-", i["msg"])
        active = keys  # a problem that goes away can alert again later (after the cooldown)
    except Exception as e:
        print("check failed:", type(e).__name__)
    time.sleep(EVERY)
