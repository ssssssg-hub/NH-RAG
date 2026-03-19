# Unit of Work

## 분해 전략
- **물리적 구조**: 3개 Unit (frontend / backend / batch) + shared 공통 모듈
- **논리적 분리**: 각 Unit 내부에서 모듈(파일) 단위로 관심사 분리
- **코드 구현 방침**: 클린하면서도 가볍게 (과도한 추상화 지양)
- **공통 모듈**: DB 접근, 설정, 임베딩 호출은 shared로 중복 제거

---

## 프로젝트 전체 구조

```
nh-rag/
  shared/              # 공통 모듈
    config.py          # 설정 (DB 경로, API URL 등)
    db.py              # ChromaDB, KùzuDB, SQLite 접근
    embeddings.py      # OpenAI API 임베딩 호출
  backend/             # Unit 2
    app.py             # FastAPI 서버
    rag_engine.py      # RAG 검색 로직
  batch/               # Unit 3
    batch.py           # 임베딩 실행 스크립트
    embedding.py       # 문서 파싱, 청킹, 엔티티 추출
    run_embedding.bat  # Windows 스케줄러용
  frontend/            # Unit 1
    index.html
    css/style.css
    js/app.js
  documents/           # 임베딩 대상 문서 디렉토리
  data/                # SQLite DB, ChromaDB 데이터 저장
  requirements.txt     # Python 의존성 (통합)
```

---

## Shared: 공통 모듈

| 항목 | 내용 |
|---|---|
| **디렉토리** | `shared/` |
| **책임** | DB 접근 추상화, 설정 관리, 임베딩 API 호출 |
| **사용처** | Backend + Batch 공용 |

---

## Unit 1: Frontend

| 항목 | 내용 |
|---|---|
| **디렉토리** | `frontend/` |
| **기술** | VanillaJS + HTML + CSS |
| **논리 컴포넌트** | C1 (Frontend) |
| **책임** | 채팅 UI, SSE 스트리밍 수신, 출처 표시, 세션 내 대화 이력 |

---

## Unit 2: Backend

| 항목 | 내용 |
|---|---|
| **디렉토리** | `backend/` |
| **기술** | Python 3.11.9 + FastAPI |
| **논리 컴포넌트** | C2 (API Server) + C3 (RAG Engine) |
| **의존** | shared (config, db, embeddings) |
| **책임** | API 서버, 하이브리드 RAG 검색, LLM 스트리밍 |

---

## Unit 3: Batch

| 항목 | 내용 |
|---|---|
| **디렉토리** | `batch/` |
| **기술** | Python 3.11.9 스크립트 + .bat |
| **논리 컴포넌트** | C4 (Embedding Engine) + C5 (Batch Service) |
| **의존** | shared (config, db, embeddings) |
| **책임** | 문서 파싱/청킹, 임베딩, 엔티티 추출, 증분/전체 모드 |
