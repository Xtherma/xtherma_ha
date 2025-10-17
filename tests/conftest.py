import os
import sys
from unittest.mock import AsyncMock, Mock, patch
import pytest

from tests.helpers import load_mock_data

VENDOR_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "custom_components",
    "xtherma_fp",
    "vendor",
    "pymodbus",
)
print(os.path.abspath(VENDOR_DIR))
sys.path.insert(0, os.path.abspath(VENDOR_DIR))

from homeassistant.const import CONF_API_KEY, CONF_HOST, CONF_PORT, CONF_ADDRESS
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
)

from custom_components.xtherma_fp.const import (
    CONF_CONNECTION,
    CONF_CONNECTION_MODBUSTCP,
    CONF_CONNECTION_RESTAPI,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    FERNPORTAL_URL,
    VERSION,
)
from tests.const import (
    MOCK_API_KEY,
    MOCK_CONFIG_ENTRY_ID,
    MOCK_MODBUS_ADDRESS,
    MOCK_MODBUS_HOST,
    MOCK_MODBUS_PORT,
    MOCK_SERIAL_NUMBER,
)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    return


@pytest.fixture
async def init_integration(hass, aioclient_mock) -> MockConfigEntry:
    """Integration using REST API."""
    mock_data = load_mock_data("rest_response.json")
    url = f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}"
    aioclient_mock.get(url, json=mock_data)

    # Create a mock config entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
            CONF_API_KEY: MOCK_API_KEY,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
        },
        entry_id=MOCK_CONFIG_ENTRY_ID,
        version=VERSION,
        title="test_entry_xtherma_config",
        source="user",
    )
    entry.add_to_hass(hass)

    # Call async_setup_entry()
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return entry


MODBUS_CLIENT_PATH = (
    "custom_components.xtherma_fp.xtherma_client_modbus.AsyncModbusTcpClient"
)


@pytest.fixture
async def mock_modbus_tcp_client(request):
    """Stub out Modbus calls."""
    with patch(MODBUS_CLIENT_PATH) as MockModbusClient:
        # Configure the mock instance that will be returned when AsyncModbusTcpClient() is called.
        # This `mock_client_instance` represents the actual client object created by your component.
        mock_instance = MockModbusClient.return_value

        mock_connected_property = Mock(return_value=False)
        type(mock_instance).connected = property(lambda self: mock_connected_property())

        # When `connect` is called, it should change the `connected` property to True,
        # and return True which will be the return value of connect()
        async def connect_side_effect():
            mock_connected_property.return_value = True
            return True

        mock_instance.connect = AsyncMock(side_effect=connect_side_effect)

        # Mock the `read_holding_registers` method.
        mock_results_queue = []
        for registers_for_this_call in request.param:
            mock_read_holding_registers_result = AsyncMock()
            mock_read_holding_registers_result.registers = registers_for_this_call
            mock_read_holding_registers_result.isError = Mock(return_value=False)
            mock_read_holding_registers_result.exception_code = 0
            mock_results_queue.append(mock_read_holding_registers_result)
        mock_instance.read_holding_registers = AsyncMock(side_effect=mock_results_queue)

        # When `close` is called, it should change the `connected` property back to False.
        def close_side_effect():
            mock_connected_property.return_value = False

        # Mock the `write_registers` method
        mock_write_register_result = AsyncMock()
        mock_write_register_result.isError = Mock(return_value=False)
        mock_write_register_result.exception_code = 0
        mock_instance.write_register = AsyncMock(
            return_value=mock_write_register_result
        )

        # Mock the `close` method, as it might be called during component teardown or error handling.
        mock_instance.close = Mock(side_effect=close_side_effect)

        yield mock_instance


@pytest.fixture
async def init_modbus_integration(hass, mock_modbus_tcp_client) -> MockConfigEntry:
    """Integration using Modbus."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_CONNECTION: CONF_CONNECTION_MODBUSTCP,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
            CONF_HOST: MOCK_MODBUS_HOST,
            CONF_PORT: MOCK_MODBUS_PORT,
            CONF_ADDRESS: MOCK_MODBUS_ADDRESS,
        },
        entry_id=MOCK_CONFIG_ENTRY_ID,
        version=VERSION,
        title="test_entry_xtherma_modbus_config",
        source="user",
    )
    entry.add_to_hass(hass)

    # Call async_setup_entry()
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return entry
