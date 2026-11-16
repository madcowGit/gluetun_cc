"""Config flow for Gluetun."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_API_KEY,
    CONF_BASE_URL,
    CONF_INSTANCE_NAME,
    CONF_TUNNEL_NAME,
    DEFAULT_BASE_URL,
    DEFAULT_INSTANCE_NAME,
    DOMAIN,
    VPN_STATUS_ENDPOINT,
)


def _normalize_and_validate_url(value: str) -> str:
    """Normalize a control-server URL and reject malformed or unsafe schemes."""
    url = value.strip().rstrip("/")
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise vol.Invalid("Enter a valid HTTP or HTTPS URL")
    if parsed.username or parsed.password:
        raise vol.Invalid("Do not include credentials in the URL")
    return url


async def _validate_connection(
    hass: HomeAssistant, base_url: str, api_key: str
) -> str | None:
    """Check that the configured Gluetun server responds to its status endpoint."""
    headers = {"Accept": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
    try:
        async with async_get_clientsession(hass).get(
            f"{base_url}{VPN_STATUS_ENDPOINT}",
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=10),
        ) as response:
            if response.status in (401, 403):
                return "invalid_auth"
            if response.status != 200:
                return "cannot_connect"
            try:
                payload = await response.json()
            except (aiohttp.ContentTypeError, ValueError):
                return "invalid_response"
            return None if isinstance(payload, dict) else "invalid_response"
    except (aiohttp.ClientError, TimeoutError):
        return "cannot_connect"


class GluetunConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Gluetun config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            instance_name = user_input[CONF_INSTANCE_NAME].strip()
            api_key = user_input.get(CONF_API_KEY, "").strip()
            tunnel_name = user_input.get(CONF_TUNNEL_NAME, "").strip()
            try:
                base_url = _normalize_and_validate_url(user_input[CONF_BASE_URL])
            except vol.Invalid:
                errors["base"] = "invalid_url"
            else:
                if error := await _validate_connection(self.hass, base_url, api_key):
                    errors["base"] = error
                else:
                    await self.async_set_unique_id(instance_name.casefold())
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"Gluetun - {tunnel_name or instance_name}",
                        data={
                            CONF_INSTANCE_NAME: instance_name,
                            CONF_BASE_URL: base_url,
                            CONF_API_KEY: api_key,
                            CONF_TUNNEL_NAME: tunnel_name,
                        },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_INSTANCE_NAME, default=DEFAULT_INSTANCE_NAME
                    ): str,
                    vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
                    vol.Optional(CONF_API_KEY, default=""): str,
                    vol.Optional(CONF_TUNNEL_NAME, default=""): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Allow an existing entry's server details to be changed."""
        entry = self._get_reconfigure_entry()
        if user_input is not None:
            api_key = user_input.get(CONF_API_KEY, "").strip()
            tunnel_name = user_input.get(CONF_TUNNEL_NAME, "").strip()
            try:
                base_url = _normalize_and_validate_url(user_input[CONF_BASE_URL])
            except vol.Invalid:
                error = "invalid_url"
            else:
                error = await _validate_connection(self.hass, base_url, api_key)

            if error:
                return self.async_show_form(
                    step_id="reconfigure",
                    data_schema=self._reconfigure_schema(entry),
                    errors={"base": error},
                )

            return self.async_update_reload_and_abort(
                entry,
                data_updates={
                    CONF_BASE_URL: base_url,
                    CONF_API_KEY: api_key,
                    CONF_TUNNEL_NAME: tunnel_name,
                },
                title=f"Gluetun - {tunnel_name or entry.data.get(CONF_INSTANCE_NAME, DEFAULT_INSTANCE_NAME)}",
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self._reconfigure_schema(entry),
        )

    @staticmethod
    def _reconfigure_schema(entry: config_entries.ConfigEntry) -> vol.Schema:
        """Build the reconfigure form using the saved settings."""
        return vol.Schema(
            {
                vol.Required(
                    CONF_BASE_URL,
                    default=entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL),
                ): str,
                vol.Optional(
                    CONF_API_KEY, default=entry.data.get(CONF_API_KEY, "")
                ): str,
                vol.Optional(
                    CONF_TUNNEL_NAME, default=entry.data.get(CONF_TUNNEL_NAME, "")
                ): str,
            }
        )
