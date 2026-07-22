from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from datetime import timedelta
import aiohttp
import logging
import json
from urllib.parse import urljoin

from .const import DOMAIN, CONF_INSTANCE_NAME, CONF_BASE_URL, CONF_API_KEY, CONF_TUNNEL_NAME

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    instance_name = entry.data.get(CONF_INSTANCE_NAME, "gluetun")
    base_url = entry.data.get(CONF_BASE_URL, "http://localhost:8111")
    api_key = entry.data.get(CONF_API_KEY, "")
    tunnel_name = entry.data.get(CONF_TUNNEL_NAME, "")
    display_name = tunnel_name if tunnel_name else instance_name

    status_url = urljoin(base_url, "/v1/vpn/status")
    public_ip_url = urljoin(base_url, "/v1/publicip/ip")

    status_coordinator = GluetunStatusCoordinator(hass, status_url, instance_name, api_key)
    public_ip_coordinator = GluetunPublicIPCoordinator(hass, public_ip_url, instance_name, api_key)

    hass.data[DOMAIN][entry.entry_id]["status_coordinator"] = status_coordinator

    await status_coordinator.async_refresh()
    await public_ip_coordinator.async_refresh()

    async_add_entities([
        GluetunStatusSensor(status_coordinator, display_name),
        GluetunPublicIPSensor(public_ip_coordinator, "public_ip", display_name),
        GluetunPublicIPSensor(public_ip_coordinator, "region", display_name),
        GluetunPublicIPSensor(public_ip_coordinator, "country", display_name),
        GluetunPublicIPSensor(public_ip_coordinator, "city", display_name),
        GluetunPublicIPSensor(public_ip_coordinator, "location", display_name),
        GluetunPublicIPSensor(public_ip_coordinator, "organization", display_name),
        GluetunPublicIPSensor(public_ip_coordinator, "postal_code", display_name),
        GluetunPublicIPSensor(public_ip_coordinator, "timezone", display_name),
    ])


class GluetunStatusCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, url, instance_name="gluetun", api_key=""):
        self.url = url
        self.instance_name = instance_name
        self.api_key = api_key
        super().__init__(
            hass,
            _LOGGER,
            name=f"gluetun_status_{instance_name}",
            update_interval=timedelta(seconds=60),
        )

    async def _async_update_data(self):
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, headers=headers) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching status: {response.status}")
                text = await response.text()
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    raise UpdateFailed("Invalid JSON response")
                return data


class GluetunPublicIPCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, url, instance_name="gluetun", api_key=""):
        self.url = url
        self.instance_name = instance_name
        self.api_key = api_key
        super().__init__(
            hass,
            _LOGGER,
            name=f"gluetun_public_ip_{instance_name}",
            update_interval=timedelta(seconds=300),
        )

    async def _async_update_data(self):
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, headers=headers) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching public IP: {response.status}")
                text = await response.text()
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    raise UpdateFailed("Invalid JSON response")
                return data


class GluetunStatusSensor(SensorEntity):
    def __init__(self, coordinator, display_name="gluetun"):
        self.coordinator = coordinator
        self.instance_name = display_name
        self._attr_name = f"Gluetun {display_name} Status"
        self._attr_unique_id = f"gluetun_{display_name}_status_sensor"

    @property
    def state(self):
        data = self.coordinator.data
        if isinstance(data, dict):
            return data.get("status", "unknown")
        return "unknown"

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )


class GluetunPublicIPSensor(SensorEntity):
    def __init__(self, coordinator, key, display_name="gluetun"):
        self.coordinator = coordinator
        self.key = key
        self.instance_name = display_name
        self._attr_name = f"Gluetun {display_name} {key.replace('_', ' ').title()}"
        self._attr_unique_id = f"gluetun_{display_name}_{key}_sensor"

    @property
    def state(self):
        data = self.coordinator.data
        if isinstance(data, dict):
            return data.get(self.key, "unknown")
        return "unknown"

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
