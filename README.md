# Gluetun status – Home Assistant custom component

This is a Home Assistant custom integration that reads VPN status information from a [Gluetun](https://github.com/qdm12/gluetun) instance via its **HTTP Control Server**. It exposes sensors for:
- **OpenVPN/WireGuard status** from `/v1/openvpn/status`
- **Public IP address** from `/v1/publicip/ip`
- **Country** (derived from the public IP, via Gluetun)

> Ensure Gluetun’s HTTP Control Server is enabled and reachable from Home Assistant. (These endpoints reflect the project’s existing behavior.)

## Installation

### HACS (as a custom repository)

1. In Home Assistant, open **HACS → Integrations**.  
2. Click **⋯ (three dots)** → **Custom repositories**.  
3. Paste `https://github.com/madcowGit/gluetun_cc` and select **Type: Integration**, then click **Add**.  
4. Back in HACS, search for **Gluetun (custom component)** and click **Install**.  
5. Restart Home Assistant when prompted.

### Manual

Copy the `custom_components/gluetun_cc/` directory into your HA `config/custom_components/` and restart.

## Requirements

- A running **Gluetun** with the **HTTP Control Server** enabled and accessible (e.g., `http://<gluetun-host>:8000`).

## Configuration (UI)

1. Go to **Settings → Devices & services → Add integration** and search for **Gluetun (custom component)**.  
2. Enter the HTTP Control Server details.  
3. Finish the flow; entities for VPN status, public IP, and country (if available) will be created.

## Development & CI

- Standard HA structure under `custom_components/gluetun_cc/`.
- `hacs.json` at repo root for HACS metadata.
- CI includes **HACS Action** and **hassfest** to validate the integration and get ready for default HACS inclusion.

## Releases

After merging changes to `main`, create a **GitHub Release** (e.g., `v0.1.0`) so HACS can present versions nicely. (Default inclusion requires a full release, not just a tag.)

## Acknowledgments

- Thanks to **qdm12** for the Gluetun project.