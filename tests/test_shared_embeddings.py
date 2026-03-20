"""shared/embeddings.py 테스트."""

from unittest.mock import MagicMock, patch
import numpy as np

import pytest


@patch("shared.embeddings._get_model")
def test_embed_texts_local(mock_get_model):
    """local 백엔드(sentence-transformers)에서 embed_texts가 정상 동작하는지 검증."""
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
    mock_get_model.return_value = mock_model

    with patch("shared.embeddings.EMBEDDING_BACKEND", "local"):
        from shared.embeddings import embed_texts
        result = embed_texts(["hello"])

    assert result == [[0.1, 0.2, 0.3]]
    mock_model.encode.assert_called_once()


@patch("shared.embeddings._get_model")
def test_embed_text_local(mock_get_model):
    """local 백엔드에서 embed_text(단일)가 정상 동작하는지 검증."""
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([[0.4, 0.5]])
    mock_get_model.return_value = mock_model

    with patch("shared.embeddings.EMBEDDING_BACKEND", "local"):
        from shared.embeddings import embed_text
        result = embed_text("test")

    assert result == [0.4, 0.5]


@patch("shared.embeddings._get_model")
def test_embed_texts_fastembed(mock_get_model):
    """fastembed 백엔드에서 embed_texts가 정상 동작하는지 검증."""
    mock_model = MagicMock()
    mock_model.embed.return_value = [np.array([0.1, 0.2, 0.3])]
    mock_get_model.return_value = mock_model

    with patch("shared.embeddings.EMBEDDING_BACKEND", "fastembed"):
        from shared.embeddings import embed_texts
        result = embed_texts(["hello"])

    assert result == [[0.1, 0.2, 0.3]]
    mock_model.embed.assert_called_once()
