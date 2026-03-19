"""batch/embedding.py 테스트."""

import os
import tempfile

import pytest

from batch.embedding import chunk_texts, compute_file_hash, detect_changes, parse_document, scan_documents


@pytest.fixture
def temp_doc_dir():
    with tempfile.TemporaryDirectory() as d:
        # 테스트 문서 생성
        with open(os.path.join(d, "test.txt"), "w", encoding="utf-8") as f:
            f.write("이것은 테스트 문서입니다.\n" * 100)
        with open(os.path.join(d, "test.md"), "w", encoding="utf-8") as f:
            f.write("# 제목\n\n본문 내용입니다.\n" * 50)
        with open(os.path.join(d, "test.csv"), "w", encoding="utf-8") as f:
            f.write("이름,값\n항목1,100\n항목2,200\n")
        with open(os.path.join(d, "skip.xlsx"), "w") as f:
            f.write("binary")
        yield d


def test_scan_documents(temp_doc_dir):
    result = scan_documents(temp_doc_dir)
    assert "test.txt" in result
    assert "test.md" in result
    assert "test.csv" in result
    assert "skip.xlsx" not in result


def test_compute_file_hash(temp_doc_dir):
    path = os.path.join(temp_doc_dir, "test.txt")
    h1 = compute_file_hash(path)
    h2 = compute_file_hash(path)
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex


def test_parse_document_txt(temp_doc_dir):
    texts = parse_document(os.path.join(temp_doc_dir, "test.txt"))
    assert len(texts) > 0
    assert "테스트" in texts[0]


def test_parse_document_unsupported(temp_doc_dir):
    texts = parse_document(os.path.join(temp_doc_dir, "skip.xlsx"))
    assert texts == []


def test_chunk_texts():
    long_text = "테스트 문장입니다. " * 500
    chunks = chunk_texts([long_text])
    assert len(chunks) > 1


def test_detect_changes_new_files(temp_doc_dir):
    changes = detect_changes(temp_doc_dir, {})
    assert len(changes["new"]) == 3
    assert len(changes["modified"]) == 0
    assert len(changes["deleted"]) == 0


def test_detect_changes_deleted_files(temp_doc_dir):
    existing = {"old_doc.txt": "oldhash"}
    changes = detect_changes(temp_doc_dir, existing)
    assert "old_doc.txt" in changes["deleted"]
