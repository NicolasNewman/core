"""Support for the RemoteTTS text-to-speech service."""

from __future__ import annotations

import logging
from typing import Any

from ha_remote_tts import ApiError

from homeassistant.components.tts import TextToSpeechEntity, TtsAudioType, Voice
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import RemoteTTSConfigEntry
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: RemoteTTSConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up RemoteTTS tts platform via config entry."""
    async_add_entities(
        [
            RemoteTTSTTSEntity(
                config_entry,
            )
        ]
    )


class RemoteTTSTTSEntity(TextToSpeechEntity):
    """The RemoteTTS API entity."""

    def __init__(self, config_entry: RemoteTTSConfigEntry) -> None:
        """Init RemoteTTS TTS service."""
        self._client = config_entry.runtime_data.client
        self._name = config_entry.runtime_data.name
        self._url = config_entry.runtime_data.url
        self._voices = [Voice(name=self._name, voice_id=self._name)]
        self._attr_unique_id = config_entry.entry_id
        self._attr_name = self._name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            manufacturer="RemoteTTS",
            model=self._name,
            entry_type=DeviceEntryType.SERVICE,
        )
        self._attr_supported_languages = [config_entry.runtime_data.language]
        self._attr_default_language = self.supported_languages[0]

    def async_get_supported_voices(self, language: str) -> list[Voice]:
        """Return a list of supported voices for a language."""
        return self._voices

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any]
    ) -> TtsAudioType:
        """Load tts audio file from the engine."""
        if not self._client:
            _LOGGER.warning("The remote-tts client is not running")
            raise HomeAssistantError("The remote-tts client is not running")
        _LOGGER.debug("Getting TTS audio for %s", message)
        _LOGGER.debug("Options: %s", options)

        try:
            audio_format, audio = await self._client.synthesize(message)
        except ApiError as err:
            _LOGGER.warning("Error during processing of TTS request %s", err)
            raise HomeAssistantError(err) from err

        return audio_format, audio
