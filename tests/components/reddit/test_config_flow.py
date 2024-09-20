"""Test the Reddit config flow."""

from unittest.mock import AsyncMock

from homeassistant.components.reddit.const import CONF_SORT_BY, CONF_SUBREDDITS, DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_MAXIMUM,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def test_steps(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_async_client: AsyncMock,
) -> None:
    """Test steps create entry result."""
    # USER STEP
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert not result["errors"]

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "RedditTest",
            CONF_CLIENT_ID: "client_id",
            CONF_CLIENT_SECRET: "client_secret",
            CONF_USERNAME: "username",
            CONF_PASSWORD: "password",
        },
    )

    # FEED STEP
    assert result["type"] is FlowResultType.FORM
    assert not result["errors"]
    assert result["step_id"] == "feed"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_SUBREDDITS: ["subreddits"],
            CONF_SORT_BY: "hot",
            CONF_MAXIMUM: 10,
        },
    )

    # VALIDATE RESULTS
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "RedditTest"
    assert result["data"] == {
        CONF_NAME: "RedditTest",
        CONF_CLIENT_ID: "client_id",
        CONF_CLIENT_SECRET: "client_secret",
        CONF_USERNAME: "username",
        CONF_PASSWORD: "password",
        CONF_SUBREDDITS: ["subreddits"],
        CONF_SORT_BY: "hot",
        CONF_MAXIMUM: 10,
    }

    mock_setup_entry.assert_called_once()
