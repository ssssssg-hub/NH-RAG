"""shared/embeddings.py 테스트."""

from unittest.mock import MagicMock, patch

import pytest


@patch("shared.embeddings._get_client")
def test_embed_texts(mock_get_client):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_item = MagicMock()
    mock_item.embedding = [0.1, 0.2, 0.3]
    mock_response.data = [mock_item]
    mock_client.embeddings.create.return_value = mock_response
    mock_get_client.return_value = mock_client

    from shared.embeddings import embed_texts
    result = embed_texts(["hello"])

    assert result == [[0.1, 0.2, 0.3]]
    mock_client.embeddings.create.assert_called_once()


@patch("shared.embeddings._get_client")
def test_embed_text(mock_get_client):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_item = MagicMock()
    mock_item.embedding = [0.4, 0.5]
    mock_response.data = [mock_item]
    mock_client.embeddings.create.return_value = mock_response
    mock_get_client.return_value = mock_client

    from shared.embeddings import embed_text
    result = embed_text("test")

    assert result == [0.4, 0.5]
