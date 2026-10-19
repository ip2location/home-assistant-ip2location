"""Binary sensor platform for IP2Location.io."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import Ip2LocationCoordinator
from .entity import Ip2LocationEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the proxy binary sensor."""
    coordinator: Ip2LocationCoordinator = entry.runtime_data
    if "is_proxy" in (coordinator.data or {}):
        async_add_entities([Ip2LocationProxyBinarySensor(coordinator)])


class Ip2LocationProxyBinarySensor(Ip2LocationEntity, BinarySensorEntity):
    """Whether the IP is a known proxy, VPN or Tor exit node."""

    _attr_translation_key = "is_proxy"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: Ip2LocationCoordinator) -> None:
        """Initialise the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_is_proxy"

    @property
    def is_on(self) -> bool:
        """Return True when the IP is flagged as a proxy."""
        return bool((self.coordinator.data or {}).get("is_proxy"))
