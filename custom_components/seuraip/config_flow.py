"""Config flow for Seura TV integration."""
from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from seura import SeuraClient, SeuraError

_LOGGER = logging.getLogger(__name__)

DOMAIN = "seura"


class SeuraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Seura TV."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                client = SeuraClient(user_input[CONF_HOST])
                # Test connection
                client.get_power()

                # Create unique ID from host
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )

            except SeuraError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_NAME, default="Seura TV"): str,
                }
            ),
            errors=errors,
        ) 