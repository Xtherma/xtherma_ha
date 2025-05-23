"""The Xtherma integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.const import (
    CONF_ADDRESS,
    CONF_API_KEY,
    CONF_HOST,
    CONF_PORT,
    Platform,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_CONNECTION,
    CONF_CONNECTION_RESTAPI,
    CONF_SERIAL_NUMBER,
    FERNPORTAL_URL,
    VERSION,
)
from .coordinator import XthermaDataUpdateCoordinator
from .xtherma_client_modbus import XthermaClientModbus
from .xtherma_client_rest import XthermaClientRest
from .xtherma_data import XthermaData

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

_PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Initialize integration."""
    _LOGGER.debug("Setup integration")

    # setup global data - Note that subclassing ConfigEntry would be nicer for
    # type safety, but then the MockConfigEntry used in tests would be incompatible.
    xtherma_data = XthermaData()
    entry.runtime_data = xtherma_data

    # create API client connector
    connection = entry.data.get(CONF_CONNECTION, CONF_CONNECTION_RESTAPI)
    if connection == CONF_CONNECTION_RESTAPI:
        api_key = entry.data[CONF_API_KEY]
        serial_number = entry.data[CONF_SERIAL_NUMBER]
        xtherma_data.serial_fp = serial_number
        client = XthermaClientRest(
            url=FERNPORTAL_URL,
            api_key=api_key,
            serial_number=serial_number,
            session=async_get_clientsession(hass),
        )
    else:
        host = entry.data[CONF_HOST]
        port = entry.data[CONF_PORT]
        address = entry.data[CONF_ADDRESS]
        client = XthermaClientModbus(
            host=host,
            port=port,
            address=address,
        )

    # create data coordinator
    # first refresh may take some time, especially if the config flow just ran,
    # so do this asynchronously
    xtherma_data.coordinator = XthermaDataUpdateCoordinator(hass, entry, client)

    # If we just passed the config flow, we will not be able to immediately fetch
    # fresh data (see https://github.com/Xtherma/Xtherma-API/issues/5)
    # We will therefore ignore errors here.
    try:
        _LOGGER.debug("Attempting initial data fetch")
        await xtherma_data.coordinator.async_config_entry_first_refresh()
    except Exception:  # noqa: BLE001
        _LOGGER.debug(
            "Data fetch failed, probably due to rate limiting. Will try again.",
        )

    # initialize platforms
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload integration."""
    _LOGGER.debug("Unload integration")
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)


async def async_migrate_entry(_: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate config entry."""
    if config_entry.version > VERSION:
        _LOGGER.error("Downgrade not supported")
        return False

    if config_entry.version < VERSION:
        _LOGGER.debug(
            "Migrating configuration from version %s.%s",
            config_entry.version,
            config_entry.minor_version,
        )

    return True
