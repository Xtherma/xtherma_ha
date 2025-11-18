"""Tests for the Xtherma select platform."""

from unittest.mock import patch

import pytest
from homeassistant.components.select import DOMAIN
from homeassistant.components.select.const import SERVICE_SELECT_OPTION
from homeassistant.const import ATTR_ENTITY_ID, ATTR_OPTION, Platform
from homeassistant.exceptions import HomeAssistantError
from pytest_homeassistant_custom_component.common import snapshot_platform

from custom_components.xtherma_fp.pymodbus_compat import (
    COMPAT_DEVICE_ID,
)
from custom_components.xtherma_fp.xtherma_client_common import XthermaReadOnlyError
from tests.helpers import provide_modbus_data, provide_rest_data

from .conftest import init_integration, init_modbus_integration

SELECT_ENTITY_ID_002 = "select.test_entry_xtherma_config_operating_mode"
SELECT_ENTITY_ID_MODBUS_002 = "select.test_entry_xtherma_modbus_config_operating_mode"


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_setup_select_rest_api(
    hass, entity_registry, snapshot, mock_rest_api_client
) -> None:
    """Test the setup of select platform using REST API."""
    with patch("custom_components.xtherma_fp._PLATFORMS", [Platform.SELECT]):
        entry = await init_integration(hass, mock_rest_api_client)

    await snapshot_platform(hass, entity_registry, snapshot, entry.entry_id)


@pytest.mark.parametrize("mock_modbus_tcp_client", provide_modbus_data(), indirect=True)
async def test_setup_select_modbus_tcp(
    hass, entity_registry, snapshot, mock_modbus_tcp_client
) -> None:
    """Test the setup of select platform using MODBUS TCP."""
    with patch("custom_components.xtherma_fp._PLATFORMS", [Platform.SELECT]):
        entry = await init_modbus_integration(hass, mock_modbus_tcp_client)

    await snapshot_platform(hass, entity_registry, snapshot, entry.entry_id)


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_set_select_rest_error(hass, mock_rest_api_client):
    await init_integration(hass, mock_rest_api_client)

    with pytest.raises(HomeAssistantError) as exc_info:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SELECT_OPTION,
            {
                ATTR_ENTITY_ID: SELECT_ENTITY_ID_002,
                ATTR_OPTION: "standby",
            },
            blocking=True,
        )
    assert isinstance(exc_info.value.__cause__, XthermaReadOnlyError)


@pytest.mark.parametrize("mock_modbus_tcp_client", provide_modbus_data(), indirect=True)
async def test_set_select_modbus(hass, mock_modbus_tcp_client):
    await init_modbus_integration(hass, mock_modbus_tcp_client)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_SELECT_OPTION,
        {
            ATTR_ENTITY_ID: SELECT_ENTITY_ID_MODBUS_002,
            ATTR_OPTION: "standby",
        },
        blocking=True,
    )

    kwargs = mock_modbus_tcp_client.write_register.call_args.kwargs
    # verify arguments passed to write_register()
    assert kwargs["address"] == 1
    assert kwargs["value"] == 0
    assert kwargs[COMPAT_DEVICE_ID] == 1
