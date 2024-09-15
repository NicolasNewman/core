"""Reddit Component."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from asyncpraw import Reddit
from asyncpraw.exceptions import PRAWException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_MAXIMUM,
    CONF_PASSWORD,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant

from .const import CONF_SORT_BY, CONF_SUBREDDITS, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


@dataclass
class RedditData:
    """Reddit data type."""

    client: Reddit
    sort_by: str
    subreddits: str
    limit: int


type RedditConfigEntry = ConfigEntry[RedditData]


async def async_setup_entry(hass: HomeAssistant, entry: RedditConfigEntry) -> bool:
    """Set up Reddit from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    try:
        user_agent = f"{entry.data[CONF_USERNAME]}_home_assistant_sensor"
        client = Reddit(
            client_id=entry.data[CONF_CLIENT_ID],
            client_secret=entry.data[CONF_CLIENT_SECRET],
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            user_agent=user_agent,
            check_for_updates=False,
        )
        await client.user.me()

        _LOGGER.debug("Connected to praw")

    except PRAWException as err:
        _LOGGER.error("Reddit error %s", err)
        return False

    hass.data[DOMAIN][entry.entry_id] = RedditData(
        client,
        sort_by=entry.data[CONF_SORT_BY],
        subreddits=entry.data[CONF_SUBREDDITS],
        limit=entry.data[CONF_MAXIMUM],
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: RedditConfigEntry) -> bool:
    """Unload a config entry."""
    reddit_data: RedditData = hass.data[DOMAIN][entry.entry_id]
    await reddit_data.client.close()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
