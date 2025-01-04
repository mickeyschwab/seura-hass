"""The Seura TV integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    Platform,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from seura import SeuraClient, SeuraError

_LOGGER = logging.getLogger(__name__)

DOMAIN = "seura"
DEFAULT_NAME = "Seura TV"

PLATFORMS = [Platform.MEDIA_PLAYER, Platform.REMOTE]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Seura TV from a config entry."""
    host = entry.data[CONF_HOST]

    try:
        client = SeuraClient(ip_address=host)
        # Test the connection
        await hass.async_add_executor_job(client.query_power)
    except SeuraError as err:
        _LOGGER.error("Could not connect to Seura TV at %s: %s", host, err)
        return False

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
