"""Test config flow."""

import asyncio
import pytest
from unittest.mock import patch

from homeassistant.const import (
    CONF_NAME,
    CONF_API_KEY,
    CONF_HOST,
    CONF_PORT,
    CONF_ADDRESS,
)
from homeassistant.data_entry_flow import FlowResultType

from custom_components.xtherma_fp.const import (
    CONF_CONNECTION,
    CONF_CONNECTION_RESTAPI,
    CONF_SERIAL_NUMBER,
    FERNPORTAL_URL,
)
from tests.const import (
    MOCK_NAME,
    MOCK_API_KEY,
    MOCK_SERIAL_NUMBER,
    MOCK_MODBUS_HOST,
    MOCK_MODBUS_PORT,
    MOCK_MODBUS_ADDRESS,
)
from tests.helpers import load_mock_data

from custom_components.xtherma_fp.config_flow import (
    _validate_connection,
    _validate_rest_api,
    _validate_modbus_tcp,
)
from custom_components.xtherma_fp.xtherma_client_common import (
    XthermaBusyError,
    XthermaError,
    XthermaNotConnectedError,
    XthermaTimeoutError,
)


MOCK_REST_DATA = {CONF_NAME: MOCK_NAME, CONF_API_KEY: MOCK_API_KEY}

MOCK_MODBUS_DATA = {
    CONF_NAME: MOCK_NAME,
    CONF_HOST: MOCK_MODBUS_HOST,
    CONF_PORT: MOCK_MODBUS_PORT,
    CONF_ADDRESS: MOCK_MODBUS_ADDRESS,
}


async def test_config_common_bad_arguments(hass):
    """Test giving bad config dat to REST API config flow."""
    result = await hass.config_entries.flow.async_init(
        "xtherma_fp",
        context={"source": "user"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_NAME: MOCK_NAME,
            CONF_SERIAL_NUMBER: "SerialNumbersMustBeginWithFP",
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "bad_arguments"}


async def test_rest_api_good_serial_number(hass, aioclient_mock):
    """Test giving an valid data to REST API config flow."""
    mock_data = load_mock_data("rest_response.json")
    aioclient_mock.get(
        f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}",
        json=mock_data,
    )

    result = await hass.config_entries.flow.async_init(
        "xtherma_fp",
        context={"source": "user"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
            CONF_NAME: MOCK_NAME,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_API_KEY: MOCK_API_KEY},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_rest_error_404(hass, aioclient_mock):
    """Test forcing network errors to REST API config flow."""
    mock_data = load_mock_data("rest_response.json")
    aioclient_mock.get(
        f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}",
        json=mock_data,
        status=404,
    )

    result = await hass.config_entries.flow.async_init(
        "xtherma_fp",
        context={"source": "user"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
            CONF_NAME: MOCK_NAME,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_API_KEY: MOCK_API_KEY},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"
    assert result["errors"] == {"base": "unknown"}


async def test_rest_error_429(hass, aioclient_mock):
    """Test forcing network errors to REST API config flow."""
    mock_data = load_mock_data("rest_response.json")
    aioclient_mock.get(
        f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}",
        json=mock_data,
        status=429,
    )

    result = await hass.config_entries.flow.async_init(
        "xtherma_fp",
        context={"source": "user"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
            CONF_NAME: MOCK_NAME,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_API_KEY: MOCK_API_KEY},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"
    assert result["errors"] == {"base": "rate_limit"}


async def test_rest_error_timeout(hass, aioclient_mock):
    """Test forcing network errors to REST API config flow."""
    aioclient_mock.get(
        f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}",
        exc=asyncio.exceptions.TimeoutError,
    )

    result = await hass.config_entries.flow.async_init(
        "xtherma_fp",
        context={"source": "user"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
            CONF_NAME: MOCK_NAME,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_API_KEY: MOCK_API_KEY},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"
    assert result["errors"] == {"base": "timeout"}


@pytest.mark.parametrize(
    ["data", "expected_errors"],
    [
        ({CONF_SERIAL_NUMBER: "FP-04-123456"}, {}),
        (
            {CONF_SERIAL_NUMBER: "SerialNumbersMustBeginWithFP"},
            {"base": "bad_arguments"},
        ),
    ],
)
async def test_validate_connection(data, expected_errors):
    """Test for general connection validation."""
    assert await _validate_connection(data) == expected_errors


@pytest.mark.parametrize(
    ["data", "side_effect", "expected_errors"],
    [
        ({}, None, {"base": "bad_arguments"}),
        (MOCK_REST_DATA, XthermaBusyError, {"base": "rate_limit"}),
        (MOCK_REST_DATA, XthermaTimeoutError, {"base": "timeout"}),
        (MOCK_REST_DATA, XthermaError, {"base": "cannot_connect"}),
        (MOCK_REST_DATA, Exception, {"base": "unknown"}),
    ],
)
async def test_validate_rest_api(hass, data, side_effect, expected_errors):
    """Test for rest api connection validation."""
    with patch(
        "custom_components.xtherma_fp.xtherma_client_rest.XthermaClientRest.connect",
        side_effect=side_effect,
    ):
        previous_data = {CONF_SERIAL_NUMBER: "FP-04-123456"}
        assert await _validate_rest_api(hass, previous_data, data) == expected_errors


@pytest.mark.parametrize(
    ["data", "side_effect", "expected_errors"],
    [
        (MOCK_MODBUS_DATA | {CONF_HOST: None}, None, {"base": "bad_arguments"}),
        (MOCK_MODBUS_DATA | {CONF_PORT: None}, None, {"base": "bad_arguments"}),
        (MOCK_MODBUS_DATA | {CONF_ADDRESS: None}, None, {"base": "bad_arguments"}),
        (MOCK_MODBUS_DATA | {CONF_PORT: 502.1}, None, {"base": "bad_arguments"}),
        (MOCK_MODBUS_DATA | {CONF_ADDRESS: 1.1}, None, {"base": "bad_arguments"}),
        (MOCK_MODBUS_DATA, XthermaTimeoutError, {"base": "timeout"}),
        (MOCK_MODBUS_DATA, XthermaNotConnectedError, {"base": "cannot_connect_modbus"}),
        (MOCK_MODBUS_DATA, Exception, {"base": "unknown"}),
    ],
)
async def test_validate_modbus_tcp(hass, data, side_effect, expected_errors):
    """Test for modbus connection validation."""
    with patch(
        "custom_components.xtherma_fp.xtherma_client_modbus.XthermaClientModbus.connect",
        side_effect=side_effect,
    ):
        assert await _validate_modbus_tcp(hass, data) == expected_errors
