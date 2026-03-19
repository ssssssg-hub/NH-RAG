"""OpenAI 호환 임베딩 API 호출 모듈.

Lazy Singleton 패턴으로 OpenAI 클라이언트를 관리한다.
내부망의 OpenAI 호환 API 서버(vLLM, Ollama 등)에 대해 동일하게 동작한다.
"""

from openai import OpenAI
from shared.config import OPENAI_API_BASE, OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(base_url=OPENAI_API_BASE, api_key=OPENAI_API_KEY)
    return _client


def embed_texts(texts: list[str]) -> list[list[float]]:
    """텍스트 리스트를 임베딩 벡터로 변환. 배치 호출로 API 요청을 최소화한다."""
    client = _get_client()
    response = client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=texts)
    return [item.embedding for item in response.data]


def embed_text(text: str) -> list[float]:
    """단일 텍스트를 임베딩 벡터로 변환."""
    return embed_texts([text])[0]
