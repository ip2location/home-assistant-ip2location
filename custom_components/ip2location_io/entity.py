"""Base entity for IP2Location.io."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import Ip2LocationCoordinator


class Ip2LocationEntity(CoordinatorEntity[Ip2LocationCoordinator]):
    """Common behaviour shared by all IP2Location.io entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: Ip2LocationCoordinator) -> None:
        """Initialise the entity and its device."""
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=MANUFACTURER,
            model=MODEL,
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.ip2location.io/",
        )
