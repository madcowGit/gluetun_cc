"""The Gluetun integration."""

from __future__ import annotations

import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_API_KEY,
    CONF_BASE_URL,
    CONF_INSTANCE_NAME,
    CONF_TUNNEL_NAME,
    DEFAULT_BASE_URL,
    DEFAULT_INSTANCE_NAME,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import GluetunCoordinator, GluetunPublicIpCoordinator


def _entry_settings(entry: ConfigEntry) -> tuple[str, str, str, str]:
    """Return normalized settings from a config entry, including legacy entries."""
    data = entry.data
    instance_name = data.get(CONF_INSTANCE_NAME, DEFAULT_INSTANCE_NAME)
    base_url = data.get(CONF_BASE_URL, DEFAULT_BASE_URL).rstrip("/")
    api_key = data.get(CONF_API_KEY, "")
    tunnel_name = data.get(CONF_TUNNEL_NAME, "")
    return instance_name, base_url, api_key, tunnel_name


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Gluetun from a config entry."""
    instance_name, base_url, api_key, tunnel_name = _entry_settings(entry)
    hass.data.setdefault(DOMAIN, {})

    status_coordinator = GluetunCoordinator(
        hass, base_url, instance_name, api_key
    )
    public_ip_coordinator = GluetunPublicIpCoordinator(
        hass, base_url, instance_name, api_key
    )
    hass.data[DOMAIN][entry.entry_id] = {
        "instance_name": instance_name,
        "base_url": base_url,
        "api_key": api_key,
        "tunnel_name": tunnel_name,
        "status_coordinator": status_coordinator,
        "public_ip_coordinator": public_ip_coordinator,
    }

    # Let the integration load if Gluetun is temporarily offline. The coordinators
    # keep retrying and entities become available when the server responds again.
    await asyncio.gather(
        status_coordinator.async_refresh(),
        public_ip_coordinator.async_refresh(),
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and its platforms."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
