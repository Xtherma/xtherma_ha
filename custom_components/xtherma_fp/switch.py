"""The xtherma integration switches."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    XtSwitchEntityDescription,
)
from .xtherma_data import XthermaData

_LOGGER = logging.getLogger(__name__)


# Create a sensor entity based on description.
def __build_switch(
    desc: EntityDescription,
    coordinator: XthermaDataUpdateCoordinator,
    device_info: DeviceInfo,
) -> Entity | None:
    if isinstance(desc, XtSwitchEntityDescription):
        return XthermaSwitchEntity(coordinator, device_info, desc)
    return None


# Create and register sensor entities based on coordinator.data.
# Call site must ensure there is data and sensors are not already
# registerd.
def _initialize_switches(
    xtherma_data: XthermaData,
    async_add_entities: AddEntitiesCallback,
) -> None:
    assert not xtherma_data.switches_initialized  # noqa: S101

    coordinator = xtherma_data.coordinator

    assert coordinator is not None  # noqa: S101

    switches = []
    for desc in coordinator.get_entity_descriptions():
        switch = __build_switch(desc, coordinator, xtherma_data.device_info)
        if switch:
            _LOGGER.debug('Adding switch "%s"', desc.key)
            switches.append(switch)
    _LOGGER.debug("Created %d switches", len(switches))
    async_add_entities(switches)

    xtherma_data.switches_initialized = True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """HA calls this to initialize sensor platform."""
    xtherma_data: XthermaData = config_entry.runtime_data

    _LOGGER.debug("Setup switch platform")

    # Normally, __init__.py will have done an initial fetch and we should
    # have data in the coordinator to initialize the sensors.
    # If not (eg. because we just completed the config flow or the integration was
    # restarted too rapidly) we will try again in the listener.
    _initialize_switches(xtherma_data, async_add_entities)

    return True


class XthermaSwitchEntity(CoordinatorEntity, SwitchEntity):
    """Xtherma Switch Input."""

    # keep this for type safe access to custom members
    xt_description: XtSwitchEntityDescription

    def __init__(
        self,
        coordinator: XthermaDataUpdateCoordinator,
        device_info: DeviceInfo,
        description: XtSwitchEntityDescription,
    ) -> None:
        """Class Constructor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self.entity_description = description
        self.xt_description = description
        self._attr_has_entity_name = True
        self._attr_device_info = device_info
        self._attr_device_class = description.device_class
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{description.key}"
        self._attr_extra_state_attributes = {
            EXTRA_STATE_ATTRIBUTE_PARAMETER: self.xt_description.key,
        }
        self.translation_key = description.key
        """
        Avoid the "unknown" state which will make the frontend render this as two icon
        buttons in case the coordinator fails to update. Note we also need to
        explicitly initialize _attr_assumed_state as an instance value, even though
        the class default is already False. I think this may have to do with the
        serialization towards the frontend.
        """
        self._attr_is_on = False
        self._attr_assumed_state = False

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        value = read_coordinator_value(self._coordinator, self.entity_description.key)
        self._attr_is_on = value > 0
        self.async_write_ha_state()

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        if self.xt_description.icon_provider:
            return self.xt_description.icon_provider(self.is_on)
        return super().icon

    async def async_turn_on(self, **kwargs: Any) -> None:  # noqa: ANN401
        """Turn the entity on."""
        try:
            await self._coordinator.async_write(self, 1)
            self._attr_is_on = True
            self.async_write_ha_state()
        except HomeAssistantError:
            self._attr_force_update = True
            self.async_write_ha_state()
            self._attr_force_update = False
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:  # noqa: ANN401
        """Turn the entity off."""
        try:
            await self._coordinator.async_write(self, 0)
            self._attr_is_on = False
            self.async_write_ha_state()
        except Exception:
            self._attr_force_update = True
            self.async_write_ha_state()
            self._attr_force_update = False
            raise
