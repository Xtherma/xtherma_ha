import asyncio
from datetime import timedelta
from unittest.mock import patch
from homeassistant.const import Platform

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.entity_registry as er
from homeassistant.helpers.entity_platform import async_get_platforms, EntityPlatform
from homeassistant.helpers.entity import Entity

from pytest import fail
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    load_json_value_fixture,
)
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    MockLongPollSideEffect,
)
from sqlalchemy import desc

from custom_components.xtherma_fp.const import (
    CONF_CONNECTION,
    CONF_CONNECTION_RESTAPI,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    EXTRA_STATE_ATTRIBUTE_PARAMETER,
    FERNPORTAL_URL,
)
from custom_components.xtherma_fp.xtherma_data import XthermaData
from tests.const import MOCK_API_KEY, MOCK_SERIAL_NUMBER, MOCK_NAME
from tests.helpers import get_platform, load_mock_data


async def test_async_setup_entry_old(hass, aioclient_mock):
    """Verify old config entries without CONF_CONNECTION work."""
    mock_data = load_mock_data("rest_response.json")
    url = f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}"
    aioclient_mock.get(url, json=mock_data)

    # Create a mock config entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: MOCK_API_KEY,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
        },
        entry_id="test_entry_xtherma",
    )
    entry.add_to_hass(hass)

    # Call async_setup_entry()
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Verify setup worked
    verify_integration_entry(entry)


def verify_integration_entry(entry: ConfigEntry):
    assert isinstance(entry.runtime_data, XthermaData)
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data.sensors_initialized


def verify_integration_sensors(hass: HomeAssistant, entry: ConfigEntry):
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data.sensors_initialized

    our_sensors = [
        state
        for state in hass.states.async_all(Platform.SENSOR)
        if state.entity_id.startswith(f"sensor.{entry.title}")
    ]
    assert len(our_sensors) == 54


def verify_integration_switches(hass: HomeAssistant, entry: ConfigEntry):
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data.switches_initialized

    our_switches = [
        state
        for state in hass.states.async_all(Platform.SWITCH)
        if state.entity_id.startswith(f"switch.{entry.title}")
    ]
    assert len(our_switches) == 7


def verify_integration_numbers(hass: HomeAssistant, entry: ConfigEntry):
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data.numbers_initialized

    our_numbers = [
        state
        for state in hass.states.async_all(Platform.NUMBER)
        if state.entity_id.startswith(f"number.{entry.title}")
    ]
    assert len(our_numbers) == 25


def verify_integration_selects(hass: HomeAssistant, entry: ConfigEntry):
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data.selects_initialized

    our_selects = [
        state
        for state in hass.states.async_all(Platform.SELECT)
        if state.entity_id.startswith(f"select.{entry.title}")
    ]
    assert len(our_selects) == 2


def verify_parameter_keys(hass: HomeAssistant, entry: ConfigEntry):
    entity_reg = er.async_get(hass)
    entries = er.async_entries_for_config_entry(entity_reg, entry.entry_id)
    for reg_entity in entries:
        domain = reg_entity.entity_id.split(".")[0]
        platform = get_platform(hass, domain)
        entity = platform.entities.get(reg_entity.entity_id)
        assert entity is not None
        key = entity._attr_extra_state_attributes.get(EXTRA_STATE_ATTRIBUTE_PARAMETER)
        assert key == entity.entity_description.key


async def test_async_setup_entry_restapi_ok(hass, aioclient_mock):
    """Verify config entries for REST API work."""
    mock_data = load_mock_data("rest_response.json")
    url = f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}"
    aioclient_mock.get(url, json=mock_data)
    # Create a mock config entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
            CONF_API_KEY: MOCK_API_KEY,
            CONF_NAME: MOCK_NAME,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
        },
        entry_id="test_entry_xtherma",
        title="test_entry_xtherma_config",
    )
    entry.add_to_hass(hass)

    # Call async_setup_entry()
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    verify_integration_entry(entry)

    verify_integration_sensors(hass, entry)

    verify_integration_switches(hass, entry)

    verify_integration_numbers(hass, entry)

    verify_integration_selects(hass, entry)

    verify_parameter_keys(hass, entry)
