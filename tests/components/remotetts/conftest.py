"""Common fixtures for the RemoteTTS tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

from ha_remote_tts import ApiError
import pytest

from homeassistant.components.remotetts.const import CONF_LANGUAGE, CONF_NAME, CONF_URL

from tests.common import MockConfigEntry


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "homeassistant.components.remotetts.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture
def mock_async_client() -> Generator[AsyncMock]:
    """Override async RemoteTTS client."""
    client_mock = AsyncMock()
    # client_mock.voices.get_all.return_value = GetVoicesResponse(voices=MOCK_VOICES)
    # client_mock.models.get_all.return_value = MOCK_MODELS
    with patch(
        "ha_remote_tts.RemoteTTSClient", return_value=client_mock
    ) as mock_async_client:
        yield mock_async_client


@pytest.fixture
def mock_async_client_fail() -> Generator[AsyncMock]:
    """Override async RemoteTTS client."""
    with patch(
        "homeassistant.components.remotetts.config_flow.RemoteTTSClient",
        return_value=AsyncMock(),
    ) as mock_async_client:
        mock_async_client.side_effect = ApiError
        yield mock_async_client


@pytest.fixture
def mock_entry() -> MockConfigEntry:
    """Mock a config entry."""
    return MockConfigEntry(
        domain="remotetts",
        data={
            CONF_URL: "url",
            CONF_NAME: "name",
            CONF_LANGUAGE: "lang",
        },
    )
    # entry.models = {
    #     "model1": "model1",
    # }

    # entry.voices = {"voice1": "voice1"}
