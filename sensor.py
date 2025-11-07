
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from datetime import timedelta
import aiohttp
import logging
import json
from urllib.parse import urljoin

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    base_url = entry.data.get("base_url", "http://localhost:8111")

    status_url = urljoin(base_url, "/v1/openvpn/status")
    public_ip_url = urljoin(base_url, "/v1/publicip/ip")

    status_coordinator = GluetunStatusCoordinator(hass, status_url)
    public_ip_coordinator = GluetunPublicIPCoordinator(hass, public_ip_url)

    await status_coordinator.async_refresh()
    await public_ip_coordinator.async_refresh()

    async_add_entities([
        GluetunStatusSensor(status_coordinator),
        GluetunPublicIPSensor(public_ip_coordinator, "public_ip"),
        GluetunPublicIPSensor(public_ip_coordinator, "country"),
    ])

class GluetunStatusCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, url):
        self.url = url
        super().__init__(
            hass,
            _LOGGER,
            name="gluetun_status",
            update_interval=timedelta(seconds=60),
        )

    async def _async_update_data(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching status: {response.status}")
                text = await response.text()
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    raise UpdateFailed("Invalid JSON response")
                return data

class GluetunPublicIPCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, url):
        self.url = url
        super().__init__(
            hass,
            _LOGGER,
            name="gluetun_public_ip",
            update_interval=timedelta(seconds=300),
        )

    async def _async_update_data(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching public IP: {response.status}")
                text = await response.text()
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    raise UpdateFailed("Invalid JSON response")
                return data

class GluetunStatusSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "Gluetun Status"
        self._attr_unique_id = "gluetun_status_sensor"

    @property
    def state(self):
        data = self.coordinator.data
        if isinstance(data, dict):
            return data.get("status", "unknown")
        return "unknown"

class GluetunPublicIPSensor(SensorEntity):
    def __init__(self, coordinator, key):
        self.coordinator = coordinator
        self.key = key
        self._attr_name = f"Gluetun {key.replace('_', ' ').title()}"
        self._attr_unique_id = f"gluetun_{key}_sensor"

    @property
    def state(self):
        data = self.coordinator.data
        if isinstance(data, dict):
            return data.get(self.key, "unknown")
        return "unknown"
