"""Sensor platform for IP2Location.io."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import EMPTY_VALUES
from .coordinator import Ip2LocationCoordinator
from .entity import Ip2LocationEntity

DIAGNOSTIC = EntityCategory.DIAGNOSTIC

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="ip",
        icon="mdi:ip-network",
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(key="country_code", icon="mdi:flag-variant"),
    SensorEntityDescription(key="country_name", icon="mdi:earth"),
    SensorEntityDescription(key="region_name", icon="mdi:map-marker-radius"),
    SensorEntityDescription(key="city_name", icon="mdi:city-variant-outline"),
    SensorEntityDescription(
        key="zip_code",
        icon="mdi:mailbox-outline",
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="latitude",
        icon="mdi:latitude",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="longitude",
        icon="mdi:longitude",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="time_zone",
        icon="mdi:clock-outline",
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="asn",
        icon="mdi:domain",
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="as",
        icon="mdi:office-building-outline",
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="isp",
        icon="mdi:server-network",
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="domain",
        icon="mdi:web",
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="net_speed",
        icon="mdi:speedometer",
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="idd_code",
        icon="mdi:phone-classic",
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="area_code",
        icon="mdi:phone-outline",
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="weather_station_code",
        icon="mdi:weather-partly-cloudy",
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="weather_station_name",
        icon="mdi:weather-cloudy",
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="elevation",
        icon="mdi:elevation-rise",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.METERS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="usage_type",
        icon="mdi:tag-outline",
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="address_type",
        icon="mdi:ip-outline",
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="mcc",
        icon="mdi:cellphone",
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="mnc",
        icon="mdi:cellphone-link",
        entity_category=DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="mobile_brand",
        icon="mdi:cellphone-marker",
        entity_category=DIAGNOSTIC,
    ),
)


def _is_displayable(value: Any) -> bool:
    """Return True when a field holds a scalar we can show."""
    return isinstance(value, (str, int, float, bool)) and value not in EMPTY_VALUES


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensors for the fields the current plan returns."""
    coordinator: Ip2LocationCoordinator = entry.runtime_data
    data = coordinator.data or {}

    async_add_entities(
        Ip2LocationSensor(coordinator, description)
        for description in SENSOR_TYPES
        if _is_displayable(data.get(description.key))
    )


class Ip2LocationSensor(Ip2LocationEntity, SensorEntity):
    """A single geolocation field."""

    entity_description: SensorEntityDescription

    def __init__(
        self,
        coordinator: Ip2LocationCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return the current value."""
        value = (self.coordinator.data or {}).get(self.entity_description.key)
        return None if value in EMPTY_VALUES else value
