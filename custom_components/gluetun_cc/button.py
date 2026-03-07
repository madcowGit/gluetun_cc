"""Button platform for Gluetun control."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GluetunStatusCoordinator


@dataclass(frozen=True, kw_only=True)
class GluetunButtonEntityDescription(ButtonEntityDescription):
    """Describe a Gluetun button entity."""

    press_status: str
    available_fn: Callable[[GluetunStatusCoordinator], bool]


BUTTONS: Final[tuple[GluetunButtonEntityDescription, ...]] = (
    GluetunButtonEntityDescription(
        key="start_vpn",
        name="Start VPN",
        icon="mdi:play",
        press_status="running",
        available_fn=lambda coordinator: coordinator.vpn_status != "running",
    ),
    GluetunButtonEntityDescription(
        key="stop_vpn",
        name="Stop VPN",
        icon="mdi:stop",
        press_status="stopped",
        available_fn=lambda coordinator: coordinator.vpn_status != "stopped",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Gluetun button entities."""
    coordinator: GluetunStatusCoordinator = hass.data[DOMAIN][entry.entry_id]["status"]

    async_add_entities(
        GluetunButton(coordinator, entry.entry_id, description)
        for description in BUTTONS
    )


class GluetunButton(CoordinatorEntity[GluetunStatusCoordinator], ButtonEntity):
    """Representation of a Gluetun control button."""

    entity_description: GluetunButtonEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GluetunStatusCoordinator,
        entry_id: str,
        description: GluetunButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.entity_description = description
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_{description.key}"

    @property
    def available(self) -> bool:
        """Return availability."""
        return super().available and self.entity_description.available_fn(self.coordinator)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name="Gluetun",
            manufacturer="Gluetun",
            model="VPN",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.set_vpn_status(self.entity_description.press_status)