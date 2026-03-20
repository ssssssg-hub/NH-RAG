"""문서 파싱, 청킹, 엔티티 추출, 변경 감지 모듈.

배치 임베딩 파이프라인의 핵심 처리 단계를 담당한다:
파일 읽기 → 텍스트 청킹 → LLM 엔티티/관계 추출 → SHA-256 변경 감지
"""

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

# 확장자별 LangChain 로더 매핑
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

# 구분자 우선순위: 문단 > 줄바꿈 > 문장 > 단어 > 문자
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

# LLM에게 구조화된 JSON으로 엔티티/관계를 추출하도록 지시하는 프롬프트
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


def extract_entities(text: str, max_retries: int = 3) -> ExtractionResult:
    """LLM으로 텍스트에서 엔티티/관계를 추출한다.

    입력 텍스트를 3000자로 제한하여 토큰 비용을 절감한다.
    Rate limit(429) 발생 시 retryDelay를 파싱하여 대기 후 재시도한다.
    실패 시 빈 결과를 반환하여 임베딩 파이프라인이 중단되지 않는다.
    """
    import re
    import time

    for attempt in range(max_retries):
        try:
            client = _get_llm_client()
            response = client.chat.completions.create(
                model=OPENAI_CHAT_MODEL,
                messages=[{"role": "user", "content": EXTRACTION_PROMPT.format(text=text[:3000])}],
                temperature=0,
            )
            content = response.choices[0].message.content.strip()
            # LLM이 마크다운 코드블록으로 감싸는 경우 처리
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            data = json.loads(content)
            return ExtractionResult(**data)
        except Exception as e:
            err_str = str(e)
            if "429" in err_str and attempt < max_retries - 1:
                match = re.search(r'retryDelay.*?(\d+)', err_str)
                wait = int(match.group(1)) + 2 if match else 35
                logger.info(f"Rate limit 도달, {wait}초 대기 후 재시도 ({attempt + 1}/{max_retries})")
                time.sleep(wait)
                continue
            logger.warning(f"엔티티 추출 실패: {e}")
            return ExtractionResult()
    return ExtractionResult()


# ── 변경 감지 ─────────────────────────────────────────────


def compute_file_hash(file_path: str) -> str:
    """파일 SHA-256 해시 계산. 8KB 단위로 읽어 대용량 파일도 처리 가능."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_documents(doc_dir: str) -> dict[str, str]:
    """문서 디렉토리를 재귀 스캔하여 {doc_id: file_path} 반환.

    doc_id는 문서 디렉토리 기준 상대 경로를 사용한다.
    """
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
    """현재 파일과 기존 해시를 비교하여 new/modified/deleted/unchanged로 분류한다."""
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

    # 디렉토리에서 사라진 파일 감지
    deleted = [doc_id for doc_id in existing_hashes if doc_id not in current_files]

    return {"new": new, "modified": modified, "deleted": deleted, "unchanged": unchanged}
