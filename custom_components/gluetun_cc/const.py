"""Constants for the Gluetun integration."""

from __future__ import annotations

DOMAIN = "gluetun_cc"
DEFAULT_NAME = "Gluetun"
DEFAULT_BASE_URL = "http://localhost:8111"
PLATFORMS: list[str] = ["sensor", "button"]

CONF_BASE_URL = "base_url"

COORDINATOR_STATUS = "status"
COORDINATOR_PUBLIC_IP = "public_ip"

STATUS_SCAN_INTERVAL_SECONDS = 60
PUBLIC_IP_SCAN_INTERVAL_SECONDS = 300

MANUFACTURER = "Gluetun"
MODEL = "VPN"
