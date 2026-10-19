# IP2Location.io for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacs-badge]][hacs]

A Home Assistant custom integration that displays geolocation information for an IP address using the [IP2Location.io](https://www.ip2location.io/) web service.

Point it at any IPv4 or IPv6 address, or let it geolocate the public IP of your Home Assistant host. The result is exposed as sensors, a proxy binary sensor and a device tracker that shows up on the Home Assistant map.

## Features

- Country, region, city, ZIP code, latitude, longitude and time zone.
- Network data: ASN, AS name, ISP, domain, connection type and usage type.
- Proxy / VPN / Tor detection as a diagnostic binary sensor.
- A device tracker so the location appears on the built-in map card.
- Works with **no API key** (anonymous limit of 1,000 queries per day) or with a free API key (50,000 queries per month).
- Configurable polling interval, UI setup, no YAML required.

## Installation

### HACS (recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ip2location&repository=home-assistant-ip2location&category=integration)

1. Open HACS in Home Assistant.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Paste `https://github.com/ip2location/home-assistant-ip2location` and select the category **Integration**.
4. Search for **IP2Location.io** in HACS and install it.
5. Restart Home Assistant.

### Manual

Copy the `custom_components/ip2location_io` directory into the `config/custom_components/` directory of your Home Assistant installation and restart Home Assistant.

## Configuration

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ip2location_io)

1. Go to **Settings** → **Devices & services**.
2. Click **Add integration** and search for **IP2Location.io**.
3. Fill in the form:

| Field | Required | Description |
| --- | --- | --- |
| Name | No | Device name shown in Home Assistant. Defaults to `IP2Location.io (<ip>)`. |
| API key | No | A key from [ip2location.io](https://www.ip2location.io/sign-up). Without one the anonymous limit of 1,000 queries per day applies. |
| IP address | No | An IPv4 or IPv6 address to geolocate. Empty means the public IP of your Home Assistant host. |

The IP address is fixed once the entry is created. To look up a different address, add another integration entry.

### Options

**Settings** → **Devices & services** → **IP2Location.io** → **Configure** lets you change the API key and the polling interval (300–86400 seconds, default 3600).

Polling the API less often is a good idea for a value that rarely changes: an IP's city is stable for months, and every poll consumes quota.

## Entities

The entities that are created depend on the API plan the key belongs to. Fields a plan does not return are skipped, so a free key produces the core location sensors only.

| Entity | Type | Notes |
| --- | --- | --- |
| `sensor.<device>_ip_address` | sensor | Diagnostic |
| `sensor.<device>_country` | sensor | Country name |
| `sensor.<device>_country_code` | sensor | ISO 3166 alpha-2 |
| `sensor.<device>_region` | sensor | Region / state |
| `sensor.<device>_city` | sensor | City |
| `sensor.<device>_zip_code` | sensor | Diagnostic |
| `sensor.<device>_latitude` | sensor | Diagnostic |
| `sensor.<device>_longitude` | sensor | Diagnostic |
| `sensor.<device>_time_zone` | sensor | UTC offset, e.g. `-07:00` |
| `sensor.<device>_asn` | sensor | Diagnostic |
| `sensor.<device>_as_name` | sensor | Diagnostic |
| `sensor.<device>_isp` | sensor | Starter plan and above |
| `sensor.<device>_domain` | sensor | Starter plan and above |
| `sensor.<device>_net_speed` | sensor | Starter plan and above |
| `sensor.<device>_elevation` | sensor | Starter plan and above, in metres |
| `sensor.<device>_usage_type` | sensor | Starter plan and above |
| `sensor.<device>_address_type` | sensor | Plus plan and above |
| `sensor.<device>_mcc`, `_mnc`, `_mobile_brand` | sensor | Plus plan and above |
| `binary_sensor.<device>_proxy` | binary_sensor | Problem class: on when the IP is a proxy / VPN / Tor |
| `device_tracker.<device>_location` | device_tracker | Shows the location on the map |

## Example dashboard

A map card with the tracked location:

```yaml
type: map
entities:
  - device_tracker.ip2location_io_203_0_113_5_location
```

A glance at the location, or a single template with everything:

```yaml
type: entities
title: IP2Location.io
entities:
  - entity: sensor.ip2location_io_203_0_113_5_country
  - entity: sensor.ip2location_io_203_0_113_5_region
  - entity: sensor.ip2location_io_203_0_113_5_city
  - entity: sensor.ip2location_io_203_0_113_5_isp
  - entity: binary_sensor.ip2location_io_203_0_113_5_proxy
```

### Automation example

Notify when the geolocated IP is suddenly behind a proxy:

```yaml
alias: IP2Location.io - IP behind a proxy
triggers:
  - trigger: state
    entity_id: binary_sensor.ip2location_io_203_0_113_5_proxy
    to: "on"
actions:
  - action: notify.persistent_notification
    data:
      title: IP2Location.io
      message: >-
        The tracked IP is now reported as a proxy or VPN.
```

## Notes on the API

- The endpoint is `https://api.ip2location.io/`. The API key is sent as an `Authorization: Bearer` header.
- Anonymous requests (no key) are limited to 1,000 queries per day, resetting at 00:00 UTC. A free key raises this to 50,000 queries per month.
- The free plan returns `ip`, `country_code`, `country_name`, `region_name`, `city_name`, `latitude`, `longitude`, `zip_code`, `time_zone`, `asn`, `as` and `is_proxy`. Higher plans add the network, mobile and proxy fields listed above.
- Error responses look like `{"error": {"error_code": 401, "error_message": "..."}}`. A `401` is reported as an authentication failure and triggers re-authentication; a `429` is reported as a rate limit.

## Troubleshooting

| Symptom | Cause |
| --- | --- |
| `invalid_auth` | The API key is wrong or has been revoked. Re-enter it in the options. |
| `rate_limit` | The daily or monthly quota is used up. Add an API key or increase the update interval. |
| `cannot_connect` | Home Assistant could not reach `api.ip2location.io`. Check DNS and outbound HTTPS. |
| Only a few sensors appear | The API key's plan does not return the other fields. |

Enable debug logging to see the raw requests:

```yaml
logger:
  logs:
    custom_components.ip2location_io: debug
```

## Publishing

Maintainer notes for releasing and for submitting this repository to the HACS default store are in [docs/HACS_PUBLISHING.md](docs/HACS_PUBLISHING.md).

## Contributing

Issues and pull requests are welcome at <https://github.com/ip2location/home-assistant-ip2location>.

## License

[MIT](LICENSE)

[releases]: https://github.com/ip2location/home-assistant-ip2location/releases
[releases-shield]: https://img.shields.io/github/release/ip2location/home-assistant-ip2location.svg
[commits]: https://github.com/ip2location/home-assistant-ip2location/commits/main
[commits-shield]: https://img.shields.io/github/commit-activity/y/ip2location/home-assistant-ip2location.svg
[license-shield]: https://img.shields.io/github/license/ip2location/home-assistant-ip2location.svg
[hacs]: https://github.com/hacs/integration
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg
