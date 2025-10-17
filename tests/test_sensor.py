"""Tests for the Xtherma sensor platform."""

import pytest
from homeassistant.components.sensor import (
    SensorEntity,
)

from tests.helpers import get_sensor_platform, load_modbus_regs_from_json

SENSOR_ENTITY_ID_PK = "sensor.test_entry_xtherma_config_pk_circulation_pump_enabled"
SENSOR_ENTITY_ID_PWW = (
    "sensor.test_entry_xtherma_config_pww_circulation_pump_hot_water_enabled"
)
SENSOR_ENTITY_ID_MODE = "sensor.test_entry_xtherma_config_current_operating_mode"
SENSOR_ENTITY_ID_SG = "sensor.test_entry_xtherma_config_sg_ready_status"
SENSOR_ENTITY_ID_LD1 = "sensor.test_entry_xtherma_config_ld1_fan_1_speed"
SENSOR_ENTITY_ID_CONTROLLER_V = "sensor.test_entry_xtherma_config_controller_version"
SENSOR_ENTITY_ID_MODBUS_TA = (
    "sensor.test_entry_xtherma_modbus_config_ta_outdoor_temperature"
)


async def test_binary_sensor_state(hass, init_integration):
    pk = hass.states.get(SENSOR_ENTITY_ID_PK)
    assert pk.state == "off"
    pww = hass.states.get(SENSOR_ENTITY_ID_PWW)
    assert pww.state == "on"


async def test_binary_sensor_icon(hass, init_integration):
    platform = get_sensor_platform(hass)
    pk = hass.states.get(SENSOR_ENTITY_ID_PK)
    assert pk.state == "off"
    e_pk = platform.entities.get(pk.entity_id)
    assert e_pk is not None
    assert e_pk.icon == "mdi:pump-off"
    pww = hass.states.get(SENSOR_ENTITY_ID_PWW)
    assert pww.state == "on"
    e_pww = platform.entities.get(pww.entity_id)
    assert e_pww is not None
    assert e_pww.icon == "mdi:pump"


async def test_opmode_sensor_icon(hass, init_integration):
    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_MODE)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.icon == "mdi:thermometer-water"


async def test_sgready_sensor_icon(hass, init_integration):
    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_SG)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.icon == "mdi:cancel"


async def test_sensor_name(hass, init_integration):
    """Check if regular sensors have proper (translated) names."""
    await hass.config.async_load()
    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_LD1)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.name == "[LD1] Fan 1 speed"


async def test_binary_sensor_name(hass, init_integration):
    """Check if binary sensors have a proper (translated) names."""
    await hass.config.async_load()
    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_PWW)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.name == "[PWW] Circulation pump hot water enabled"


async def test_enum_sensor_name(hass, init_integration):
    """Check if enum sensors have a proper (translated) names."""
    await hass.config.async_load()
    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_MODE)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.name == "Current operating mode"


async def test_version_sensor(hass, init_integration):
    """Check if enum sensors have a proper (translated) names."""
    await hass.config.async_load()
    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_CONTROLLER_V)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.state == "2.39"


def load_and_prep_rest_response():
    regs_list = load_modbus_regs_from_json("rest_response.json")
    # change "ta" register #140 to be -20 °C in 2s complement
    regs_list[11][0] = ((20 * 10) ^ 65535) + 1
    return [regs_list]


@pytest.mark.parametrize(
    "mock_modbus_tcp_client",  # This refers to the fixture
    load_and_prep_rest_response(),
    indirect=True,  # This tells pytest to pass the parameter to the fixture
)
# check reading negative values from 2s complement
async def test_get_negative_number_modbus(
    hass, init_modbus_integration, mock_modbus_tcp_client
):
    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_MODBUS_TA)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, SensorEntity)
    assert state.state == "-20.0"
