"""Data update coordinator for IP2Location.io."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    Ip2LocationAuthError,
    Ip2LocationError,
    async_get_geolocation,
)
from .const import DOMAIN, LOGGER


class Ip2LocationCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll the IP2Location.io API on a fixed interval."""

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        config_entry: ConfigEntry,
        api_key: str | None,
        ip_address: str | None,
        update_interval: timedelta,
    ) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
            config_entry=config_entry,
        )
        self.api_key = api_key
        self.ip_address = ip_address

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the latest geolocation data."""
        try:
            return await async_get_geolocation(self.hass, self.api_key, self.ip_address)
        except Ip2LocationAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except Ip2LocationError as err:
            raise UpdateFailed(str(err)) from err
