from homeassistant.components.device_tracker import TrackerEntity, SourceType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from datetime import timedelta
import aiohttp
import logging
import json
from urllib.parse import urljoin

from .const import CONF_INSTANCE_NAME, CONF_BASE_URL, CONF_API_KEY, CONF_TUNNEL_NAME

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    instance_name = entry.data.get(CONF_INSTANCE_NAME, "gluetun")
    base_url = entry.data.get(CONF_BASE_URL, "http://localhost:8111")
    api_key = entry.data.get(CONF_API_KEY, "")
    tunnel_name = entry.data.get(CONF_TUNNEL_NAME, "")
    display_name = tunnel_name if tunnel_name else instance_name

    public_ip_url = urljoin(base_url, "/v1/publicip/ip")
    coordinator = GluetunPublicIPCoordinator(hass, public_ip_url, instance_name, api_key)

    await coordinator.async_refresh()

    async_add_entities([
        GluetunTrackerEntity(coordinator, display_name),
    ])


class GluetunPublicIPCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, url, instance_name="gluetun", api_key=""):
        self.url = url
        self.instance_name = instance_name
        self.api_key = api_key
        super().__init__(
            hass,
            _LOGGER,
            name=f"gluetun_tracker_{instance_name}",
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


class GluetunTrackerEntity(TrackerEntity):
    def __init__(self, coordinator, display_name="gluetun"):
        self.coordinator = coordinator
        self.instance_name = display_name
        self._attr_name = f"Gluetun {display_name} VPN Location"
        self._attr_unique_id = f"gluetun_{display_name}_tracker"
        self._attr_icon = "mdi:vpn"

    @property
    def source_type(self):
        return SourceType.GPS

    @property
    def latitude(self):
        data = self.coordinator.data
        if isinstance(data, dict):
            location = data.get("location")
            if location and isinstance(location, str) and "," in location:
                try:
                    lat, _ = location.split(",", 1)
                    return float(lat)
                except (ValueError, AttributeError):
                    return None
        return None

    @property
    def longitude(self):
        data = self.coordinator.data
        if isinstance(data, dict):
            location = data.get("location")
            if location and isinstance(location, str) and "," in location:
                try:
                    _, lon = location.split(",", 1)
                    return float(lon)
                except (ValueError, AttributeError):
                    return None
        return None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if isinstance(data, dict):
            return {
                "public_ip": data.get("public_ip"),
                "city": data.get("city"),
                "country": data.get("country"),
                "region": data.get("region"),
                "organization": data.get("organization"),
            }
        return {}

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
