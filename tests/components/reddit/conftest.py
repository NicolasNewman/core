"""Common fixtures for the Reddit tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "homeassistant.components.reddit.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture
def mock_async_client() -> Generator[AsyncMock]:
    """Override async Reddit client."""
    client_mock = AsyncMock()
    # client_mock.voices.get_all.return_value = GetVoicesResponse(voices=MOCK_VOICES)
    # client_mock.models.get_all.return_value = MOCK_MODELS
    with patch("asyncpraw.Reddit", return_value=client_mock) as mock_async_client:
        yield mock_async_client
