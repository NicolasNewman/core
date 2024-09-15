"""Config flow for the Reddit integration."""

import logging
from typing import Any

from asyncpraw import Reddit
from asyncpraw.exceptions import PRAWException
from asyncprawcore.exceptions import Redirect, ResponseException
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_MAXIMUM,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_USERNAME,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import CONF_SORT_BY, CONF_SUBREDDITS, DOMAIN, LIST_TYPES

USER_STEP_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default="Reddit"): str,
        vol.Required(CONF_CLIENT_ID): str,
        vol.Required(CONF_CLIENT_SECRET): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

FEED_STEP_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SUBREDDITS, default=[]): SelectSelector(
            SelectSelectorConfig(
                mode=SelectSelectorMode.DROPDOWN,
                multiple=True,
                sort=True,
                custom_value=True,
                options=[],
            )
        ),
        vol.Optional(CONF_SORT_BY, default="hot"): SelectSelector(
            SelectSelectorConfig(
                mode=SelectSelectorMode.DROPDOWN,
                multiple=False,
                sort=True,
                custom_value=False,
                options=LIST_TYPES,
            )
        ),
        vol.Optional(CONF_MAXIMUM, default=10): cv.positive_int,
    }
)


_LOGGER = logging.getLogger(__name__)


class RedditConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Reddit integration."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._auth: dict[str, Any] | None = None
        self._reddit: Reddit | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                user_agent = f"{user_input[CONF_USERNAME]}_home_assistant_sensor"
                self._reddit = Reddit(
                    client_id=user_input[CONF_CLIENT_ID],
                    client_secret=user_input[CONF_CLIENT_SECRET],
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                    user_agent=user_agent,
                    check_for_updates=False,
                )
                await self._reddit.user.me()
            except ResponseException as err:
                if err.response.status == 401:
                    errors["base"] = "unauthorized_response"
                else:
                    errors["base"] = "unknown_response"
            except PRAWException:
                errors["base"] = "praw_response"
            else:
                self._auth = user_input
                return await self.async_step_feed()
        return self.async_show_form(
            step_id="user", data_schema=USER_STEP_SCHEMA, errors=errors
        )

    async def async_step_feed(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        assert self._auth is not None
        assert self._reddit is not None

        if user_input is not None:
            try:
                await self._reddit.subreddit(
                    "+".join(user_input[CONF_SUBREDDITS]), True
                )
            except Redirect:
                errors["base"] = "invalid_subreddit"
            except ValueError:
                errors["base"] = "no_subreddits"
            else:
                await self._reddit.close()
                return self.async_create_entry(
                    title=self._auth[CONF_NAME],
                    data={**self._auth, **user_input},
                )
        return self.async_show_form(
            step_id="feed", data_schema=FEED_STEP_SCHEMA, errors=errors
        )

    # @staticmethod
    # def async_get_options_flow(
    #     config_entry: ConfigEntry,
    # ) -> OptionsFlow:
    #     """Create the options flow."""
    #     return ElevenLabsOptionsFlow(config_entry)
