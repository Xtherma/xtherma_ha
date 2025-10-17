"""Tests for the Xtherma select platform."""

import pytest
from homeassistant.components.select import (
    SelectEntity,
)
from homeassistant.exceptions import HomeAssistantError

from tests.helpers import get_select_platform, load_modbus_regs_from_json

SELECT_ENTITY_ID_002 = "select.test_entry_xtherma_config_operating_mode"
SELECT_ENTITY_ID_MODBUS_002 = "select.test_entry_xtherma_modbus_config_operating_mode"


async def test_select_entity(hass, init_integration):
    platform = get_select_platform(hass)
    state = hass.states.get(SELECT_ENTITY_ID_002)
    assert state.state == "auto"
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.icon == "mdi:brightness-auto"


async def test_set_select_rest(hass, init_integration):
    platform = get_select_platform(hass)
    state = hass.states.get(SELECT_ENTITY_ID_002)
    assert state.state == "auto"
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, SelectEntity)
    # init_integration uses REST-API, which cannot write
    with pytest.raises(HomeAssistantError):
        await entity.async_select_option(entity.options[0])


def _modbus_data_from_json():
    regs_list = load_modbus_regs_from_json("rest_response.json")
    return [regs_list]


@pytest.mark.parametrize(
    "mock_modbus_tcp_client",  # This refers to the fixture
    _modbus_data_from_json(),
    indirect=True,  # This tells pytest to pass the parameter to the fixture
)
async def test_set_select_modbus(hass, init_modbus_integration, mock_modbus_tcp_client):
    platform = get_select_platform(hass)
    state = hass.states.get(SELECT_ENTITY_ID_MODBUS_002)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, SelectEntity)
    await entity.async_select_option(entity.options[0])
    kwargs = mock_modbus_tcp_client.write_register.call_args.kwargs
    # verify arguments passed to write_register()
    assert kwargs["address"] == 1
    assert kwargs["value"] == 0
    assert kwargs["slave"] == 1
