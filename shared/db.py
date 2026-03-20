"""DB 접근 모듈 - ChromaDB, KùzuDB, SQLite.

세 가지 저장소를 Repository 패턴으로 추상화한다.
- ChromaDB: 벡터 임베딩 저장/검색 (코사인 유사도)
- KùzuDB: 엔티티-관계 지식 그래프 (임베디드 그래프 DB)
- SQLite: 문서 메타데이터 및 배치 실행 이력
"""

import json
import logging
import os
import sqlite3
from datetime import datetime, timezone

import chromadb
import kuzu

from shared.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIR,
    KUZU_DB_PATH,
    SQLITE_DB_PATH,
)

logger = logging.getLogger(__name__)


# ── ChromaDB ──────────────────────────────────────────────


class ChromaRepository:
    def __init__(self):
        os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
        self._client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        # hnsw:space=cosine → 코사인 유사도 기반 ANN 인덱스
        self._collection = self._client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )

    def upsert(self, doc_id: str, chunk_ids: list[str], texts: list[str], embeddings: list[list[float]], metadatas: list[dict]):
        self._collection.upsert(ids=chunk_ids, documents=texts, embeddings=embeddings, metadatas=metadatas)

    def search(self, embedding: list[float], top_k: int = 5) -> dict:
        return self._collection.query(query_embeddings=[embedding], n_results=top_k)

    def delete_by_doc(self, doc_id: str):
        try:
            self._collection.delete(where={"doc_id": doc_id})
        except Exception as e:
            logger.warning(f"ChromaDB 삭제 실패 (doc_id={doc_id}): {e}")

    def reset(self):
        """컬렉션을 삭제 후 재생성하여 전체 데이터를 초기화한다."""
        self._client.delete_collection(CHROMA_COLLECTION_NAME)
        self._collection = self._client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )


# ── KùzuDB ────────────────────────────────────────────────


class KuzuRepository:
    """KùzuDB 지식 그래프 저장소.

    초기화 실패 시 Graph 검색을 비활성화하고 Vector 검색만으로 동작한다.
    (Graceful Degradation - KùzuDB 없이도 서비스 가능)
    """

    def __init__(self):
        try:
            # kuzu 0.11+는 DB 경로가 이미 디렉토리로 존재하면 에러 → 부모만 생성
            parent = os.path.dirname(KUZU_DB_PATH)
            if parent:
                os.makedirs(parent, exist_ok=True)
            self._db = kuzu.Database(KUZU_DB_PATH)
            self._conn = kuzu.Connection(self._db)
            self._init_schema()
            logger.info("KùzuDB 연결 성공")
        except Exception as e:
            self._db = None
            self._conn = None
            logger.warning(f"KùzuDB 초기화 실패 (Graph 검색 비활성화): {e}")

    def _init_schema(self):
        """Entity 노드와 RELATES 관계 테이블을 생성한다.

        Entity: name(PK), type(CONCEPT/PERSON/SYSTEM 등), doc_id(출처 문서)
        RELATES: 엔티티 간 관계 (type: RELATED_TO/PART_OF/USES 등)
        """
        try:
            self._conn.execute("CREATE NODE TABLE IF NOT EXISTS Entity(name STRING, type STRING, doc_id STRING, PRIMARY KEY(name))")
            self._conn.execute("CREATE REL TABLE IF NOT EXISTS RELATES(FROM Entity TO Entity, type STRING, doc_id STRING)")
        except Exception as e:
            logger.warning(f"KùzuDB 스키마 초기화 경고: {e}")

    @property
    def available(self) -> bool:
        return self._conn is not None

    def close(self):
        self._conn = None
        self._db = None

    def upsert_entities(self, doc_id: str, entities: list[dict], relations: list[dict]):
        if not self.available:
            return
        # MERGE: 동일 name의 엔티티가 있으면 업데이트, 없으면 생성
        for entity in entities:
            self._conn.execute(
                "MERGE (e:Entity {name: $name}) SET e.type = $type, e.doc_id = $doc_id",
                parameters={"name": entity["name"], "type": entity.get("type", "CONCEPT"), "doc_id": doc_id},
            )
        for rel in relations:
            try:
                self._conn.execute(
                    "MATCH (a:Entity {name: $source}), (b:Entity {name: $target}) "
                    "CREATE (a)-[:RELATES {type: $rel_type, doc_id: $doc_id}]->(b)",
                    parameters={"source": rel["source"], "target": rel["target"],
                                "rel_type": rel.get("type", "RELATED_TO"), "doc_id": doc_id},
                )
            except Exception:
                pass  # 중복 관계 무시

    def search_related(self, entity_names: list[str], top_k: int = 5) -> list[dict]:
        """엔티티명 목록으로 1-hop 관계를 탐색한다.

        양방향 탐색(-[r:RELATES]-)으로 incoming/outgoing 관계 모두 반환.
        """
        if not self.available:
            return []
        results = []
        for name in entity_names:
            try:
                result = self._conn.execute(
                    "MATCH (a:Entity {name: $name})-[r:RELATES]-(b:Entity) "
                    "RETURN a.name AS source, r.type AS rel_type, r.type AS rel_subtype, "
                    "b.name AS target, b.type AS target_type, r.doc_id AS doc_id LIMIT $limit",
                    parameters={"name": name, "limit": top_k},
                )
                while result.has_next():
                    row = result.get_next()
                    results.append({"source": row[0], "rel_type": row[1], "rel_subtype": row[2],
                                    "target": row[3], "target_type": row[4], "doc_id": row[5]})
            except Exception:
                pass
        return results

    def delete_by_doc(self, doc_id: str):
        """문서에 속한 관계 → 엔티티 순서로 삭제한다.

        관계를 먼저 삭제해야 엔티티 삭제 시 참조 무결성 오류가 발생하지 않는다.
        """
        if not self.available:
            return
        try:
            self._conn.execute("MATCH (a:Entity)-[r:RELATES]->() WHERE r.doc_id = $doc_id DELETE r", parameters={"doc_id": doc_id})
            self._conn.execute("MATCH ()-[r:RELATES]->(b:Entity) WHERE r.doc_id = $doc_id DELETE r", parameters={"doc_id": doc_id})
            self._conn.execute("MATCH (e:Entity) WHERE e.doc_id = $doc_id DELETE e", parameters={"doc_id": doc_id})
        except Exception as e:
            logger.warning(f"KùzuDB 삭제 실패 (doc_id={doc_id}): {e}")

    def reset(self):
        if not self.available:
            return
        try:
            self._conn.execute("MATCH (n:Entity) DETACH DELETE n")
        except Exception:
            pass


