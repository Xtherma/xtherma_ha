"""Test config flow."""

from homeassistant.config_entries import (
    ConfigEntryState,
)
from homeassistant.const import CONF_ADDRESS, CONF_API_KEY, CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResultType

from custom_components.xtherma_fp.const import (
    CONF_CONNECTION,
    CONF_CONNECTION_MODBUSTCP,
    CONF_CONNECTION_RESTAPI,
)
from tests.const import (
    MOCK_API_KEY,
    MOCK_MODBUS_ADDRESS,
    MOCK_MODBUS_HOST,
    MOCK_MODBUS_PORT,
)


async def test_options_flow_rest_api_ok(hass, init_integration):
    """Test options flow."""
    entry = init_integration
    assert entry.state is ConfigEntryState.LOADED

    result = await hass.config_entries.options.async_init(
        entry.entry_id,
        context={"source": "test"},
        data=None,
    )
    assert result["type"] == FlowResultType.FORM

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_CONNECTION: CONF_CONNECTION_RESTAPI},
    )

    assert result["type"] == FlowResultType.FORM

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_API_KEY: MOCK_API_KEY},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_options_flow_rest_api_change_to_modbus(hass, init_integration):
    """Test options flow."""
    entry = init_integration
    assert entry.state is ConfigEntryState.LOADED

    result = await hass.config_entries.options.async_init(
        entry.entry_id,
        context={"source": "test"},
        data=None,
    )
    assert result["type"] == FlowResultType.FORM

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_CONNECTION: CONF_CONNECTION_MODBUSTCP},
    )

    assert result["type"] == FlowResultType.FORM

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_HOST: MOCK_MODBUS_HOST,
            CONF_PORT: MOCK_MODBUS_PORT,
            CONF_ADDRESS: MOCK_MODBUS_ADDRESS,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
