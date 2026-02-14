from typing import Any
from homeassistant import config_entries
from .const import DOMAIN  # or from . import DOMAIN if you define it in __init__.py

class GluetunCcConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Gluetun CC."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # validate here if you need to
            return self.async_create_entry(
                title="Gluetun",  # what will show in UI
                data=user_input,  # store connection details for your component
            )

        # IMPORTANT: The step_id must correspond to an async_step_<step_id> method.
        return self.async_show_form(
            step_id="user",
            data_schema=...  # voluptuous schema for host/port etc.
            # errors=errors
        )