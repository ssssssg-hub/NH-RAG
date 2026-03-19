# Unit Test Execution

## 테스트 프레임워크
- **pytest** + **pytest-asyncio**
- 모든 외부 의존성(OpenAI API, ChromaDB, KùzuDB)은 mock 처리

## Run Unit Tests

### 1. 전체 테스트 실행
```bash
pytest tests/ -v
```

### 2. 모듈별 실행
```bash
# shared 모듈
pytest tests/test_shared_db.py tests/test_shared_embeddings.py -v

# batch 모듈
pytest tests/test_batch_embedding.py tests/test_batch_main.py -v

# backend 모듈
pytest tests/test_backend_rag_engine.py tests/test_backend_app.py -v
```

### 3. 커버리지 측정 (선택)
```bash
pip install pytest-cov
pytest tests/ -v --cov=shared --cov=batch --cov=backend --cov-report=term-missing
```

## 테스트 목록

### shared 모듈 (4 tests)
| 테스트 | 검증 내용 |
|---|---|
| `test_save_and_get_doc_meta` | SQLite 문서 메타 저장/조회 |
| `test_delete_doc_meta` | SQLite 문서 메타 삭제 |
| `test_save_batch_log` | 배치 로그 저장 |
| `test_reset` | SQLite 전체 초기화 |

### shared/embeddings 모듈 (2 tests)
| 테스트 | 검증 내용 |
|---|---|
| `test_embed_texts` | 복수 텍스트 임베딩 (mock) |
| `test_embed_text` | 단일 텍스트 임베딩 (mock) |

### batch 모듈 (7 tests)
| 테스트 | 검증 내용 |
|---|---|
| `test_scan_documents` | 지원 형식만 스캔 |
| `test_compute_file_hash` | SHA-256 해시 일관성 |
| `test_parse_document_txt` | TXT 파싱 |
| `test_parse_document_unsupported` | 미지원 형식 빈 리스트 |
| `test_chunk_texts` | 텍스트 청킹 |
| `test_detect_changes_new_files` | 신규 파일 감지 |
| `test_detect_changes_deleted_files` | 삭제 파일 감지 |

### batch/batch.py 오케스트레이션 (2 tests)
| 테스트 | 검증 내용 |
|---|---|
| `test_run_full_mode_empty` | 전체 모드 초기화 동작 |
| `test_run_incremental_no_changes` | 변경 없을 때 건너뛰기 |

### backend 모듈 (4 tests)
| 테스트 | 검증 내용 |
|---|---|
| `test_search_returns_context_and_sources` | RAG 하이브리드 검색 결과 |
| `test_search_handles_failure` | 검색 실패 시 Graceful Degradation |
| `test_new_session` | 세션 생성 API |
| `test_chat_empty_message` | 빈 메시지 validation |

### Expected Results
- **Total Tests**: 19
- **Expected**: 19 passed, 0 failed
- **외부 서비스 불필요**: 모든 테스트는 mock 기반으로 KùzuDB/OpenAI 없이 실행 가능

## Fix Failing Tests

테스트 실패 시:
1. `pytest tests/ -v --tb=long` 으로 상세 traceback 확인
2. import 오류 → `PYTHONPATH=. pytest tests/ -v` 로 재시도
3. mock 관련 오류 → 대상 모듈의 import 경로 확인
