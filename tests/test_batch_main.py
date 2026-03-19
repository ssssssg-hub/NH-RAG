"""batch/batch.py CLI 및 오케스트레이션 테스트."""

from unittest.mock import MagicMock, patch

import pytest


@patch("batch.batch.KuzuRepository")
@patch("batch.batch.ChromaRepository")
@patch("batch.batch.SQLiteRepository")
@patch("batch.batch.scan_documents")
@patch("batch.batch.compute_file_hash")
def test_run_full_mode_empty(mock_hash, mock_scan, mock_sqlite_cls, mock_chroma_cls, mock_kuzu_cls):
    mock_scan.return_value = {}
    mock_sqlite = MagicMock()
    mock_sqlite_cls.return_value = mock_sqlite
    mock_chroma = MagicMock()
    mock_chroma_cls.return_value = mock_chroma
    mock_kuzu = MagicMock()
    mock_kuzu_cls.return_value = mock_kuzu

    from batch.batch import run
    run(full=True)

    mock_chroma.reset.assert_called_once()
    mock_kuzu.reset.assert_called_once()
    mock_sqlite.reset.assert_called_once()


@patch("batch.batch.KuzuRepository")
@patch("batch.batch.ChromaRepository")
@patch("batch.batch.SQLiteRepository")
@patch("batch.batch.detect_changes")
def test_run_incremental_no_changes(mock_detect, mock_sqlite_cls, mock_chroma_cls, mock_kuzu_cls):
    mock_detect.return_value = {"new": [], "modified": [], "deleted": [], "unchanged": ["doc1"]}
    mock_sqlite = MagicMock()
    mock_sqlite.get_all_doc_hashes.return_value = {"doc1": "hash1"}
    mock_sqlite_cls.return_value = mock_sqlite
    mock_chroma_cls.return_value = MagicMock()
    mock_kuzu_cls.return_value = MagicMock()

    from batch.batch import run
    run(full=False)

    mock_sqlite.save_batch_log.assert_called_once()
