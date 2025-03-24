"""The xtherma integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import CONF_API_KEY, Platform

from .const import FERNPORTAL_URL, CONF_SERIAL_NUMBER, DOMAIN, LOGGER, VERSION
from .xtherma_client import XthermaClient
from .coordinator import XthermaDataUpdateCoordinator
from .xtherma_data import XthermaData

_PLATFORMS = [ Platform.SENSOR ]

async def async_setup_entry(
    hass: HomeAssistant, 
    entry: ConfigEntry, 
) -> bool:
    LOGGER.debug(f"Setup integration")

    # setup global data
    hass.data.setdefault(DOMAIN, {})
    xtherma_data = XthermaData()
    hass.data[DOMAIN][entry.entry_id] = xtherma_data

    # required configuration
    api_key = entry.data[CONF_API_KEY]
    serial_number = entry.data[CONF_SERIAL_NUMBER]
    xtherma_data.serial_fp = serial_number

    # create API client connector
    client = XthermaClient(
        url = FERNPORTAL_URL, 
        api_key = api_key, 
        serial_number = serial_number, 
        session = async_get_clientsession(hass))

    # create data coordinator 
    # first refresh may take some time, especially if the config flow just ran,
    # so do this asynchronously
    xtherma_data.coordinator = XthermaDataUpdateCoordinator(hass, entry, client)

    # If we just passed the config flow, we will not be able to immediately fetch
    # fresh data (see https://github.com/Xtherma/Xtherma-API/issues/5)
    # We will therefore ignore errors here.
    try:
        LOGGER.debug("Attempting initial data fetch")
        await xtherma_data.coordinator.async_config_entry_first_refresh()
    except Exception:
        LOGGER.debug("Data fetch failed, probably due to rate limiting. Will try again.")
        pass

    # initialize platforms
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    LOGGER.debug("Unload integration")
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)

async def async_migrate_entry(hass, config_entry: ConfigEntry):
    LOGGER.debug("Migrating configuration from version %s.%s", config_entry.version, config_entry.minor_version)

    if config_entry.version > VERSION:
        LOGGER.error("Downgrade not supported")
        return False

    return True
