"""The Gluetun integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_BASE_URL, DEFAULT_BASE_URL, DOMAIN, PLATFORMS
from .coordinator import GluetunPublicIPCoordinator, GluetunStatusCoordinator


type GluetunConfigEntry = ConfigEntry[dict[str, object]]


async def async_setup_entry(hass: HomeAssistant, entry: GluetunConfigEntry) -> bool:
    """Set up Gluetun from a config entry."""
    base_url = str(entry.options.get(CONF_BASE_URL, entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL)))

    status_coordinator = GluetunStatusCoordinator(hass, base_url)
    public_ip_coordinator = GluetunPublicIPCoordinator(hass, base_url)

    await status_coordinator.async_config_entry_first_refresh()
    await public_ip_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "status": status_coordinator,
        "public_ip": public_ip_coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: GluetunConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
