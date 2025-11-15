"""Tests for the Xtherma sensor platform."""

from unittest.mock import patch

import pytest
from homeassistant.const import Platform
from pytest_homeassistant_custom_component.common import snapshot_platform

from tests.conftest import MockModbusParam
from tests.helpers import provide_modbus_data, provide_rest_data, set_modbus_register

from .conftest import init_integration, init_modbus_integration

SENSOR_ENTITY_ID_MODBUS_TA = (
    "sensor.test_entry_xtherma_modbus_config_ta_outdoor_temperature"
)

SENSOR_ENTITY_ID_MODBUS_OUT_HP = (
    "sensor.test_entry_xtherma_modbus_config_heat_output_heat_pump_thermal"
)

SENSOR_ENTITY_ID_MODBUS_DAY_HP_OUT_H = (
    "sensor.test_entry_xtherma_modbus_config_daily_heating_operation_thermal_output"
)

SENSOR_ENTITY_ID_MODBUS_LD1 = "sensor.test_entry_xtherma_modbus_config_ld1_fan_1_speed"

SENSOR_ENTITY_ID_MODBUS_V = "sensor.test_entry_xtherma_modbus_config_v_volume_flow"

SENSOR_ENTITY_ID_MODBUS_VF = (
    "sensor.test_entry_xtherma_modbus_config_compressor_frequency"
)


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_setup_sensor_rest_api(
    hass, entity_registry, snapshot, mock_rest_api_client
) -> None:
    """Test the setup of sensor platform using REST API."""
    with patch("custom_components.xtherma_fp._PLATFORMS", [Platform.SENSOR]):
        entry = await init_integration(hass, mock_rest_api_client)

    await snapshot_platform(hass, entity_registry, snapshot, entry.entry_id)


@pytest.mark.parametrize("mock_modbus_tcp_client", provide_modbus_data(), indirect=True)
async def test_setup_sensor_modbus_tcp(
    hass, entity_registry, snapshot, mock_modbus_tcp_client
) -> None:
    """Test the setup of sensor platform using MODBUS TCP."""
    with patch("custom_components.xtherma_fp._PLATFORMS", [Platform.SENSOR]):
        entry = await init_modbus_integration(hass, mock_modbus_tcp_client)

    await snapshot_platform(hass, entity_registry, snapshot, entry.entry_id)


def _test_get_negative_number_modbus_regs() -> list[MockModbusParam]:
    def twos_complement(value: int) -> int:
        if value < 0:
            value = (-value ^ 65535) + 1
        return value

    param = provide_modbus_data()

    # try covering several types of values

    # temperature
    set_modbus_register(param[0], "ta", twos_complement(-20 * 10))

    # power
    set_modbus_register(param[0], "out_hp", twos_complement(-600 // 10))

    # energy
    set_modbus_register(param[0], "day_hp_out_h", twos_complement(-5000 * 100))

    # frequency
    set_modbus_register(param[0], "vf", twos_complement(-15))

    # ventilator speed
    set_modbus_register(param[0], "ld1", twos_complement(-10))

    # volume flow rate
    set_modbus_register(param[0], "v", twos_complement(-110 * 10))

    return param


@pytest.mark.parametrize(
    "mock_modbus_tcp_client", _test_get_negative_number_modbus_regs(), indirect=True
)
# check reading negative values from 2s complement
async def test_get_negative_number_modbus(hass, mock_modbus_tcp_client):
    await init_modbus_integration(hass, mock_modbus_tcp_client)

    state = hass.states.get(SENSOR_ENTITY_ID_MODBUS_TA)
    assert state.state == "-20.0"

    state = hass.states.get(SENSOR_ENTITY_ID_MODBUS_OUT_HP)
    assert state.state == "-600.0"

    state = hass.states.get(SENSOR_ENTITY_ID_MODBUS_DAY_HP_OUT_H)
    assert state.state == "-5000.0"

    state = hass.states.get(SENSOR_ENTITY_ID_MODBUS_LD1)
    assert state.state == "-10.0"

    state = hass.states.get(SENSOR_ENTITY_ID_MODBUS_V)
    assert state.state == "-110.0"

    state = hass.states.get(SENSOR_ENTITY_ID_MODBUS_VF)
    assert state.state == "-15.0"
