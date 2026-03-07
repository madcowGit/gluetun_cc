"""Config flow for the Gluetun integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlowWithReload
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_BASE_URL, DEFAULT_BASE_URL, DEFAULT_NAME, DOMAIN


def _build_base_url_schema(default_base_url: str) -> vol.Schema:
    """Build the schema for the base URL form."""
    return vol.Schema(
        {
            vol.Required(CONF_BASE_URL, default=default_base_url): str,
        }
    )


class GluetunConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gluetun."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> GluetunOptionsFlow:
        """Return the options flow for this handler."""
        return GluetunOptionsFlow()

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title=DEFAULT_NAME, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_build_base_url_schema(DEFAULT_BASE_URL),
        )


class GluetunOptionsFlow(OptionsFlowWithReload):
    """Handle options for the Gluetun integration."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the integration options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_base_url = str(
            self.config_entry.options.get(
                CONF_BASE_URL,
                self.config_entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL),
            )
        )

        return self.async_show_form(
            step_id="init",
            data_schema=_build_base_url_schema(current_base_url),
        )
