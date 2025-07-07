from pytest_homeassistant_custom_component.common import load_json_value_fixture

def test_json_load_value_fixture():
    data = load_json_value_fixture("rest_response.json")
    assert isinstance(data, dict)
    assert len(data) == 3
    assert data.get("serial_number") == "FP-04-123456"
    settings = data.get("settings")
    assert isinstance(settings, list)
    assert len(settings) == 29
    telemetry = data.get("telemetry")
    assert isinstance(telemetry, list)
    assert len(telemetry) == 53
    t0 = telemetry[0]
    assert isinstance(t0, dict)
    assert t0.get("key") == "tvl"
    assert t0.get("input_factor") == "/10"
    tLast = telemetry[52]
    assert isinstance(tLast, dict)
    assert tLast.get("key") == "mode_3"
    assert tLast.get("value") == "3"
