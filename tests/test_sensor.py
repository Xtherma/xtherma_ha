import pytest

from homeassistant.core import State, HomeAssistant
from homeassistant.helpers.entity_platform import async_get_platforms
from homeassistant.helpers.translation import async_get_translations
from homeassistant.const import Platform
from custom_components.xtherma_fp.const import DOMAIN

from homeassistant.components.sensor import (
    SensorDeviceClass,
)
from custom_components.xtherma_fp.sensor_descriptors import SENSOR_DESCRIPTIONS


async def _find_state(hass: HomeAssistant, id: str) -> State:
    full_id = f"sensor.xtherma_fp_{id}"
    state = hass.states.get(full_id)
    assert state is not None
    return state


# def _get_entity(hass: HomeAssistant, state: State) -> Entity:


async def test_binary_sensor_state(hass, init_integration):
    pk = await _find_state(hass, "pk")
    assert pk.state == "off"
    pww = await _find_state(hass, "pww")
    assert pww.state == "on"


async def test_binary_sensor_icon(hass, init_integration):
    platforms = async_get_platforms(hass, DOMAIN)
    assert len(platforms) == 1
    platform = platforms[0]
    pk = await _find_state(hass, "pk")
    assert pk.state == "off"
    e_pk = platform.entities.get(pk.entity_id)
    assert e_pk is not None
    assert e_pk.icon == "mdi:pump-off"
    pww = await _find_state(hass, "pww")
    assert pww.state == "on"
    e_pww = platform.entities.get(pww.entity_id)
    assert e_pww is not None
    assert e_pww.icon == "mdi:pump"


async def test_opmode_sensor_icon(hass, init_integration):
    platforms = async_get_platforms(hass, DOMAIN)
    assert len(platforms) == 1
    platform = platforms[0]
    state = await _find_state(hass, "mode_3")
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.icon == "mdi:thermometer-water"


async def test_enum_sensor_translation(hass, init_integration):
    """Ensure all enum sensor values are translated."""
    prefix = f"component.{DOMAIN}.entity.{Platform.SENSOR.value}"

    for lang in [ "en", "de" ]:
        # collect all sensor state translations
        translations = await async_get_translations(hass, lang, "entity", [DOMAIN])
        translation_states = {
            k for k in translations if k.startswith(prefix) and ".state." in k
        }

        # collect all options of all enum sensors
        sensor_options = {
            f"{prefix}.{entity_description.key}.state.{option}"
            for entity_description in SENSOR_DESCRIPTIONS
            if entity_description.device_class == SensorDeviceClass.ENUM
            for option in entity_description.options
        }

        assert sensor_options == translation_states


async def test_sensor_name_translation(hass, init_integration):
    """Ensure all sensor names are translated."""
    prefix = f"component.{DOMAIN}.entity.{Platform.SENSOR.value}"

    for lang in [ "en", "de" ]:
        # collect all sensor state translations
        translations = await async_get_translations(hass, lang, "entity", [DOMAIN])
        translation_states = {
            k for k in translations if k.startswith(prefix) and ".name" in k
        }

        # collect all options of all enum sensors
        sensor_names = {
            f"{prefix}.{entity_description.key}.name"
            for entity_description in SENSOR_DESCRIPTIONS
        }

        assert sensor_names == translation_states


async def test_sgready_sensor_icon(hass, init_integration):
    platforms = async_get_platforms(hass, DOMAIN)
    assert len(platforms) == 1
    platform = platforms[0]
    state = await _find_state(hass, "sg")
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.icon == "mdi:cancel"


async def test_sensor_name(hass, init_integration):
    """Check if regular sensors have proper (translated) names."""
    await hass.config.async_load()
    platforms = async_get_platforms(hass, DOMAIN)
    assert len(platforms) == 1
    platform = platforms[0]
    state = await _find_state(hass, "ld1")
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.name == "[LD1] Fan 1 speed"


async def test_binary_sensor_name(hass, init_integration):
    """Check if binary sensors have a proper (translated) names."""
    await hass.config.async_load()
    platforms = async_get_platforms(hass, DOMAIN)
    assert len(platforms) == 1
    platform = platforms[0]
    state = await _find_state(hass, "pww")
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.name == "[PWW] Circulation pump hot water enabled"


async def test_enum_sensor_name(hass, init_integration):
    """Check if enum sensors have a proper (translated) names."""
    await hass.config.async_load()
    platforms = async_get_platforms(hass, DOMAIN)
    assert len(platforms) == 1
    platform = platforms[0]
    state = await _find_state(hass, "mode_3")
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.name == "Operating mode"
