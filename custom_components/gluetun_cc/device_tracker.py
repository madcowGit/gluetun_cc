"""Device tracker for Gluetun's public IP geolocation."""

from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import _entry_settings
from .const import DOMAIN
from .coordinator import GluetunPublicIpCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up the Gluetun location tracker."""
    instance_name, _, _, tunnel_name = _entry_settings(entry)
    display_name = tunnel_name or instance_name
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: GluetunPublicIpCoordinator = data["public_ip_coordinator"]
    async_add_entities(
        [
            GluetunTrackerEntity(
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


class GluetunTrackerEntity(
    CoordinatorEntity[GluetunPublicIpCoordinator], TrackerEntity
):
    """Represent the VPN's approximate public geolocation."""

    _attr_icon = "mdi:vpn"

    def __init__(
        self,
        coordinator: GluetunPublicIpCoordinator,
        display_name: str,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator)
        self._attr_name = f"Gluetun {display_name} VPN location"
        self._attr_unique_id = f"gluetun_{display_name}_tracker"
        self._attr_device_info = device_info

    @property
    def source_type(self) -> SourceType:
        """Return the source type for this tracker."""
        return SourceType.GPS

    def _coordinates(self) -> tuple[float, float] | None:
        """Parse and validate latitude and longitude from Gluetun's location field."""
        location = self.coordinator.data.get("location")
        if not isinstance(location, str):
            return None
        try:
            latitude_text, longitude_text = location.split(",", maxsplit=1)
            latitude, longitude = (
                float(latitude_text.strip()),
                float(longitude_text.strip()),
            )
        except (ValueError, TypeError):
            return None
        if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
            return None
        return latitude, longitude

    @property
    def latitude(self) -> float | None:
        """Return latitude when Gluetun provides valid coordinates."""
        coordinates = self._coordinates()
        return coordinates[0] if coordinates else None

    @property
    def longitude(self) -> float | None:
        """Return longitude when Gluetun provides valid coordinates."""
        coordinates = self._coordinates()
        return coordinates[1] if coordinates else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose public IP and location details as tracker attributes."""
        data = self.coordinator.data
        return {
            key: data.get(key)
            for key in ("public_ip", "city", "country", "region", "organization")
            if data.get(key) is not None
        }
