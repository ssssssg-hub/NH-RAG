# Backend Unit - Code Generation Plan

## Unit Context
- **Unit**: Unit 2 - Backend
- **디렉토리**: `backend/`
- **스토리**: US-01~US-06
- **의존**: shared/, 내부 OpenAI API, ChromaDB, KùzuDB

## Steps

### Step 1: backend/rag_engine.py
- [x] 질의 임베딩 + Vector 검색 + Graph 검색
- [x] RRF 결합
- [x] 프롬프트 구성 + LLM 스트리밍 호출
- [x] 출처 생성

### Step 2: backend/app.py
- [x] FastAPI 앱 + SSE 스트리밍 엔드포인트
- [x] 세션 관리 (in-memory)
- [x] 정적 파일 서빙 (frontend/)
- [x] CORS 설정

### Step 3: Unit Tests
- [x] tests/test_backend_rag_engine.py
- [x] tests/test_backend_app.py

### Step 4: Documentation
- [x] aidlc-docs/construction/backend/code/code-summary.md
