"""Client for the IP2Location.io geolocation API."""

from __future__ import annotations

import asyncio
from http import HTTPStatus
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_BASE_URL, REQUEST_TIMEOUT


class Ip2LocationError(Exception):
    """Base error for the IP2Location.io API."""


class Ip2LocationAuthError(Ip2LocationError):
    """The API key is missing or invalid."""


class Ip2LocationRateLimitError(Ip2LocationError):
    """The daily or monthly query quota has been exhausted."""


class Ip2LocationConnectionError(Ip2LocationError):
    """The API could not be reached or returned an unusable response."""


async def async_get_geolocation(
    hass: HomeAssistant,
    api_key: str | None,
    ip_address: str | None,
) -> dict[str, Any]:
    """Look up the geolocation of an IP address.

    When ``ip_address`` is ``None`` the API geolocates the caller itself,
    which is the public IP of the Home Assistant host.
    """
    session = async_get_clientsession(hass)

    params: dict[str, str] = {"format": "json"}
    if ip_address:
        params["ip"] = ip_address

    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    try:
        async with asyncio.timeout(REQUEST_TIMEOUT):
            response = await session.get(API_BASE_URL, params=params, headers=headers)
            async with response:
                if response.status in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
                    raise Ip2LocationAuthError(f"HTTP {response.status}")
                if response.status == HTTPStatus.TOO_MANY_REQUESTS:
                    raise Ip2LocationRateLimitError("rate limit exceeded")
                response.raise_for_status()
                data = await response.json(content_type=None)
    except Ip2LocationError:
        raise
    except (aiohttp.ClientError, TimeoutError, ValueError) as err:
        raise Ip2LocationConnectionError(str(err)) from err

    if not isinstance(data, dict):
        raise Ip2LocationConnectionError("unexpected response body")

    error = data.get("error")
    if isinstance(error, dict):
        code = error.get("error_code")
        message = error.get("error_message") or "unknown API error"
        if code in (401, 403):
            raise Ip2LocationAuthError(message)
        if code == 429:
            raise Ip2LocationRateLimitError(message)
        raise Ip2LocationError(message)

    if "country_code" not in data:
        raise Ip2LocationRateLimitError(data.get("message") or "quota exceeded")

    return data
