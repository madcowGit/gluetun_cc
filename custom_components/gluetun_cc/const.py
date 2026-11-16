"""Constants for the Gluetun integration."""

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "gluetun_cc"

CONF_INSTANCE_NAME = "instance_name"
CONF_BASE_URL = "base_url"
CONF_API_KEY = "api_key"
CONF_TUNNEL_NAME = "tunnel_name"

DEFAULT_BASE_URL = "http://localhost:8111"
DEFAULT_INSTANCE_NAME = "gluetun"

VPN_STATUS_ENDPOINT = "/v1/vpn/status"
PUBLIC_IP_ENDPOINT = "/v1/publicip/ip"

STATUS_UPDATE_INTERVAL = timedelta(seconds=60)
PUBLIC_IP_UPDATE_INTERVAL = timedelta(minutes=5)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.DEVICE_TRACKER, Platform.SWITCH]
