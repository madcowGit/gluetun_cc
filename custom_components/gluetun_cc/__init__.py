from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault("gluetun", {})
    hass.data["gluetun"][entry.entry_id] = {
        "instance_name": entry.data.get("instance_name", "gluetun")
    }
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data["gluetun"].pop(entry.entry_id, None)
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")