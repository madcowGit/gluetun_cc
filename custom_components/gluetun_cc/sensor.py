"""Sensors for Gluetun VPN status and public IP details."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import _entry_settings
from .const import DOMAIN
from .coordinator import GluetunCoordinator, GluetunPublicIpCoordinator

PUBLIC_IP_SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(key="public_ip", name="Public IP"),
    SensorEntityDescription(key="region", name="Region"),
    SensorEntityDescription(key="country", name="Country"),
    SensorEntityDescription(key="city", name="City"),
    SensorEntityDescription(key="location", name="Location"),
    SensorEntityDescription(key="organization", name="Organization"),
    SensorEntityDescription(key="postal_code", name="Postal code"),
    SensorEntityDescription(key="timezone", name="Timezone"),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Gluetun sensors."""
    instance_name, _, _, tunnel_name = _entry_settings(entry)
    display_name = tunnel_name or instance_name
    data = hass.data[DOMAIN][entry.entry_id]
    status_coordinator: GluetunCoordinator = data["status_coordinator"]
    ip_coordinator: GluetunPublicIpCoordinator = data["public_ip_coordinator"]
    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=display_name,
        manufacturer="Gluetun",
        configuration_url=data["base_url"],
    )

    async_add_entities(
        [
            GluetunStatusSensor(status_coordinator, display_name, device_info),
            *(
                GluetunPublicIpSensor(ip_coordinator, description, display_name, device_info)
                for description in PUBLIC_IP_SENSORS
            ),
        ]
    )


class GluetunStatusSensor(CoordinatorEntity[GluetunCoordinator], SensorEntity):
    """Expose the VPN status as a sensor."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: GluetunCoordinator,
        display_name: str,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = SensorEntityDescription(
            key="status", name="VPN status"
        )
        self._attr_name = f"Gluetun {display_name} VPN status"
        self._attr_unique_id = f"gluetun_{display_name}_status_sensor"
        self._attr_device_info = device_info

    @property
    def native_value(self) -> str | None:
        """Return the server's VPN status."""
        value = self.coordinator.data.get("status")
        return str(value) if value is not None else None


class GluetunPublicIpSensor(
    CoordinatorEntity[GluetunPublicIpCoordinator], SensorEntity
):
    """Expose one public IP or geolocation field as a sensor."""

    def __init__(
        self,
        coordinator: GluetunPublicIpCoordinator,
        description: SensorEntityDescription,
        display_name: str,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = f"Gluetun {display_name} {description.name}"
        self._attr_unique_id = f"gluetun_{display_name}_{description.key}_sensor"
        self._attr_device_info = device_info

    @property
    def native_value(self) -> str | None:
        """Return the field's current value, if available."""
        value: Any = self.coordinator.data.get(self.entity_description.key)
        return str(value) if value is not None else None
