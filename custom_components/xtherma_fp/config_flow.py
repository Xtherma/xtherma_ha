"""Config flow for the xtherma integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_API_KEY,
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from custom_components.xtherma_fp.xtherma_client_common import (
    XthermaBusyError,
    XthermaError,
    XthermaNotConnectedError,
)

from .const import (
    CONF_CONNECTION,
    CONF_CONNECTION_MODBUSTCP,
    CONF_CONNECTION_RESTAPI,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    FERNPORTAL_URL,
)
from .xtherma_client_modbus import XthermaClientModbus
from .xtherma_client_rest import (
    XthermaClientRest,
    XthermaTimeoutError,
)

_LOGGER = logging.getLogger(__name__)

_DEF_MODBUS_PORT = 502
_DEF_MODBUS_ADDRESS = 1


async def _validate_connection(
    data: dict[str, Any],
) -> dict[str, str]:
    _LOGGER.debug("validate connection settings")
    errors = {}

    serial_number = data.get(CONF_SERIAL_NUMBER)
    if serial_number is None or not serial_number.startswith("FP-"):
        errors["base"] = "bad_arguments"

    return errors


async def _validate_rest_api(
    hass: HomeAssistant,
    previous_data: dict[str, Any],
    data: dict[str, Any],
) -> dict[str, str]:
    _LOGGER.debug("validate REST-API settings")
    errors = {}

    api_key = data.get(CONF_API_KEY)
    if not api_key:
        errors["base"] = "bad_arguments"
        return errors

    serial_number = previous_data.get(CONF_SERIAL_NUMBER, "")

    try:
        session = aiohttp_client.async_get_clientsession(hass)
        client = XthermaClientRest(
            url=FERNPORTAL_URL,
            api_key=api_key,
            serial_number=serial_number,
            session=session,
        )
        await client.connect()
        await client.async_get_data()
        await client.disconnect()
    except XthermaBusyError:
        _LOGGER.debug("RateLimitError")
        errors["base"] = "rate_limit"
    except XthermaTimeoutError:
        _LOGGER.debug("TimeoutError")
        errors["base"] = "timeout"
    except XthermaError:
        _LOGGER.debug("GeneralError")
        errors["base"] = "cannot_connect"
    except Exception:  # noqa: BLE001
        _LOGGER.debug("Unexpected exception")
        errors["base"] = "unknown"

    if errors:
        _LOGGER.debug("validation unsuccessful (%s)", errors["base"])
    else:
        _LOGGER.debug("validation successful")

    return errors


async def _validate_modbus_tcp(
    hass: HomeAssistant,
    data: dict[str, Any],
) -> dict[str, str]:
    """Check values in data dict."""
    _LOGGER.debug("validate Modbus/TCP settings")
    errors = {}

    host = data.get(CONF_HOST)
    port = data.get(CONF_PORT)
    address = data.get(CONF_ADDRESS)
    if not (
        host and port and address and int(port) == port and int(address) == address
    ):
        errors["base"] = "bad_arguments"
        return errors

    try:
        client = XthermaClientModbus(
            host=host,
            port=int(port),
            address=int(address),
        )
        await client.connect()
        await client.async_get_data()
        await client.disconnect()
    except XthermaTimeoutError:
        _LOGGER.debug("TimeoutError")
        errors["base"] = "timeout"
    except XthermaNotConnectedError:
        errors["base"] = "cannot_connect_modbus"
    except Exception as e:  # noqa: BLE001
        _LOGGER.debug("Unexpected exception %s", e)
        errors["base"] = "unknown"

    if errors:
        _LOGGER.debug("validation unsuccessful (%s)", errors["base"])
    else:
        _LOGGER.debug("validation successful")

    return errors


class XthermaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Process config flow."""

    VERSION = 1
    MINOR_VERSION = 0

    def __init__(self) -> None:
        """Constructor."""
        # here we will collect inputs from the various pages
        self._config_data: dict[str, str] = {}

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Process user step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors |= await _validate_connection(user_input)
            if not errors:
                self._config_data.update(user_input)
                connection_type = user_input[CONF_CONNECTION]
                if connection_type == CONF_CONNECTION_RESTAPI:
                    return await self.async_step_rest_api()
                if connection_type == CONF_CONNECTION_MODBUSTCP:
                    return await self.async_step_modbus_tcp()

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_NAME,
                    msg="Entry name",
                ): str,
                vol.Required(
                    CONF_SERIAL_NUMBER,
                    msg="Serial Number (FP-XX-XXXXXX)",
                ): str,
                vol.Required(CONF_CONNECTION): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            CONF_CONNECTION_RESTAPI,
                            CONF_CONNECTION_MODBUSTCP,
                        ],
                        mode=SelectSelectorMode.LIST,
                        translation_key=CONF_CONNECTION,
                    ),
                ),
            },
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_rest_api(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Process rest api config step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors |= await _validate_rest_api(
                self.hass,
                self._config_data,
                user_input,
            )
            if not errors:
                self._config_data.update(user_input)
                return self.async_create_entry(
                    title=self._config_data[CONF_NAME],
                    data=self._config_data,
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY, msg="API Key"): str,
            },
        )

        return self.async_show_form(
            step_id="rest_api",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_modbus_tcp(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Process modbus tcp config step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors |= await _validate_modbus_tcp(
                self.hass,
                user_input,
            )
            if not errors:
                self._config_data.update(user_input)
                return self.async_create_entry(
                    title=self._config_data[CONF_NAME],
                    data=self._config_data,
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=""): str,
                vol.Required(CONF_PORT, default=_DEF_MODBUS_PORT): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=0, max=65535),
                ),
                vol.Required(CONF_ADDRESS, default=_DEF_MODBUS_ADDRESS): vol.All(
                    vol.Coerce(int),
                    NumberSelector(
                        NumberSelectorConfig(
                            min=1,
                            max=255,
                            mode=NumberSelectorMode.BOX,
                        ),
                    ),
                ),
            },
        )

        return self.async_show_form(
            step_id="modbus_tcp",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlowHandler:
        """Create the options flow."""
        return OptionsFlowHandler()


class OptionsFlowHandler(OptionsFlow):
    """Reconfigure integration."""

    def __init__(self) -> None:
        """Constructor."""
        # here we will collect inputs from the various pages
        self._config_data: dict[str, str] = {}

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}
        entry = self.config_entry
        entry = self.config_entry

        self._config_data[CONF_CONNECTION] = entry.data.get(CONF_CONNECTION, "")
        self._config_data[CONF_SERIAL_NUMBER] = entry.data.get(CONF_SERIAL_NUMBER, "")
        self._config_data[CONF_HOST] = entry.data.get(CONF_HOST, "")
        self._config_data[CONF_ADDRESS] = entry.data.get(
            CONF_ADDRESS,
            _DEF_MODBUS_ADDRESS,
        )
        self._config_data[CONF_PORT] = entry.data.get(CONF_PORT, _DEF_MODBUS_PORT)
        self._config_data[CONF_API_KEY] = entry.data.get(CONF_API_KEY, "")

        if user_input is not None:
            self._config_data.update(user_input)
            connection_type = user_input[CONF_CONNECTION]
            if connection_type == CONF_CONNECTION_RESTAPI:
                return await self.async_step_rest_api()
            if connection_type == CONF_CONNECTION_MODBUSTCP:
                return await self.async_step_modbus_tcp()

        def_connection = self._config_data[CONF_CONNECTION]

        schema = vol.Schema(
            {
                vol.Required(CONF_CONNECTION, default=def_connection): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            CONF_CONNECTION_RESTAPI,
                            CONF_CONNECTION_MODBUSTCP,
                        ],
                        mode=SelectSelectorMode.LIST,
                        translation_key=CONF_CONNECTION,
                    ),
                ),
            },
        )

        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)

    async def async_step_rest_api(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Process rest api config step."""
        errors: dict[str, str] = {}

        hass = self.hass
        entry = self.config_entry

        if user_input is not None:
            self._config_data.update(user_input)
            hass.config_entries.async_update_entry(entry, data=self._config_data)
            await hass.config_entries.async_reload(entry.entry_id)
            return self.async_create_entry(data={})

        def_api_key = self._config_data[CONF_API_KEY]

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_API_KEY,
                    msg="API Key",
                    default=def_api_key,
                ): str,
            },
        )

        return self.async_show_form(
            step_id="rest_api",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_modbus_tcp(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Process modbus tcp config step."""
        errors: dict[str, str] = {}

        hass = self.hass
        entry = self.config_entry

        if user_input is not None:
            self._config_data.update(user_input)
            hass.config_entries.async_update_entry(entry, data=self._config_data)
            await hass.config_entries.async_reload(entry.entry_id)
            return self.async_create_entry(data=self._config_data)

        def_host = self._config_data[CONF_HOST]
        def_port = self._config_data[CONF_PORT]
        def_address = self._config_data[CONF_ADDRESS]

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=def_host): str,
                vol.Required(CONF_PORT, default=def_port): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=0, max=65535),
                ),
                vol.Required(
                    CONF_ADDRESS,
                    default=def_address,
                ): NumberSelector(
                    NumberSelectorConfig(min=1, max=255, mode=NumberSelectorMode.BOX),
                ),
            },
        )

        return self.async_show_form(
            step_id="modbus_tcp",
            data_schema=schema,
            errors=errors,
        )
