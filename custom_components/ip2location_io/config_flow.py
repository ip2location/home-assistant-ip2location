"""Config flow for the IP2Location.io integration."""

from __future__ import annotations

import ipaddress
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback

from .api import (
    Ip2LocationAuthError,
    Ip2LocationConnectionError,
    Ip2LocationRateLimitError,
    async_get_geolocation,
)
from .const import (
    CONF_API_KEY,
    CONF_IP_ADDRESS,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TITLE,
    DOMAIN,
    LOGGER,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    SELF_UNIQUE_ID,
)


def _validate_ip(value: str) -> str:
    """Validate an optional IPv4/IPv6 address."""
    value = (value or "").strip()
    if not value:
        return ""
    try:
        ipaddress.ip_address(value)
    except ValueError as err:
        raise vol.Invalid("invalid_ip") from err
    return value


class Ip2LocationConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the UI configuration of IP2Location.io."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = (user_input.get(CONF_API_KEY) or "").strip() or None
            ip_address = (user_input.get(CONF_IP_ADDRESS) or "").strip() or None

            try:
                data = await async_get_geolocation(self.hass, api_key, ip_address)
            except Ip2LocationAuthError:
                errors["base"] = "invalid_auth"
            except Ip2LocationRateLimitError:
                errors["base"] = "rate_limit"
            except Ip2LocationConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                LOGGER.exception("Unexpected error during IP2Location.io setup")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(ip_address or SELF_UNIQUE_ID)
                self._abort_if_unique_id_configured()

                title = user_input.get(CONF_NAME) or DEFAULT_TITLE.format(
                    ip=data.get("ip", ip_address or "auto")
                )
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_API_KEY: api_key,
                        CONF_IP_ADDRESS: ip_address,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=""): str,
                    vol.Optional(CONF_API_KEY, default=""): str,
                    vol.Optional(CONF_IP_ADDRESS, default=""): _validate_ip,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow."""
        return Ip2LocationOptionsFlow()


class Ip2LocationOptionsFlow(OptionsFlow):
    """Handle the options of an IP2Location.io entry."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}
        entry = self.config_entry

        if user_input is not None:
            api_key = (user_input.get(CONF_API_KEY) or "").strip() or None
            try:
                await async_get_geolocation(
                    self.hass, api_key, entry.data.get(CONF_IP_ADDRESS) or None
                )
            except Ip2LocationAuthError:
                errors["base"] = "invalid_auth"
            except Ip2LocationRateLimitError:
                errors["base"] = "rate_limit"
            except Ip2LocationConnectionError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="", data=user_input)

        current_key = entry.options.get(CONF_API_KEY, entry.data.get(CONF_API_KEY))
        current_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_API_KEY, default=current_key or ""): str,
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=int(current_interval)
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                    ),
                }
            ),
            errors=errors,
        )
