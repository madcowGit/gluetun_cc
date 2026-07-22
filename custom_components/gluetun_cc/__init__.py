from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, CONF_INSTANCE_NAME, CONF_API_KEY, PLATFORMS


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    instance_name = entry.data.get(CONF_INSTANCE_NAME, "gluetun")
    api_key = entry.data.get(CONF_API_KEY, "")
    hass.data[DOMAIN][entry.entry_id] = {
        "instance_name": instance_name,
        "api_key": api_key,
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data[DOMAIN].pop(entry.entry_id, None)
    unload_ok = all(
        await hass.config_entries.async_forward_entry_unload(entry, platform)
        for platform in PLATFORMS
    )
    return unload_ok
