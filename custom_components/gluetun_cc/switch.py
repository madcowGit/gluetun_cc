"""Switch platform for Gluetun VPN control."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import _entry_settings
from .const import DOMAIN
from .coordinator import GluetunCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up the Gluetun VPN switch."""
    instance_name, _, _, tunnel_name = _entry_settings(entry)
    display_name = tunnel_name or instance_name
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: GluetunCoordinator = data["status_coordinator"]
    async_add_entities(
        [
            GluetunSwitch(
                coordinator,
                display_name,
                DeviceInfo(
                    identifiers={(DOMAIN, entry.entry_id)},
                    name=display_name,
                    manufacturer="Gluetun",
                    configuration_url=data["base_url"],
                ),
            )
        ]
    )


class GluetunSwitch(CoordinatorEntity[GluetunCoordinator], SwitchEntity):
    """Control whether the Gluetun VPN is running."""

    _attr_icon = "mdi:vpn"

    def __init__(
        self,
        coordinator: GluetunCoordinator,
        display_name: str,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator)
        self._attr_name = f"Gluetun {display_name} VPN"
        self._attr_unique_id = f"gluetun_{display_name}_switch"
        self._attr_device_info = device_info

    @property
    def is_on(self) -> bool:
        """Return whether the VPN is running."""
        return self.coordinator.data.get("status") == "running"

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Expose the raw VPN status for diagnostics."""
        status: Any = self.coordinator.data.get("status", "unknown")
        return {"status": str(status)}

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Start the VPN through Gluetun's control API."""
        await self._set_vpn_status("running")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Stop the VPN through Gluetun's control API."""
        await self._set_vpn_status("stopped")

    async def _set_vpn_status(self, status: str) -> None:
        """Update Gluetun and refresh the reported state."""
        try:
            await self.coordinator.api.set_vpn_status(status)
            await self.coordinator.async_request_refresh()
        except HomeAssistantError as err:
            raise HomeAssistantError(f"Unable to set Gluetun VPN status: {err}") from err
