"""backend/rag_engine.py 테스트."""

from unittest.mock import MagicMock, patch

import pytest


@patch("backend.rag_engine.KuzuRepository")
@patch("backend.rag_engine.ChromaRepository")
@patch("backend.rag_engine.OpenAI")
@patch("backend.rag_engine.embed_text")
def test_search_returns_context_and_sources(mock_embed, mock_openai_cls, mock_chroma_cls, mock_kuzu_cls):
    mock_embed.return_value = [0.1, 0.2]

    mock_chroma = MagicMock()
    mock_chroma.search.return_value = {
        "documents": [["문서 내용입니다"]],
        "metadatas": [[{"doc_id": "doc1", "chunk_index": 0, "file_name": "test.txt"}]],
    }
    mock_chroma_cls.return_value = mock_chroma

    mock_kuzu = MagicMock()
    mock_kuzu.search_related.return_value = []
    mock_kuzu_cls.return_value = mock_kuzu

    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '["테스트"]'
    mock_llm.chat.completions.create.return_value = mock_response
    mock_openai_cls.return_value = mock_llm

    from backend.rag_engine import RAGEngine
    engine = RAGEngine()
    context, sources = engine.search("테스트 질문")

    assert "문서 내용" in context
    assert len(sources) > 0
    assert sources[0].file_name == "test.txt"


@patch("backend.rag_engine.KuzuRepository")
@patch("backend.rag_engine.ChromaRepository")
@patch("backend.rag_engine.OpenAI")
@patch("backend.rag_engine.embed_text")
def test_search_handles_failure(mock_embed, mock_openai_cls, mock_chroma_cls, mock_kuzu_cls):
    mock_embed.side_effect = Exception("API 실패")
    mock_chroma_cls.return_value = MagicMock()
    mock_kuzu_cls.return_value = MagicMock()
    mock_openai_cls.return_value = MagicMock()

    from backend.rag_engine import RAGEngine
    engine = RAGEngine()
    context, sources = engine.search("테스트")

    assert context == ""
    assert sources == []
