"""NH-RAG 공통 설정 모듈."""

import os
from pathlib import Path

from dotenv import load_dotenv

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

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

# OpenAI API (내부)
OPENAI_API_BASE = os.getenv("NH_RAG_OPENAI_API_BASE", "http://localhost:8000/v1")
OPENAI_API_KEY = os.getenv("NH_RAG_OPENAI_API_KEY", "internal-key")
OPENAI_EMBEDDING_MODEL = os.getenv("NH_RAG_EMBEDDING_MODEL", "text-embedding-ada-002")
OPENAI_CHAT_MODEL = os.getenv("NH_RAG_CHAT_MODEL", "gpt-4")

# 청킹 설정
CHUNK_SIZE = int(os.getenv("NH_RAG_CHUNK_SIZE", "1500"))
CHUNK_OVERLAP = int(os.getenv("NH_RAG_CHUNK_OVERLAP", "150"))

# 검색 설정
VECTOR_SEARCH_TOP_K = int(os.getenv("NH_RAG_VECTOR_TOP_K", "5"))
GRAPH_SEARCH_TOP_K = int(os.getenv("NH_RAG_GRAPH_TOP_K", "5"))

# 지원 파일 형식
SUPPORTED_EXTENSIONS = {".txt", ".csv", ".md"}
