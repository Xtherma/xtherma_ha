"""Tests for Xtherma translations."""

from homeassistant.components.binary_sensor import (
    BinarySensorEntityDescription,
)
from homeassistant.components.number import (
    NumberEntityDescription,
)
from homeassistant.components.select import (
    SelectEntityDescription,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
)
from homeassistant.components.switch import (
    SwitchEntityDescription,
)
from homeassistant.const import Platform
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.translation import async_get_translations

from custom_components.xtherma_fp.const import DOMAIN
from custom_components.xtherma_fp.entity_descriptors import (
    ENTITY_DESCRIPTIONS,
    MODBUS_ENTITY_DESCRIPTIONS,
)


async def test_sensor_name_translation(hass, init_integration):
    """Ensure all sensor names are translated."""
    prefix = f"component.{DOMAIN}.entity.{Platform.SENSOR.value}"

    for lang in ["en", "de"]:
        # collect all entity translations
        all_entity_translations = await async_get_translations(
            hass, lang, "entity", [DOMAIN]
        )
        domain_entity_translations = {
            k for k in all_entity_translations if k.startswith(prefix) and ".name" in k
        }

        # collect all options of all sensors
        entity_classes = (
            SensorEntityDescription,
            BinarySensorEntityDescription,
        )
        entity_names_rest = {
            f"{prefix}.{entity_description.key}.name"
            for entity_description in ENTITY_DESCRIPTIONS
            if isinstance(entity_description, entity_classes)
        }
        entity_names_modbus = {
            f"{prefix}.{entity_description.key}.name"
            for reg_desc in MODBUS_ENTITY_DESCRIPTIONS
            for entity_description in reg_desc.descriptors
            if isinstance(entity_description, entity_classes)
        }

        assert (
            entity_names_rest.union(entity_names_modbus) == domain_entity_translations
        )


def _get_all_entity_descriptions() -> list[EntityDescription]:
    keys: set[str] = set()
    descs: list[EntityDescription] = []

    all_descs: list[EntityDescription] = [
        entity_description
        for reg_desc in MODBUS_ENTITY_DESCRIPTIONS
        for entity_description in reg_desc.descriptors
        if isinstance(entity_description, EntityDescription)
    ]
    all_descs.extend(ENTITY_DESCRIPTIONS)

    for entity_description in all_descs:
        if (
            isinstance(entity_description, EntityDescription)
            and entity_description.key not in keys
        ):
            keys.add(entity_description.key)
            descs.append(entity_description)
    return descs


async def test_enum_sensor_translation(hass, init_integration):
    """Ensure all enum sensor values are translated."""
    prefix = f"component.{DOMAIN}.entity.{Platform.SENSOR.value}"

    for lang in ["en", "de"]:
        # collect all sensor state translations
        translations = await async_get_translations(hass, lang, "entity", [DOMAIN])
        translation_states = {
            k for k in translations if k.startswith(prefix) and ".state." in k
        }

        # collect all options of all enum sensors
        sensor_descs = _get_all_entity_descriptions()
        sensor_options = {
            f"{prefix}.{entity_description.key}.state.{option}"
            for entity_description in sensor_descs
            if isinstance(entity_description, SensorEntityDescription)
            if entity_description.device_class == SensorDeviceClass.ENUM
            if entity_description.options is not None
            for option in entity_description.options
        }
        assert sensor_options == translation_states


async def test_switch_name_translation(hass, init_integration):
    """Ensure all switch names are translated."""
    prefix = f"component.{DOMAIN}.entity.{Platform.SWITCH.value}"

    for lang in ["en", "de"]:
        # collect all entity translations
        all_entity_translations = await async_get_translations(
            hass, lang, "entity", [DOMAIN]
        )
        domain_entity_translations = {
            k for k in all_entity_translations if k.startswith(prefix) and ".name" in k
        }

        # collect all options of all switches
        entity_classes = (SwitchEntityDescription,)
        entity_names_rest = {
            f"{prefix}.{entity_description.key}.name"
            for entity_description in ENTITY_DESCRIPTIONS
            if isinstance(entity_description, entity_classes)
        }
        entity_names_modbus = {
            f"{prefix}.{entity_description.key}.name"
            for reg_desc in MODBUS_ENTITY_DESCRIPTIONS
            for entity_description in reg_desc.descriptors
            if isinstance(entity_description, entity_classes)
        }

        assert (
            entity_names_rest.union(entity_names_modbus) == domain_entity_translations
        )


async def test_number_name_translation(hass, init_integration):
    """Ensure all number names are translated."""
    prefix = f"component.{DOMAIN}.entity.{Platform.NUMBER.value}"

    for lang in ["en", "de"]:
        # collect all entity translations
        all_entity_translations = await async_get_translations(
            hass, lang, "entity", [DOMAIN]
        )
        domain_entity_translations = {
            k for k in all_entity_translations if k.startswith(prefix) and ".name" in k
        }

        # collect all options of all switches
        entity_classes = (NumberEntityDescription,)
        entity_names_rest = {
            f"{prefix}.{entity_description.key}.name"
            for entity_description in ENTITY_DESCRIPTIONS
            if isinstance(entity_description, entity_classes)
        }
        entity_names_modbus = {
            f"{prefix}.{entity_description.key}.name"
            for reg_desc in MODBUS_ENTITY_DESCRIPTIONS
            for entity_description in reg_desc.descriptors
            if isinstance(entity_description, entity_classes)
        }

        assert (
            entity_names_rest.union(entity_names_modbus) == domain_entity_translations
        )


async def test_select_name_translation(hass, init_integration):
    """Ensure all select names are translated."""
    prefix = f"component.{DOMAIN}.entity.{Platform.SELECT.value}"

    for lang in ["en", "de"]:
        # collect all entity translations
        all_entity_translations = await async_get_translations(
            hass, lang, "entity", [DOMAIN]
        )
        domain_entity_translations = {
            k for k in all_entity_translations if k.startswith(prefix) and ".name" in k
        }

        # collect all options of all switches
        entity_classes = (SelectEntityDescription,)
        entity_names_rest = {
            f"{prefix}.{entity_description.key}.name"
            for entity_description in ENTITY_DESCRIPTIONS
            if isinstance(entity_description, entity_classes)
        }
        entity_names_modbus = {
            f"{prefix}.{entity_description.key}.name"
            for reg_desc in MODBUS_ENTITY_DESCRIPTIONS
            for entity_description in reg_desc.descriptors
            if isinstance(entity_description, entity_classes)
        }

        assert (
            entity_names_rest.union(entity_names_modbus) == domain_entity_translations
        )


async def test_select_options_translation(hass, init_integration):
    """Ensure all select options are translated."""
    prefix = f"component.{DOMAIN}.entity.{Platform.SELECT.value}"

    for lang in ["en", "de"]:
        # collect all select state translations
        translations = await async_get_translations(hass, lang, "entity", [DOMAIN])
        translation_states = {
            k for k in translations if k.startswith(prefix) and ".state." in k
        }

        # collect all options of all select entities
        sensor_descs = _get_all_entity_descriptions()
        sensor_options = {
            f"{prefix}.{entity_description.key}.state.{option}"
            for entity_description in sensor_descs
            if isinstance(entity_description, SelectEntityDescription)
            if entity_description.options is not None
            for option in entity_description.options
        }
        assert sensor_options == translation_states
