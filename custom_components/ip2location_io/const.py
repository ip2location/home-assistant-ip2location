"""Constants for the IP2Location.io integration."""

from __future__ import annotations

import logging
from typing import Final

DOMAIN: Final = "ip2location_io"
LOGGER = logging.getLogger(__package__)

MANUFACTURER: Final = "IP2Location"
MODEL: Final = "IP Geolocation API"

API_BASE_URL: Final = "https://api.ip2location.io/"
REQUEST_TIMEOUT: Final = 30

CONF_API_KEY: Final = "api_key"
CONF_IP_ADDRESS: Final = "ip_address"
CONF_NAME: Final = "name"
CONF_SCAN_INTERVAL: Final = "scan_interval"

DEFAULT_TITLE: Final = "IP2Location.io ({ip})"
DEFAULT_SCAN_INTERVAL: Final = 3600
MIN_SCAN_INTERVAL: Final = 300
MAX_SCAN_INTERVAL: Final = 86400

SELF_UNIQUE_ID: Final = "self"

EMPTY_VALUES: Final = (None, "", "-")
