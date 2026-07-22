from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import aiohttp
import logging

from .const import DOMAIN, CONF_INSTANCE_NAME, CONF_BASE_URL, CONF_API_KEY, CONF_TUNNEL_NAME

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    instance_name = entry.data.get(CONF_INSTANCE_NAME, "gluetun")
    base_url = entry.data.get(CONF_BASE_URL, "http://localhost:8111")
    api_key = entry.data.get(CONF_API_KEY, "")
    tunnel_name = entry.data.get(CONF_TUNNEL_NAME, "")
    display_name = tunnel_name if tunnel_name else instance_name

    coordinator = hass.data[DOMAIN][entry.entry_id].get("status_coordinator")

    if coordinator is None:
        _LOGGER.warning("Status coordinator not available for switch, skipping")
        return

    async_add_entities([
        GluetunSwitch(coordinator, display_name, base_url, api_key),
    ])


class GluetunSwitch(SwitchEntity):
    def __init__(self, coordinator, display_name, base_url, api_key):
        self.coordinator = coordinator
        self.instance_name = display_name
        self.base_url = base_url
        self.api_key = api_key
        self._attr_name = f"Gluetun {display_name} VPN"
        self._attr_unique_id = f"gluetun_{display_name}_switch"
        self._attr_icon = "mdi:vpn"

    @property
    def is_on(self):
        data = self.coordinator.data
        if isinstance(data, dict):
            return data.get("status") == "running"
        return False

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if isinstance(data, dict):
            return {"status": data.get("status", "unknown")}
        return {"status": "unknown"}

    async def async_turn_on(self, **kwargs):
        await self._set_vpn_status("running")

    async def async_turn_off(self, **kwargs):
        await self._set_vpn_status("stopped")

    async def _set_vpn_status(self, status):
        url = f"{self.base_url.rstrip('/')}/v1/vpn/status"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        payload = {"status": status}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        _LOGGER.error(
                            "Failed to set VPN status to %s: HTTP %s",
                            status,
                            response.status,
                        )
                        return
            await self.coordinator.async_request_refresh()
        except aiohttp.ClientError as err:
            _LOGGER.error("Error setting VPN status to %s: %s", status, err)

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
