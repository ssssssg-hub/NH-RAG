"""로컬 임베딩 모듈.

환경변수 NH_RAG_EMBEDDING_BACKEND로 백엔드를 선택한다:
- "local": sentence-transformers + 한국어 모델 (torch CPU 필요)
- "fastembed": ONNX 기반 다국어 모델 (torch 불필요, 폴백용)
"""

import logging

from shared.config import EMBEDDING_BACKEND, EMBEDDING_MODEL_PATH, FASTEMBED_MODEL_NAME

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    global _model
    if _model is not None:
        return _model

    if EMBEDDING_BACKEND == "fastembed":
        from fastembed import TextEmbedding

        _model = TextEmbedding(model_name=FASTEMBED_MODEL_NAME)
        logger.info(f"fastembed 모델 로드: {FASTEMBED_MODEL_NAME}")
    else:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(EMBEDDING_MODEL_PATH)
        logger.info(f"sentence-transformers 모델 로드: {EMBEDDING_MODEL_PATH}")

    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """텍스트 리스트를 임베딩 벡터로 변환."""
    model = _get_model()

    if EMBEDDING_BACKEND == "fastembed":
        return [e.tolist() for e in model.embed(texts)]
    else:
        return model.encode(texts, normalize_embeddings=True).tolist()


def embed_text(text: str) -> list[float]:
    """단일 텍스트를 임베딩 벡터로 변환."""
    return embed_texts([text])[0]
