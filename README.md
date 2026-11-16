# Gluetun for Home Assistant

A custom Home Assistant integration for monitoring and controlling a [Gluetun](https://github.com/qdm12/gluetun) instance through its HTTP Control Server.

## Features

- VPN status sensor.
- Public IP, region, country, city, location, organization, postal code, and timezone sensors.
- Approximate VPN geolocation device tracker when Gluetun returns valid coordinates.
- Switch to start or stop the VPN using the Control Server API.
- Multiple Gluetun instances with separately configurable URLs and optional API keys.
- Automatic polling and recovery when the Control Server is temporarily unavailable.

## Requirements

- Gluetun with the HTTP Control Server enabled.
- The Control Server URL must be reachable from Home Assistant (for example, `http://gluetun:8000`).
- Configure authentication in Gluetun when exposing the Control Server beyond a trusted network. The integration sends the optional API key in the `X-API-Key` header.

> The HTTP Control Server is a privileged control interface. Do not expose it directly to the internet; use a trusted network and appropriate authentication.

## Installation

### HACS

1. In HACS, open **Integrations** and select **Custom repositories** from the menu.
2. Add `https://github.com/madcowGit/gluetun_cc` with type **Integration**.
3. Install **Gluetun** and restart Home Assistant.

### Manual

Copy `custom_components/gluetun_cc/` into your Home Assistant `config/custom_components/` directory, then restart Home Assistant.

## Configuration

1. Go to **Settings → Devices & services → Add integration** and search for **Gluetun**.
2. Enter an instance name, the HTTP Control Server URL, and optionally the API key and a display name.
3. The integration checks the URL and credentials against `/v1/vpn/status` before saving.
4. Change the connection details later using **Configure** on the integration entry.

The default URL is `http://localhost:8111`. Use the host and port that Home Assistant can reach, not necessarily the address used by the Gluetun container itself.

## Entities

Entities are grouped under a Gluetun device. Status updates every minute; public IP and geolocation data update every five minutes. If a response field is missing, its sensor has no value. The location tracker uses coordinates only when the server provides valid latitude/longitude values.

The VPN switch calls `PUT /v1/vpn/status` with `{"status":"running"}` or `{"status":"stopped"}`. This requires a Control Server configuration that permits changing the VPN status. A failed request raises a Home Assistant action error instead of silently appearing successful.

## Acknowledgments

Thanks to [qdm12](https://github.com/qdm12) for the Gluetun project.

## License

Apache License 2.0. See [LICENSE](LICENSE).
