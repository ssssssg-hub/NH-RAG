"""backend/app.py API 테스트."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@patch("backend.app.RAGEngine")
def test_new_session(mock_engine_cls):
    mock_engine_cls.return_value = MagicMock()
    from backend.app import app
    client = TestClient(app)
    response = client.post("/api/chat/new")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data


@patch("backend.app.rag_engine")
def test_chat_empty_message(mock_engine):
    from backend.app import app
    client = TestClient(app)
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 422  # validation error


@patch("backend.app.rag_engine")
def test_chat_returns_sse(mock_engine):
    mock_engine.search.return_value = ("context", [])

    async def mock_stream(*args, **kwargs):
        yield {"event": "token", "data": "안녕"}
    mock_engine.generate_stream = mock_stream

    from backend.app import app
    client = TestClient(app)
    response = client.post("/api/chat", json={"message": "테스트 질문"})
    assert response.status_code == 200
