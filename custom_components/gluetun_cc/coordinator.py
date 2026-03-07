"""Data update coordinators for the Gluetun integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any
from urllib.parse import urljoin

from aiohttp import ClientError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import PUBLIC_IP_SCAN_INTERVAL_SECONDS, STATUS_SCAN_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)


class _GluetunCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Base coordinator for Gluetun API endpoints."""

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        name: str,
        url: str,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator."""
        self.url = url
        self.session = async_get_clientsession(hass)
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch and parse JSON data from the configured endpoint."""
        try:
            async with self.session.get(self.url) as response:
                response.raise_for_status()
                data = await response.json(content_type=None)
        except ClientError as err:
            raise UpdateFailed(f"Error fetching {self.name}: {err}") from err
        except ValueError as err:
            raise UpdateFailed(f"Invalid JSON response from {self.name}") from err

        if not isinstance(data, dict):
            raise UpdateFailed(
                f"Unexpected response type from {self.name}: {type(data).__name__}"
            )

        return data


class GluetunStatusCoordinator(_GluetunCoordinator):
    """Coordinator for the OpenVPN status endpoint."""

    def __init__(self, hass: HomeAssistant, base_url: str) -> None:
        """Initialize the status coordinator."""
        self.base_url = base_url.rstrip("/")
        super().__init__(
            hass,
            name="gluetun_status",
            url=urljoin(self.base_url, "/v1/openvpn/status"),
            update_interval=timedelta(seconds=STATUS_SCAN_INTERVAL_SECONDS),
        )

    @property
    def vpn_status(self) -> str | None:
        """Return the current VPN status."""
        if not self.data:
            return None
        return self.data.get("status")

    async def set_vpn_status(self, status: str) -> None:
        """Set the VPN status."""
        url = urljoin(self.base_url, "/v1/vpn/status")
        payload = {"status": status}

        try:
            async with self.session.put(url, json=payload) as response:
                response.raise_for_status()
        except ClientError as err:
            raise UpdateFailed(f"Error setting VPN status: {err}") from err

        await self.async_request_refresh()


class GluetunPublicIPCoordinator(_GluetunCoordinator):
    """Coordinator for the public IP endpoint."""

    def __init__(self, hass: HomeAssistant, base_url: str) -> None:
        """Initialize the public IP coordinator."""
        super().__init__(
            hass,
            name="gluetun_public_ip",
            url=urljoin(base_url.rstrip("/"), "/v1/publicip/ip"),
            update_interval=timedelta(seconds=PUBLIC_IP_SCAN_INTERVAL_SECONDS),
        )