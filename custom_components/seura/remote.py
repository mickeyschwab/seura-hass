"""Support for Seura TV remote control."""
from __future__ import annotations

import logging
from typing import Any, Iterable

from homeassistant.components.remote import (
    RemoteEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from seura import SeuraClient

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Seura remote."""
    host = entry.data[CONF_HOST]
    name = entry.data[CONF_NAME]

    async_add_entities([SeuraRemote(host, name)], True)


class SeuraRemote(RemoteEntity):
    """Representation of a Seura Remote."""

    _attr_has_entity_name = True

    def __init__(self, host: str, name: str) -> None:
        """Initialize the Seura Remote."""
        self._host = host
        self._attr_name = f"{name} Remote"
        self._attr_unique_id = f"{name.lower().replace(' ', '_')}_remote"
        self._client = SeuraClient(ip_address=host)

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the remote on."""
        self._client.power_on()

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the remote off."""
        self._client.power_off()

    def send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send commands to a device.
        
        This method handles both button commands and numeric input.
        Commands should be strings, either button names or numbers.
        """
        try:
            for cmd in command:
                if cmd.isdigit():
                    self._client.remote_number(int(cmd))
                else:
                    self._client.remote_button(cmd)
        except Exception as err:
            _LOGGER.error("Error sending command %s: %s", command, err) 