# ── SQLite ────────────────────────────────────────────────


class SQLiteRepository:
    """문서 메타데이터와 배치 실행 이력을 관리한다.

    document_meta: 증분 임베딩을 위한 파일 해시 및 상태 추적
    batch_log: 배치 실행 결과 기록 (모드, 처리/실패/삭제 건수)
    """

    def __init__(self):
        os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
        self._conn = sqlite3.connect(SQLITE_DB_PATH)
        self._conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS document_meta (
                doc_id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                file_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'embedded',
                chunk_count INTEGER DEFAULT 0,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS batch_log (
                run_id TEXT PRIMARY KEY,
                mode TEXT NOT NULL,
                total_files INTEGER,
                processed INTEGER,
                skipped INTEGER,
                failed INTEGER,
                deleted INTEGER,
                started_at TEXT NOT NULL,
                finished_at TEXT
            );
        """)
        self._conn.commit()

    def save_doc_meta(self, doc_id: str, file_path: str, file_hash: str, file_type: str, status: str, chunk_count: int):
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            "INSERT OR REPLACE INTO document_meta (doc_id, file_path, file_hash, file_type, status, chunk_count, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (doc_id, file_path, file_hash, file_type, status, chunk_count, now),
        )
        self._conn.commit()

    def get_all_doc_hashes(self) -> dict[str, str]:
        """증분 임베딩 시 변경 감지를 위해 기존 문서의 해시를 조회한다."""
        rows = self._conn.execute("SELECT doc_id, file_hash FROM document_meta WHERE status != 'deleted'").fetchall()
        return {row["doc_id"]: row["file_hash"] for row in rows}

    def delete_doc_meta(self, doc_id: str):
        self._conn.execute("DELETE FROM document_meta WHERE doc_id = ?", (doc_id,))
        self._conn.commit()

    def save_batch_log(self, run_id: str, mode: str, total_files: int, processed: int, skipped: int, failed: int, deleted: int, started_at: str):
        finished_at = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            "INSERT INTO batch_log (run_id, mode, total_files, processed, skipped, failed, deleted, started_at, finished_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (run_id, mode, total_files, processed, skipped, failed, deleted, started_at, finished_at),
        )
        self._conn.commit()

    def reset(self):
        self._conn.executescript("DELETE FROM document_meta; DELETE FROM batch_log;")
        self._conn.commit()

    def close(self):
        self._conn.close()
