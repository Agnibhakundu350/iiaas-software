"""Simple anomaly checks on recent readings. Teammate B owns this file."""
STUCK_S = 600    # identical readings for this many seconds = sensor may be stuck
STUCK_MIN_N = 20  # ...and at least this many readings in that time
JUMP = 25        # a change this big between two readings (in % points) = sudden jump
LIMITS = {"soil_moisture": (0, 100), "humidity": (0, 100)}  # pH range is already checked in main.py
NAMES = {"soil_moisture": "soil moisture", "humidity": "humidity", "air_temp": "air temperature",
         "soil_temp": "soil temperature", "ph": "pH"}


def check(node, rows):
    """rows: readings of ONE node, oldest first (what history() returns). Gives insight-style dicts."""
    out = []
    add = lambda level, msg: out.append({"level": level, "msg": msg})
    for field, name in NAMES.items():
        pts = [(r["ts"], r[field]) for r in rows if r.get(field) is not None]
        if not pts:
            continue
        ts, last = pts[-1]
        lim = LIMITS.get(field)
        if lim and not lim[0] <= last <= lim[1]:
            add("bad", f"Node {node}: {name} reading {last:.0f} is out of range. Check the sensor.")
            continue
        recent = [v for t, v in pts if t >= ts - STUCK_S]
        if pts[0][0] <= ts - STUCK_S and len(recent) >= STUCK_MIN_N and len(set(recent)) == 1:
            add("warn", f"Node {node}: {name} has not changed for 10 minutes. The sensor may be stuck.")
        if field in ("soil_moisture", "humidity") and len(pts) >= 2 and abs(last - pts[-2][1]) > JUMP:
            add("warn", f"Node {node}: {name} jumped by {abs(last - pts[-2][1]):.0f} points. Check the sensor.")
    return out