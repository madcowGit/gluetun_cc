"""Sensor platform for the Gluetun integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import DOMAIN, MANUFACTURER, MODEL


GluetunConfigEntry = ConfigEntry[dict[str, object]]


@dataclass(frozen=True, kw_only=True)
class GluetunSensorEntityDescription(SensorEntityDescription):
    """Describes a Gluetun sensor entity."""

    coordinator_key: str
    value_key: str
    fallback_value: str = "unknown"


SENSORS: tuple[GluetunSensorEntityDescription, ...] = (
    GluetunSensorEntityDescription(
        key="status",
        translation_key="status",
        coordinator_key="status",
        value_key="status",
    ),
    GluetunSensorEntityDescription(
        key="public_ip",
        translation_key="public_ip",
        coordinator_key="public_ip",
        value_key="public_ip",
    ),
    GluetunSensorEntityDescription(
        key="region",
        translation_key="region",
        coordinator_key="public_ip",
        value_key="region",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    GluetunSensorEntityDescription(
        key="country",
        translation_key="country",
        coordinator_key="public_ip",
        value_key="country",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    GluetunSensorEntityDescription(
        key="city",
        translation_key="city",
        coordinator_key="public_ip",
        value_key="city",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    GluetunSensorEntityDescription(
        key="location",
        translation_key="location",
        coordinator_key="public_ip",
        value_key="location",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    GluetunSensorEntityDescription(
        key="organization",
        translation_key="organization",
        coordinator_key="public_ip",
        value_key="organization",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    GluetunSensorEntityDescription(
        key="postal_code",
        translation_key="postal_code",
        coordinator_key="public_ip",
        value_key="postal_code",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    GluetunSensorEntityDescription(
        key="timezone",
        translation_key="timezone",
        coordinator_key="public_ip",
        value_key="timezone",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GluetunConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Gluetun sensor entities."""
    coordinators: dict[str, DataUpdateCoordinator[dict[str, Any]]] = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        GluetunSensor(
            entry=entry,
            coordinator=coordinators[description.coordinator_key],
            description=description,
        )
        for description in SENSORS
    )


class GluetunSensor(CoordinatorEntity[DataUpdateCoordinator[dict[str, Any]]], SensorEntity):
    """Representation of a Gluetun sensor."""

    entity_description: GluetunSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        *,
        entry: GluetunConfigEntry,
        coordinator: DataUpdateCoordinator[dict[str, Any]],
        description: GluetunSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Gluetun",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> str | None:
        """Return the sensor state."""
        value = self.coordinator.data.get(
            self.entity_description.value_key,
            self.entity_description.fallback_value,
        )
        return None if value is None else str(value)