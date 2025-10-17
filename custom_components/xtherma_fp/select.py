"""The xtherma integration selects."""

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import (
    DeviceInfo,
)
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from custom_components.xtherma_fp.const import EXTRA_STATE_ATTRIBUTE_PARAMETER

from .coordinator import XthermaDataUpdateCoordinator, read_coordinator_value
from .entity_descriptors import (
    XtSelectEntityDescription,
)
from .xtherma_data import XthermaData

_LOGGER = logging.getLogger(__name__)


# Create a sensor entity based on description.
def __build_select(
    desc: EntityDescription,
    coordinator: XthermaDataUpdateCoordinator,
    device_info: DeviceInfo,
) -> Entity | None:
    if isinstance(desc, XtSelectEntityDescription):
        return XthermaSelectEntity(coordinator, device_info, desc)
    return None


# Create and register sensor entities based on coordinator.data.
# Call site must ensure there is data and sensors are not already
# registered.
def _initialize_selects(
    xtherma_data: XthermaData,
    async_add_entities: AddEntitiesCallback,
) -> None:
    assert not xtherma_data.selects_initialized  # noqa: S101

    coordinator = xtherma_data.coordinator

    assert coordinator is not None  # noqa: S101

    selects = []
    for desc in coordinator.get_entity_descriptions():
        select = __build_select(desc, coordinator, xtherma_data.device_info)
        if select:
            _LOGGER.debug('Adding select "%s"', desc.key)
            selects.append(select)
    _LOGGER.debug("Created %d selects", len(selects))
    async_add_entities(selects)

    xtherma_data.selects_initialized = True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """HA calls this to initialize sensor platform."""
    xtherma_data: XthermaData = config_entry.runtime_data

    _LOGGER.debug("Setup select platform")

    _initialize_selects(xtherma_data, async_add_entities)

    return True


class XthermaSelectEntity(CoordinatorEntity, SelectEntity):
    """Xtherma Select Input."""

    # keep this for type safe access to custom members
    xt_description: XtSelectEntityDescription

    def __init__(
        self,
        coordinator: XthermaDataUpdateCoordinator,
        device_info: DeviceInfo,
        description: XtSelectEntityDescription,
    ) -> None:
        """Class Constructor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self.entity_description = description
        self.xt_description = description
        self._attr_has_entity_name = True
        if description.options is None:
            _LOGGER.error("Description of %s has no options!", description.key)
        else:
            self._attr_options = description.options
        self._attr_device_info = device_info
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{description.key}"
        self._attr_extra_state_attributes = {
            EXTRA_STATE_ATTRIBUTE_PARAMETER: self.xt_description.key,
        }
        self.translation_key = description.key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        value = read_coordinator_value(self._coordinator, self.entity_description.key)
        new_index = int(value) % len(self.options)
        self._attr_current_option = self.options[new_index]
        self.async_write_ha_state()

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        if self.xt_description.icon_provider:
            return self.xt_description.icon_provider(self._attr_current_option)
        return super().icon

    async def async_select_option(self, option: str) -> None:
        """Set value."""
        try:
            index = self.options.index(option)
            await self._coordinator.async_write(self, value=index)
            self._attr_current_option = option
            self.async_write_ha_state()
        except HomeAssistantError:
            self._attr_force_update = True
            self.async_write_ha_state()
            self._attr_force_update = False
            raise
