"""Helpers for tests."""

from typing import Any

import pytest
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import EntityPlatform, async_get_platforms
from homeassistant.util.json import (
    JsonValueType,
)
from pytest_homeassistant_custom_component.common import (
    load_json_value_fixture,
)

from custom_components.xtherma_fp.const import (
    DOMAIN,
    KEY_ENTRY_KEY,
    KEY_ENTRY_VALUE,
    KEY_SETTINGS,
    KEY_TELEMETRY,
)
from custom_components.xtherma_fp.entity_descriptors import MODBUS_ENTITY_DESCRIPTIONS


def get_platform(hass: HomeAssistant, domain: str) -> EntityPlatform:
    platforms = async_get_platforms(hass, DOMAIN)
    for platform in platforms:
        if platform.domain == domain:
            return platform
    pytest.fail(f"We have no platfom {domain}")


def get_sensor_platform(hass: HomeAssistant) -> EntityPlatform:
    return get_platform(hass, Platform.SENSOR)


def get_switch_platform(hass: HomeAssistant) -> EntityPlatform:
    return get_platform(hass, Platform.SWITCH)


def get_number_platform(hass: HomeAssistant) -> EntityPlatform:
    return get_platform(hass, Platform.NUMBER)


def get_select_platform(hass: HomeAssistant) -> EntityPlatform:
    return get_platform(hass, Platform.SELECT)


def find_entry(values: list[dict], key: str) -> dict[str, Any] | None:
    for entry in values:
        if entry[KEY_ENTRY_KEY] == key:
            return entry
    raise KeyError(key)


def load_mock_data(filename: str) -> JsonValueType:
    return load_json_value_fixture(filename)


def load_modbus_regs_from_json(filename: str) -> list[list[int]]:
    """Integration using Modbus."""
    # Create a mock config entry
    mock_data = load_mock_data(filename)
    assert isinstance(mock_data, dict)
    telemetry = mock_data[KEY_TELEMETRY]
    settings = mock_data[KEY_SETTINGS]
    assert isinstance(telemetry, list)
    assert isinstance(settings, list)
    all_values = telemetry
    all_values.extend(settings)
    regs_list = []
    for reg_desc in MODBUS_ENTITY_DESCRIPTIONS:
        regs = [0] * len(reg_desc.descriptors)
        for i, desc in enumerate(reg_desc.descriptors):
            if desc is None:
                continue
            entry = find_entry(all_values, desc.key)
            if entry is None:
                continue
            value = int(str(entry[KEY_ENTRY_VALUE]))
            regs[i] = value
        regs_list.append(regs)
    return regs_list


def load_rest_response():
    """Return a list of complete Modbus register read-outs.

    Currently returns only one read-out based on our standard REST API response.
    """
    regs_list = load_modbus_regs_from_json("rest_response.json")
    return [regs_list]
