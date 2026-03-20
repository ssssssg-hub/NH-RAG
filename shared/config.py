"""NH-RAG 공통 설정 모듈."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# 필수 환경변수 검증
_REQUIRED_VARS = ["NH_RAG_OPENAI_API_BASE", "NH_RAG_OPENAI_API_KEY", "NH_RAG_CHAT_MODEL"]
_missing = [v for v in _REQUIRED_VARS if not os.getenv(v)]
if _missing:
    print(f"[ERROR] 필수 환경변수가 설정되지 않았습니다: {', '.join(_missing)}", file=sys.stderr)
    print("  .env 파일을 프로젝트 루트에 생성하세요. README.md 참고.", file=sys.stderr)
    sys.exit(1)

# 문서 디렉토리
DOCUMENTS_DIR = os.getenv("NH_RAG_DOCUMENTS_DIR", str(PROJECT_ROOT / "documents"))

# 데이터 디렉토리
DATA_DIR = os.getenv("NH_RAG_DATA_DIR", str(PROJECT_ROOT / "data"))

# SQLite
SQLITE_DB_PATH = os.path.join(DATA_DIR, "nh_rag.db")

# ChromaDB
CHROMA_PERSIST_DIR = os.path.join(DATA_DIR, "chromadb")
CHROMA_COLLECTION_NAME = "nh_rag_documents"

# KùzuDB
KUZU_DB_PATH = os.path.join(DATA_DIR, "kuzudb")

# OpenAI API (채팅 전용)
OPENAI_API_BASE = os.getenv("NH_RAG_OPENAI_API_BASE")
OPENAI_API_KEY = os.getenv("NH_RAG_OPENAI_API_KEY")
OPENAI_CHAT_MODEL = os.getenv("NH_RAG_CHAT_MODEL")

# 로컬 임베딩 설정
# backend: "local" (sentence-transformers) 또는 "fastembed"
EMBEDDING_BACKEND = os.getenv("NH_RAG_EMBEDDING_BACKEND", "local")
# local 모드: 모델 디렉토리 경로 또는 HuggingFace 모델명
EMBEDDING_MODEL_PATH = os.getenv("NH_RAG_EMBEDDING_MODEL_PATH", str(PROJECT_ROOT / "models" / "ko-sroberta"))
# fastembed 모드: 모델명
FASTEMBED_MODEL_NAME = os.getenv("NH_RAG_FASTEMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# 청킹 설정
CHUNK_SIZE = int(os.getenv("NH_RAG_CHUNK_SIZE", "1500"))
CHUNK_OVERLAP = int(os.getenv("NH_RAG_CHUNK_OVERLAP", "150"))

# 검색 설정
VECTOR_SEARCH_TOP_K = int(os.getenv("NH_RAG_VECTOR_TOP_K", "5"))
GRAPH_SEARCH_TOP_K = int(os.getenv("NH_RAG_GRAPH_TOP_K", "5"))

# 지원 파일 형식
SUPPORTED_EXTENSIONS = {".txt", ".csv", ".md"}
