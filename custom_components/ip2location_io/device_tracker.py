"""Device tracker platform for IP2Location.io."""

from __future__ import annotations

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import Ip2LocationCoordinator
from .entity import Ip2LocationEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the location tracker when coordinates are available."""
    coordinator: Ip2LocationCoordinator = entry.runtime_data
    data = coordinator.data or {}
    if data.get("latitude") is not None and data.get("longitude") is not None:
        async_add_entities([Ip2LocationTracker(coordinator)])


class Ip2LocationTracker(Ip2LocationEntity, TrackerEntity):
    """Plot the geolocated IP on the Home Assistant map."""

    _attr_translation_key = "location"

    def __init__(self, coordinator: Ip2LocationCoordinator) -> None:
        """Initialise the tracker."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_location"

    @property
    def latitude(self) -> float | None:
        """Return the latitude."""
        return (self.coordinator.data or {}).get("latitude")

    @property
    def longitude(self) -> float | None:
        """Return the longitude."""
        return (self.coordinator.data or {}).get("longitude")

    @property
    def location_name(self) -> str | None:
        """Return a human readable location."""
        data = self.coordinator.data or {}
        parts = [
            part
            for part in (data.get("city_name"), data.get("country_name"))
            if part
        ]
        return ", ".join(parts) or None

    @property
    def source_type(self) -> SourceType:
        """Return the source type."""
        return SourceType.ROUTER
