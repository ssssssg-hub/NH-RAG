"""shared/db.py SQLite 테스트."""

import os
import tempfile

import pytest

# SQLite 테스트용 임시 DB 경로 설정
_temp_dir = tempfile.mkdtemp()
os.environ["NH_RAG_DATA_DIR"] = _temp_dir

from shared.db import SQLiteRepository


@pytest.fixture
def sqlite_repo():
    repo = SQLiteRepository()
    yield repo
    repo.close()


def test_save_and_get_doc_meta(sqlite_repo):
    sqlite_repo.save_doc_meta("doc1", "/path/doc1.txt", "abc123", ".txt", "embedded", 5)
    hashes = sqlite_repo.get_all_doc_hashes()
    assert "doc1" in hashes
    assert hashes["doc1"] == "abc123"


def test_delete_doc_meta(sqlite_repo):
    sqlite_repo.save_doc_meta("doc2", "/path/doc2.txt", "def456", ".txt", "embedded", 3)
    sqlite_repo.delete_doc_meta("doc2")
    hashes = sqlite_repo.get_all_doc_hashes()
    assert "doc2" not in hashes


def test_save_batch_log(sqlite_repo):
    # 에러 없이 저장되는지 확인
    sqlite_repo.save_batch_log("run1", "incremental", 10, 8, 1, 1, 0, "2026-01-01T00:00:00Z")


def test_reset(sqlite_repo):
    sqlite_repo.save_doc_meta("doc3", "/path/doc3.txt", "ghi789", ".txt", "embedded", 2)
    sqlite_repo.reset()
    hashes = sqlite_repo.get_all_doc_hashes()
    assert len(hashes) == 0
