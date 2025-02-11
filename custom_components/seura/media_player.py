"""Support for Seura TVs."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from seura import SeuraClient
from seura.config import INPUT_MAP

_LOGGER = logging.getLogger(__name__)

SUPPORTED_FEATURES = (
    MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.SELECT_SOURCE
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Seura TV from a config entry."""
    host = entry.data[CONF_HOST]
    name = entry.data[CONF_NAME]

    async_add_entities([SeuraTV(host, name)], update_before_add=True)


class SeuraTV(MediaPlayerEntity):
    """Representation of a Seura TV."""

    def __init__(self, host: str, name: str) -> None:
        """Initialize the Seura TV device."""
        self._attr_unique_id = name.lower().replace(' ', '_')
        self._host = host
        self._name = name
        self._state = MediaPlayerState.OFF
        self._volume = 0
        self._muted = False
        self._source = None
        self._source_list = []
        self._client = SeuraClient(host=host)

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return self._name

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the device."""
        return self._state

    @property
    def volume_level(self) -> float | None:
        """Volume level of the media player (0..100)."""
        return self._volume

    @property
    def is_volume_muted(self) -> bool:
        """Boolean if volume is currently muted."""
        return self._muted

    @property
    def source(self) -> str | None:
        """Return the current input source."""
        return self._source

    @property
    def source_list(self) -> list[str]:
        """List of available input sources."""
        return self._source_list

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Flag media player features that are supported."""
        return SUPPORTED_FEATURES

    def update(self) -> None:
        """Fetch state from the device."""
        try:
            power_state = self._client.query_power()
            self._state = (
                MediaPlayerState.ON if power_state == "ON" else MediaPlayerState.OFF
            )

            if self._state == MediaPlayerState.ON:
                self._volume = self._client.query_volume() / 100
                self._muted = self._volume == 0
                self._source = self._client.query_input()
                self._source_list = list(INPUT_MAP.keys())
        except Exception as err:
            _LOGGER.error("Error updating Seura TV state: %s", err)
            self._state = MediaPlayerState.OFF

    def turn_on(self) -> None:
        """Turn the media player on."""
        self._client.power_on()

    def turn_off(self) -> None:
        """Turn the media player off."""
        self._client.power_off()

    def volume_up(self) -> None:
        """Volume up the media player."""
        self._client.volume_up()
        self._volume += 0.01

    def volume_down(self) -> None:
        """Volume down the media player."""
        self._client.volume_down()
        self._volume -= 0.01

    def set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        _LOGGER.info("Setting volume level to %s", int(volume * 100))
        self._client.set_volume(int(volume * 100))
        self._volume = volume

    def mute_volume(self, mute: bool) -> None:
        """Mute (true) or unmute (false) media player."""
        self._client.send_command("MUTE")
        self._muted = mute

    def select_source(self, source: str) -> None:
        """Select input source."""
        self._client.set_input(source)
        self._source = source
