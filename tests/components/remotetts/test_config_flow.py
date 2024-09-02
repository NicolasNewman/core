"""Test the ElevenLabs text-to-speech config flow."""

from unittest.mock import AsyncMock

from homeassistant.components.remotetts.const import (
    CONF_LANGUAGE,
    CONF_NAME,
    CONF_URL,
    DOMAIN,
)
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def test_user_step(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_async_client: AsyncMock,
) -> None:
    """Test user step create entry result."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert not result["errors"]

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "name",
            CONF_LANGUAGE: "lang",
            CONF_URL: "url",
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "RemoteTTS"
    assert result["data"] == {
        CONF_NAME: "name",
        CONF_LANGUAGE: "lang",
        CONF_URL: "url",
    }
    # assert result["options"] == {CONF_MODEL: DEFAULT_MODEL, CONF_VOICE: "voice1"}

    mock_setup_entry.assert_called_once()


async def test_invalid_api_key(
    hass: HomeAssistant, mock_setup_entry: AsyncMock, mock_async_client_fail: AsyncMock
) -> None:
    """Test user step with an invalid name."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert not result["errors"]

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "name",
            CONF_LANGUAGE: "lang",
            CONF_URL: "url",
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"]

    mock_setup_entry.assert_not_called()
