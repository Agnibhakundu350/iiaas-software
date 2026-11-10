"""Integration test for pump_events logic (no pytest required, runs with plain python)."""
import sys, json, time, sqlite3, tempfile, pathlib, os
sys.path.insert(0,'.')

import app.main as M
import app.alerts as AL

tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
tmp.close()
tmppath = pathlib.Path(tmp.name)
M.DB = tmppath
AL.DB = tmppath

# Create table and insert a relay sequence
c = M.db()
c.execute('DELETE FROM readings')
readings = [
    (time.time()-300, 1, 1, None, 'sim', json.dumps({'air_temp':30,'humidity':60,'soil_moisture':55,'water_raw':2000,'mq135_raw':700,'eco2_ppm':450,'relay':False})),
    (time.time()-240, 1, 2, None, 'sim', json.dumps({'air_temp':30,'humidity':60,'soil_moisture':45,'water_raw':2000,'mq135_raw':700,'eco2_ppm':450,'relay':False})),
    (time.time()-180, 1, 3, None, 'sim', json.dumps({'air_temp':30,'humidity':60,'soil_moisture':38,'water_raw':2000,'mq135_raw':700,'eco2_ppm':450,'relay':True})),
    (time.time()-120, 1, 4, None, 'sim', json.dumps({'air_temp':30,'humidity':60,'soil_moisture':40,'water_raw':2000,'mq135_raw':700,'eco2_ppm':450,'relay':True})),
    (time.time()-60,  1, 5, None, 'sim', json.dumps({'air_temp':30,'humidity':60,'soil_moisture':55,'water_raw':2000,'mq135_raw':700,'eco2_ppm':450,'relay':False})),
]
for r in readings:
    c.execute('INSERT INTO readings(ts,node,seq,rssi,source,data) VALUES(?,?,?,?,?,?)', r)
c.commit()

events = M.pump_events(limit=50)
print('Pump events:', json.dumps(events, indent=2))

assert len(events) == 2, 'Expected 2 events (1 ON + 1 OFF), got ' + str(len(events))
most_recent = events[0]
assert most_recent['event'] == 'off', 'Most recent should be OFF, got ' + most_recent['event']
assert most_recent['duration_s'] is not None, 'OFF event should have duration'
print()
print('PASS: pump event detection found', len(events), 'events')
print('PASS: OFF event duration =', events[0]['duration_s'], 's (expected ~120s)')

# Test /api/history with hours filter
M.DB = tmppath
c2 = M.db()
# History for all
all_rows = M.history(node=1, limit=100)
assert len(all_rows) == 5, 'Expected 5 rows, got ' + str(len(all_rows))
print('PASS: history returns all 5 rows')

# History with hours=0.01 (last 36 seconds) - should get only the last reading
recent = M.history(node=1, limit=100, hours=0.01)
assert len(recent) <= 2, 'Expected <=2 recent rows, got ' + str(len(recent))
print('PASS: history time filter works, got', len(recent), 'row(s) in last 36s')

try:
    os.unlink(tmp.name)
except PermissionError:
    pass  # SQLite may hold a brief lock on Windows; file will be cleaned up at process exit
print()
print('All integration tests PASSED')
