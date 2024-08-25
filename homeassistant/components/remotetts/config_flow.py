"""Config flow for remotetts."""

from __future__ import annotations

import logging
from typing import Any

from ha_remote_tts import ApiError, RemoteTTSClient
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
    OptionsFlowWithConfigEntry,
)

from . import RemoteTTSConfigEntry
from .const import CONF_LANGUAGE, CONF_NAME, CONF_URL, DOMAIN

USER_STEP_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_LANGUAGE): str,
        vol.Required(CONF_URL): str,
    }
)

_LOGGER = logging.getLogger(__name__)


class RemoteTTSConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for RemoteTTS text-to-speech."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                client = RemoteTTSClient(user_input[CONF_URL])
                await client.verify_connection()
                await client.close()
            except ApiError:
                errors["base"] = "invalid_url"
            except ValueError:
                errors["base"] = "connection_error"
            return self.async_create_entry(
                title="RemoteTTS",
                data=user_input,
                options={
                    CONF_NAME: "RemoteTTS Voice",
                    CONF_LANGUAGE: "",
                    CONF_URL: "",
                },
            )
        return self.async_show_form(
            step_id="user", data_schema=USER_STEP_SCHEMA, errors=errors
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: RemoteTTSConfigEntry,
    ) -> OptionsFlow:
        """Create the options flow."""
        return RemoteTTSOptionsFlow(config_entry)


class RemoteTTSOptionsFlow(OptionsFlowWithConfigEntry):
    """RemoteTTS options flow."""

    def __init__(self, config_entry: RemoteTTSConfigEntry) -> None:
        """Initialize options flow."""
        super().__init__(config_entry)

        self.name = getattr(config_entry.runtime_data, CONF_NAME)
        self.url = getattr(config_entry.runtime_data, CONF_URL)
        self.language = getattr(config_entry.runtime_data, CONF_LANGUAGE)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            try:
                client = RemoteTTSClient(user_input[CONF_URL])
                await client.verify_connection()
                await client.close()
            except ApiError as err:
                _LOGGER.warning(err)
                return self.async_abort(reason=f"{err.status_code}: {err.body}")
            except ValueError as err:
                _LOGGER.warning(err)
                return self.async_abort(reason="URL must be absolute")

            return self.async_create_entry(
                title="RemoteTTS",
                data=user_input,
            )

        self.options[CONF_NAME] = self.name
        self.options[CONF_LANGUAGE] = self.language
        self.options[CONF_URL] = self.url

        schema = self.remote_tts_config_option_schema()
        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )

    def remote_tts_config_option_schema(self) -> vol.Schema:
        """RemoteTTS options schema."""
        return self.add_suggested_values_to_schema(
            vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Required(CONF_LANGUAGE): str,
                    vol.Required(CONF_URL): str,
                }
            ),
            self.options,
        )
