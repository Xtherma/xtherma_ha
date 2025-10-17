from homeassistant.components.switch import (
    SwitchEntity,
)
import pytest

from custom_components.xtherma_fp.xtherma_client_common import XthermaReadOnlyError
from tests.helpers import get_switch_platform, load_modbus_regs_from_json
from homeassistant.exceptions import HomeAssistantError

SWITCH_ENTITY_ID_450 = "switch.test_entry_xtherma_config_cooling_curve_2_active"
SWITCH_ENTITY_ID_MODBUS_450 = (
    "switch.test_entry_xtherma_modbus_config_cooling_curve_2_active"
)
SWITCH_ENTITY_ID_MODBUS_350 = (
    "switch.test_entry_xtherma_modbus_config_cooling_curve_1_active"
)


async def test_binary_switch_icon(hass, init_integration):
    platform = get_switch_platform(hass)
    entity = platform.entities.get(SWITCH_ENTITY_ID_450)
    assert entity is not None
    assert entity.icon == "mdi:snowflake"


async def test_set_switch_rest(hass, init_integration):
    platform = get_switch_platform(hass)
    state = hass.states.get(SWITCH_ENTITY_ID_450)
    assert state.state == "on"
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, SwitchEntity)
    # init_integration uses REST-API, which cannot write
    with pytest.raises(HomeAssistantError):
        await entity.async_turn_off()


def _modbus_data_from_json():
    regs_list = load_modbus_regs_from_json("rest_response.json")
    return [
        regs_list
        # ([...]),x
        # ([...]),
    ]


@pytest.mark.parametrize(
    "mock_modbus_tcp_client",  # This refers to the fixture
    _modbus_data_from_json(),
    indirect=True,  # This tells pytest to pass the parameter to the fixture
)
async def test_set_switch_modbus(hass, init_modbus_integration, mock_modbus_tcp_client):
    platform = get_switch_platform(hass)
    state = hass.states.get(SWITCH_ENTITY_ID_MODBUS_450)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, SwitchEntity)
    await entity.async_turn_off()
    kwargs = mock_modbus_tcp_client.write_register.call_args.kwargs
    # verify arguments passed to write_register()
    assert kwargs["address"] == 40
    assert kwargs["value"] == 0
    assert kwargs["slave"] == 1
    await entity.async_turn_on()


@pytest.mark.parametrize(
    "mock_modbus_tcp_client",  # This refers to the fixture
    _modbus_data_from_json(),
    indirect=True,  # This tells pytest to pass the parameter to the fixture
)
async def test_set_multiple_switches_modbus(
    hass, init_modbus_integration, mock_modbus_tcp_client
):
    platform = get_switch_platform(hass)
    state = hass.states.get(SWITCH_ENTITY_ID_MODBUS_450)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, SwitchEntity)
    await entity.async_turn_off()
    kwargs = mock_modbus_tcp_client.write_register.call_args.kwargs
    # verify arguments passed to write_register()
    assert kwargs["address"] == 40
    assert kwargs["value"] == 0
    assert kwargs["slave"] == 1
    await entity.async_turn_on()
    state = hass.states.get(SWITCH_ENTITY_ID_MODBUS_350)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, SwitchEntity)
    await entity.async_turn_off()
    kwargs = mock_modbus_tcp_client.write_register.call_args.kwargs
    # verify arguments passed to write_register()
    assert kwargs["address"] == 20
    assert kwargs["value"] == 0
    assert kwargs["slave"] == 1
    await entity.async_turn_on()
