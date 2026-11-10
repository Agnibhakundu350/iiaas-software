import pytest
from app.main import normalize
from app.anomaly import check


# ---- packet parsing (normalize) ----
def test_hub_format_node1():
    node, seq, d = normalize({"node": "ESP32_1", "temperature": 30.5, "humidity": 60,
                              "soil_percent": 42, "relay": True})
    assert node == 1 and d["air_temp"] == 30.5 and d["soil_moisture"] == 42 and d["relay"] is True


def test_hub_format_node2():
    node, seq, d = normalize({"node": "ESP32_2", "temperature": 27, "moisture": 38, "ph": 6.5,
                              "nitrogen": 120, "phosphorus": 45, "potassium": 160, "count": 7})
    assert node == 2 and seq == 7 and d["ph"] == 6.5 and d["n"] == 120 and d["soil_temp"] == 27


def test_compact_lora_format():
    node, seq, d = normalize({"id": 1, "seq": 105, "temp": 29.5, "hum": 68, "soil": 42})
    assert node == 1 and seq == 105 and d["humidity"] == 68 and d["soil_moisture"] == 42
    node, seq, d = normalize({"id": 2, "seq": 106, "soil": 38, "soil_temp": 27.2,
                              "ph": 6.5, "n": 120, "p": 45, "k": 160})
    assert node == 2 and d["soil_temp"] == 27.2 and d["k"] == 160


def test_unknown_node_rejected():
    with pytest.raises(ValueError):
        normalize({"id": 9, "temp": 30})


def test_bad_values_become_none():
    _, _, d = normalize({"node": "ESP32_1", "temperature": "nan", "humidity": "abc", "soil_percent": 40})
    assert d["air_temp"] is None and d["humidity"] is None and d["soil_moisture"] == 40


# ---- anomaly checks ----
def rows(vals, step=30, field="soil_moisture"):
    return [{"ts": 1000 + i * step, field: v} for i, v in enumerate(vals)]


def msgs(node, r):
    return [i["msg"] for i in check(node, r)]


def test_normal_readings_ok():
    assert msgs(1, rows([50, 51, 50, 52, 51] * 8)) == []


def test_stuck_sensor_found():
    assert any("stuck" in m for m in msgs(1, rows([55] * 30)))  # 30 identical readings over 14 minutes


def test_few_identical_readings_not_stuck():
    assert msgs(1, rows([55] * 5)) == []


def test_sudden_jump_found():
    assert any("jumped" in m for m in msgs(1, rows([50, 51, 88])))


def test_small_change_not_a_jump():
    assert msgs(1, rows([50, 60])) == []


def test_out_of_range_found():
    assert any("out of range" in m for m in msgs(1, rows([50, 140])))