# Batch Unit - Code Generation Plan

## Unit Context
- **Unit**: Unit 3 - Batch
- **디렉토리**: `batch/` + `shared/`
- **스토리**: US-07 (수동 임베딩), US-08 (증분), US-09 (.bat), US-10 (전체 재임베딩), US-11 (문서 배치)
- **의존**: 내부 OpenAI API, ChromaDB, KùzuDB, SQLite

## Code Generation Steps

### Step 1: 프로젝트 구조 생성
- [x] 디렉토리 생성: `shared/`, `batch/`, `documents/`, `data/`
- [x] `shared/__init__.py`, `batch/__init__.py` 생성
- [x] `requirements.txt` 생성 (프로젝트 루트)

### Step 2: shared/config.py
- [x] 설정 모듈 생성 (DB 경로, API URL, 모델명, 청크 크기 등)
- [x] 관련: DP-06 (Configuration Externalization)

### Step 3: shared/embeddings.py
- [x] OpenAI 임베딩 API 호출 모듈 생성
- [x] 관련: US-07, US-08

### Step 4: shared/db.py
- [x] ChromaDB 접근 (upsert, search, delete)
- [x] KùzuDB 접근 (upsert_entities, search_related, delete_by_doc)
- [x] SQLite 접근 (문서 메타데이터, Batch 이력)
- [x] 관련: DP-02 (Idempotent), US-07, US-08

### Step 5: batch/embedding.py
- [x] 문서 파싱 (LangChain 로더: .txt, .csv, .md)
- [x] 텍스트 청킹 (RecursiveCharacterTextSplitter)
- [x] 엔티티 추출 (LLM 프롬프트 + Pydantic 스키마)
- [x] 변경 감지 (SHA-256 해시 비교)
- [x] 관련: BR-01~BR-04, BR-07, US-07, US-08, US-11

### Step 6: batch/batch.py
- [x] CLI 진입점 (argparse: --full 옵션)
- [x] 메인 오케스트레이션 (증분/전체 모드)
- [x] 진행률 출력 (Rich)
- [x] 결과 요약 출력
- [x] 관련: DP-01 (Fail-Safe), DP-04 (Progress), BR-05, BR-08, US-07, US-10

### Step 7: batch/run_embedding.bat
- [x] Windows .bat 파일 생성
- [x] 관련: US-09

### Step 8: Unit Tests
- [x] tests/test_shared_db.py - DB 접근 테스트
- [x] tests/test_shared_embeddings.py - 임베딩 호출 테스트
- [x] tests/test_batch_embedding.py - 파싱, 청킹, 변경 감지 테스트
- [x] tests/test_batch_main.py - CLI 및 오케스트레이션 테스트

### Step 9: Documentation
- [x] `aidlc-docs/construction/batch/code/code-summary.md` 생성

## Story Traceability

| Step | US-07 | US-08 | US-09 | US-10 | US-11 |
|---|---|---|---|---|---|
| Step 2 (config) | ✓ | ✓ | | ✓ | |
| Step 3 (embeddings) | ✓ | ✓ | | ✓ | |
| Step 4 (db) | ✓ | ✓ | | ✓ | ✓ |
| Step 5 (embedding) | ✓ | ✓ | | | ✓ |
| Step 6 (batch) | ✓ | ✓ | | ✓ | |
| Step 7 (.bat) | | | ✓ | | |
| Step 8 (tests) | ✓ | ✓ | ✓ | ✓ | ✓ |
