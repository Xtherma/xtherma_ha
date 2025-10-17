import pytest
from homeassistant.components.number import (
    NumberEntity,
)
from homeassistant.exceptions import HomeAssistantError

from tests.helpers import get_number_platform, load_rest_response

NUMBER_ENTITY_ID_451 = (
    "number.test_entry_xtherma_config_cooling_curve_2_outside_temperature_low_p1"
)
NUMBER_ENTITY_ID_MODBUS_451 = (
    "number.test_entry_xtherma_modbus_config_cooling_curve_2_outside_temperature_low_p1"
)
NUMBER_ENTITY_ID_MODBUS_411 = (
    "number.test_entry_xtherma_modbus_config_heating_curve_2_outside_temperature_low_p1"
)


async def test_number_icon(hass, init_integration):
    platform = get_number_platform(hass)
    entity = platform.entities.get(NUMBER_ENTITY_ID_451)
    assert entity is not None
    assert entity.icon == "mdi:thermometer"


async def test_set_number_rest(hass, init_integration):
    platform = get_number_platform(hass)
    state = hass.states.get(NUMBER_ENTITY_ID_451)
    assert state.state == "33.0"
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, NumberEntity)
    # init_integration uses REST-API, which cannot write
    with pytest.raises(HomeAssistantError):
        await entity.async_set_native_value(entity.native_min_value)


@pytest.mark.parametrize(
    "mock_modbus_tcp_client",  # This refers to the fixture
    load_rest_response(),
    indirect=True,  # This tells pytest to pass the parameter to the fixture
)
# check writing positive values
async def test_set_number_modbus(hass, init_modbus_integration, mock_modbus_tcp_client):
    platform = get_number_platform(hass)
    state = hass.states.get(NUMBER_ENTITY_ID_MODBUS_451)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, NumberEntity)
    await entity.async_set_native_value(entity.native_min_value)
    kwargs = mock_modbus_tcp_client.write_register.call_args.kwargs
    # verify arguments passed to write_register()
    assert kwargs["address"] == 41
    assert entity.native_min_value == 16
    assert kwargs["value"] == entity.native_min_value
    assert kwargs["slave"] == 1


# check writing negative values as 2s complement
@pytest.mark.parametrize(
    "mock_modbus_tcp_client",  # This refers to the fixture
    load_rest_response(),
    indirect=True,  # This tells pytest to pass the parameter to the fixture
)
async def test_set_negative_number_modbus(
    hass, init_modbus_integration, mock_modbus_tcp_client
):
    platform = get_number_platform(hass)
    state = hass.states.get(NUMBER_ENTITY_ID_MODBUS_411)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, NumberEntity)
    await entity.async_set_native_value(entity.native_min_value)
    kwargs = mock_modbus_tcp_client.write_register.call_args.kwargs
    # verify arguments passed to write_register()
    assert kwargs["address"] == 31
    assert entity.native_min_value == -20
    assert kwargs["value"] == (20 ^ 65535) + 1
    assert kwargs["slave"] == 1
