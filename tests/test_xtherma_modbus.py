import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from tests.const import (
    MOCK_CONFIG_ENTRY_ID,
)
from tests.helpers import load_modbus_regs_from_json
from tests.test_xtherma_fp import (
    verify_integration_entry,
    verify_integration_numbers,
    verify_integration_selects,
    verify_integration_sensors,
    verify_integration_switches,
    verify_parameter_keys,
)


def _get_config_entry(hass: HomeAssistant) -> ConfigEntry:
    entry = hass.config_entries.async_get_entry(MOCK_CONFIG_ENTRY_ID)
    assert isinstance(entry, ConfigEntry)
    return entry


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
@pytest.mark.asyncio
async def test_async_setup_entry_modbus_ok(hass, init_modbus_integration):
    # Verify setup worked
    entry = _get_config_entry(hass)

    verify_integration_entry(entry)

    verify_integration_sensors(hass, entry)

    verify_integration_switches(hass, entry)

    verify_integration_numbers(hass, entry)

    verify_integration_selects(hass, entry)

    verify_parameter_keys(hass, entry)
