"""The remotetts integration."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from ha_remote_tts import ApiError, RemoteTTSClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError

from .const import CONF_LANGUAGE, CONF_NAME, CONF_URL

PLATFORMS: list[Platform] = [Platform.TTS]

_LOGGER = logging.getLogger(__name__)


@dataclass(kw_only=True, slots=True)
class RemoteTTSData:
    """RemoteTTS data type."""

    client: RemoteTTSClient | None
    url: str
    name: str
    language: str


type RemoteTTSConfigEntry = ConfigEntry[RemoteTTSData]


async def async_setup_entry(hass: HomeAssistant, entry: RemoteTTSConfigEntry) -> bool:
    """Set up remotetts from a config entry."""

    name = entry.data[CONF_NAME]
    language = entry.data[CONF_LANGUAGE]
    url = entry.data[CONF_URL]

    if name is None:
        raise ConfigEntryError("Name could not be resolved")
    if language is None:
        raise ConfigEntryError("Language could not be resolved")
    if url is None:
        raise ConfigEntryError("Url could not be resolved")

    entry.runtime_data = RemoteTTSData(
        client=None, url=url, language=language, name=name
    )

    try:
        client = RemoteTTSClient(url)
        await client.verify_connection()
        # await client.close()
    except ApiError as err:
        raise ConfigEntryError("Could not connect to API") from err
    except ValueError as err:
        raise ConfigEntryError(err) from err

    entry.runtime_data.client = client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: RemoteTTSConfigEntry) -> bool:
    """Unload a config entry."""
    if entry.runtime_data.client:
        await entry.runtime_data.client.close()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def update_listener(
    hass: HomeAssistant, config_entry: RemoteTTSConfigEntry
) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)
