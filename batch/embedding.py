"""문서 파싱, 청킹, 임베딩, 엔티티 추출 모듈."""

import hashlib
import json
import logging
import os
from pathlib import Path

from langchain_community.document_loaders import CSVLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from pydantic import BaseModel

from shared.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    OPENAI_API_BASE,
    OPENAI_API_KEY,
    OPENAI_CHAT_MODEL,
    SUPPORTED_EXTENSIONS,
)
from shared.embeddings import embed_texts

logger = logging.getLogger(__name__)


# ── Pydantic 스키마 ───────────────────────────────────────


class ExtractedEntity(BaseModel):
    name: str
    type: str = "CONCEPT"


class ExtractedRelation(BaseModel):
    source: str
    target: str
    type: str = "RELATED_TO"


class ExtractionResult(BaseModel):
    entities: list[ExtractedEntity] = []
    relations: list[ExtractedRelation] = []


# ── 문서 파싱 ─────────────────────────────────────────────


LOADERS = {
    ".txt": lambda p: TextLoader(p, encoding="utf-8"),
    ".csv": lambda p: CSVLoader(p, encoding="utf-8"),
    ".md": lambda p: UnstructuredMarkdownLoader(p),
}


def parse_document(file_path: str) -> list[str]:
    """파일을 읽어 텍스트 리스트로 반환."""
    ext = Path(file_path).suffix.lower()
    if ext not in LOADERS:
        logger.warning(f"지원하지 않는 형식: {file_path} - 복호화 후 .txt/.csv로 변환하여 다시 배치해주세요.")
        return []
    loader = LOADERS[ext](file_path)
    docs = loader.load()
    return [doc.page_content for doc in docs]


# ── 청킹 ─────────────────────────────────────────────────


_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def chunk_texts(texts: list[str]) -> list[str]:
    """텍스트를 청크로 분할."""
    full_text = "\n\n".join(texts)
    return _splitter.split_text(full_text)


# ── 엔티티 추출 ──────────────────────────────────────────


EXTRACTION_PROMPT = """다음 텍스트에서 핵심 엔티티(개념, 용어, 인물, 조직, 시스템, 프로세스)와 엔티티 간 관계를 추출하세요.

텍스트:
{text}

JSON 형식으로 응답하세요:
{{"entities": [{{"name": "엔티티명", "type": "CONCEPT|PERSON|ORGANIZATION|SYSTEM|PROCESS"}}], "relations": [{{"source": "엔티티1", "target": "엔티티2", "type": "RELATED_TO|PART_OF|USES|DEPENDS_ON|MANAGES"}}]}}
"""

_llm_client = None


def _get_llm_client() -> OpenAI:
    global _llm_client
    if _llm_client is None:
        _llm_client = OpenAI(base_url=OPENAI_API_BASE, api_key=OPENAI_API_KEY)
    return _llm_client


def extract_entities(text: str) -> ExtractionResult:
    """LLM으로 텍스트에서 엔티티/관계 추출."""
    try:
        client = _get_llm_client()
        response = client.chat.completions.create(
            model=OPENAI_CHAT_MODEL,
            messages=[{"role": "user", "content": EXTRACTION_PROMPT.format(text=text[:3000])}],
            temperature=0,
        )
        content = response.choices[0].message.content.strip()
        # JSON 파싱 시도
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        data = json.loads(content)
        return ExtractionResult(**data)
    except Exception as e:
        logger.warning(f"엔티티 추출 실패: {e}")
        return ExtractionResult()


# ── 변경 감지 ─────────────────────────────────────────────


def compute_file_hash(file_path: str) -> str:
    """파일 SHA-256 해시 계산."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_documents(doc_dir: str) -> dict[str, str]:
    """문서 디렉토리를 스캔하여 {doc_id: file_path} 반환. 지원 형식만."""
    result = {}
    for root, _, files in os.walk(doc_dir):
        for fname in files:
            fpath = os.path.join(root, fname)
            ext = Path(fname).suffix.lower()
            if ext in SUPPORTED_EXTENSIONS:
                doc_id = os.path.relpath(fpath, doc_dir)
                result[doc_id] = fpath
    return result


def detect_changes(doc_dir: str, existing_hashes: dict[str, str]) -> dict:
    """변경 감지: new, modified, deleted, unchanged 분류."""
    current_files = scan_documents(doc_dir)
    new, modified, unchanged = [], [], []

    for doc_id, fpath in current_files.items():
        file_hash = compute_file_hash(fpath)
        if doc_id not in existing_hashes:
            new.append((doc_id, fpath, file_hash))
        elif existing_hashes[doc_id] != file_hash:
            modified.append((doc_id, fpath, file_hash))
        else:
            unchanged.append(doc_id)

    deleted = [doc_id for doc_id in existing_hashes if doc_id not in current_files]

    return {"new": new, "modified": modified, "deleted": deleted, "unchanged": unchanged}
