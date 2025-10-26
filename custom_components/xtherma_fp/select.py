"""The xtherma integration selects."""

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import XthermaConfigEntry
from .coordinator import XthermaDataUpdateCoordinator
from .entity import XthermaCoordinatorEntity
from .entity_descriptors import XtSelectEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: XthermaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """HA calls this to initialize sensor platform."""
    _LOGGER.debug("Setup select platform")
    xtherma_data = config_entry.runtime_data
    coordinator = xtherma_data.coordinator

    selects = []
    for desc in coordinator.get_entity_descriptions():
        if not isinstance(desc, XtSelectEntityDescription):
            continue
        _LOGGER.debug('Adding select "%s"', desc.key)
        selects.append(XthermaSelectEntity(coordinator, xtherma_data.device_info, desc))
    _LOGGER.debug("Created %d selects", len(selects))
    async_add_entities(selects)

    xtherma_data.selects_initialized = True

    return True


class XthermaSelectEntity(XthermaCoordinatorEntity, SelectEntity):
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
        super().__init__(coordinator, device_info, description)
        if description.options is None:
            _LOGGER.error("Description of %s has no options!", description.key)
        else:
            self._attr_options = description.options

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        value = self.coordinator.read_value(self.entity_description.key)
        if value is None:
            return
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
            await self.coordinator.async_write(self, value=index)
            self._attr_current_option = option
            self.async_write_ha_state()
        except HomeAssistantError:
            self._attr_force_update = True
            self.async_write_ha_state()
            self._attr_force_update = False
            raise
