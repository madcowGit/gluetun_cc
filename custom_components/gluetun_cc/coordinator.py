"""HTTP client and update coordinators for Gluetun."""

from __future__ import annotations

import json
import logging
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    PUBLIC_IP_ENDPOINT,
    PUBLIC_IP_UPDATE_INTERVAL,
    STATUS_UPDATE_INTERVAL,
    VPN_STATUS_ENDPOINT,
)

_LOGGER = logging.getLogger(__name__)


class GluetunApi:
    """Async API client for a Gluetun HTTP Control Server."""

    def __init__(self, hass: HomeAssistant, base_url: str, api_key: str) -> None:
        self._session = async_get_clientsession(hass)
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key

    @property
    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self._api_key:
            headers["X-API-Key"] = self._api_key
        return headers

    async def get_json(self, endpoint: str) -> dict[str, Any]:
        """Request and validate a JSON object from Gluetun."""
        try:
            async with self._session.get(
                f"{self._base_url}{endpoint}",
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status != 200:
                    raise UpdateFailed(
                        f"Gluetun returned HTTP {response.status} for {endpoint}"
                    )
                try:
                    data = json.loads(await response.text())
                except (json.JSONDecodeError, UnicodeDecodeError) as err:
                    raise UpdateFailed("Gluetun returned invalid JSON") from err
                if not isinstance(data, dict):
                    raise UpdateFailed("Gluetun returned an unexpected response")
                return data
        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(f"Unable to connect to Gluetun: {err}") from err

    async def set_vpn_status(self, status: str) -> None:
        """Ask Gluetun to change the VPN status."""
        try:
            async with self._session.put(
                f"{self._base_url}{VPN_STATUS_ENDPOINT}",
                json={"status": status},
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status not in (200, 204):
                    raise HomeAssistantError(
                        f"Gluetun could not set VPN status (HTTP {response.status})"
                    )
        except (aiohttp.ClientError, TimeoutError) as err:
            raise HomeAssistantError("Unable to connect to Gluetun") from err


class GluetunCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll VPN status from Gluetun."""

    def __init__(
        self, hass: HomeAssistant, base_url: str, instance_name: str, api_key: str
    ) -> None:
        self.api = GluetunApi(hass, base_url, api_key)
        super().__init__(
            hass,
            _LOGGER,
            name=f"Gluetun VPN status ({instance_name})",
            update_interval=STATUS_UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch current VPN status."""
        return await self.api.get_json(VPN_STATUS_ENDPOINT)


class GluetunPublicIpCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll public IP and geolocation data from Gluetun."""

    def __init__(
        self, hass: HomeAssistant, base_url: str, instance_name: str, api_key: str
    ) -> None:
        self.api = GluetunApi(hass, base_url, api_key)
        super().__init__(
            hass,
            _LOGGER,
            name=f"Gluetun public IP ({instance_name})",
            update_interval=PUBLIC_IP_UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch current public IP details."""
        return await self.api.get_json(PUBLIC_IP_ENDPOINT)
