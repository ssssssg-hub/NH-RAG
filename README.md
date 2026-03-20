# NH-RAG

내부망 환경에서 사내 문서를 기반으로 질의응답하는 RAG(Retrieval-Augmented Generation) 채팅 서비스

Vector(ChromaDB) + Graph(KùzuDB) 하이브리드 검색과 RRF(Reciprocal Rank Fusion) 결합을 통해 정확도 높은 문서 검색을 수행하고, LLM 스트리밍 응답을 제공함

## 주요 기능

- **하이브리드 검색**: ChromaDB 벡터 검색 + KùzuDB 지식 그래프 검색을 RRF로 결합
- **SSE 스트리밍 응답**: 실시간 토큰 단위 응답 스트리밍
- **자동 엔티티 추출**: 문서 임베딩 시 LLM 기반 엔티티/관계 자동 추출 → 지식 그래프 구축
- **증분 임베딩**: SHA-256 해시 기반 변경 감지로 수정된 문서만 재처리
- **대화 이력 관리**: In-Memory 세션 기반 멀티턴 대화 지원 (최근 20턴)
- **출처 표시**: 답변에 참조된 문서 출처를 접이식 UI로 제공
- **Graceful Degradation**: KùzuDB 장애 시 Vector 검색만으로 자동 전환
- **다크 테마 UI**: ChatGPT/Claude 스타일의 채팅 인터페이스

## 프로젝트 구조

```
nh-rag/
├── shared/                  # 공통 모듈
│   ├── config.py            # 환경변수 기반 설정 관리
│   ├── db.py                # ChromaDB, KùzuDB, SQLite Repository
│   └── embeddings.py        # 로컬 임베딩 (sentence-transformers / fastembed)
├── backend/                 # FastAPI 백엔드
│   ├── app.py               # API 서버 (SSE, 세션, 정적 파일 서빙)
│   └── rag_engine.py        # RAG 검색 엔진 (Vector+Graph+RRF+LLM)
├── batch/                   # 문서 임베딩 배치
│   ├── batch.py             # CLI 진입점
│   ├── embedding.py         # 파싱, 청킹, 엔티티 추출, 변경 감지
│   └── run_embedding.bat    # Windows 스케줄러용 실행 스크립트
├── frontend/                # VanillaJS 프론트엔드 (ES Modules)
│   ├── index.html
│   ├── css/
│   │   ├── base.css         # 리셋, CSS 변수, 공통
│   │   ├── header.css
│   │   ├── chat.css         # 메시지, 웰컴, 타이핑
│   │   ├── input.css
│   │   └── sources.css      # 출처 접이식 UI
│   └── js/
│       ├── app.js           # 진입점 (컴포넌트 조합)
│       ├── state.js         # 전역 상태
│       ├── utils.js         # 마크다운 렌더링, DOM 헬퍼
│       └── components/
│           ├── api.js       # API 통신 + SSE 파싱
│           ├── Header.js
│           ├── ChatArea.js  # 메시지 렌더링, SSE 이벤트 처리
│           ├── MessageInput.js
│           └── Sources.js
├── tests/                   # 단위 테스트
├── documents/               # 임베딩 대상 문서 디렉토리
├── data/                    # 런타임 데이터 (SQLite, ChromaDB, KùzuDB)
├── requirements.txt
└── .env                     # 환경변수 설정
```

## 기술 스택

| 구분          | 기술                                             |
| ------------- | ------------------------------------------------ |
| Backend       | Python 3.11, FastAPI, uvicorn, sse-starlette     |
| Vector DB     | ChromaDB (임베디드, 코사인 유사도)               |
| Graph DB      | KùzuDB (임베디드, Cypher 쿼리)                   |
| Metadata DB   | SQLite                                           |
| LLM           | OpenAI 호환 API (채팅/엔티티 추출 전용)          |
| Embedding     | sentence-transformers + 한국어 모델 (로컬, CPU)  |
| 문서 처리     | LangChain (로더, RecursiveCharacterTextSplitter) |
| Frontend      | VanillaJS (ES Modules), 순수 CSS                 |
| 테스트        | pytest, pytest-asyncio                           |

## 아키텍처

### 시스템 구성도

```
┌─────────────────────────────────────────────────────────────────┐
│  Frontend (VanillaJS)                                           │
│  ┌───────────┐  ┌──────────────┐  ┌──────────┐  ┌───────────┐  │
│  │  Header   │  │  ChatArea    │  │  Sources  │  │  Input    │  │
│  └───────────┘  └──────┬───────┘  └──────────┘  └─────┬─────┘  │
│                        │ SSE Stream                    │ POST   │
└────────────────────────┼───────────────────────────────┼────────┘
                         │                               │
                    ┌────▼───────────────────────────────▼────┐
                    │  FastAPI Backend (app.py)                │
                    │  ┌────────────────────────────────────┐  │
                    │  │  In-Memory Session (대화 이력)     │  │
                    │  └────────────────────────────────────┘  │
                    │  ┌────────────────────────────────────┐  │
                    │  │  RAG Engine (rag_engine.py)        │  │
                    │  │                                    │  │
                    │  │  1. Query → 벡터 임베딩            │  │
                    │  │  2. Query → LLM 엔티티 추출       │  │
                    │  │  3. Vector + Graph 검색            │  │
                    │  │  4. RRF 결합 → 컨텍스트 구성      │  │
                    │  │  5. LLM 스트리밍 응답 생성         │  │
                    │  └──────┬──────────────┬──────────────┘  │
                    └─────────┼──────────────┼─────────────────┘
                              │              │
              ┌───────────────┼──────────────┼───────────────┐
              │               ▼              ▼               │
              │  ┌──────────────┐  ┌──────────────┐          │
              │  │  ChromaDB    │  │   KùzuDB     │          │
              │  │  (Vector)    │  │   (Graph)    │          │
              │  └──────────────┘  └──────────────┘          │
              │         ┌──────────────┐                     │
              │         │   SQLite     │                     │
              │         │  (Metadata)  │                     │
              │         └──────────────┘                     │
              │              data/                           │
              └──────────────────────────────────────────────┘

                    ┌─────────────────────────────────┐
                    │  Batch (batch.py)                │
                    │                                  │
                    │  documents/ → 파싱 → 청킹        │
                    │  → 벡터 임베딩 (ChromaDB)        │
                    │  → LLM 엔티티 추출 (KùzuDB)     │
                    │  → SHA-256 변경 감지 (SQLite)    │
                    └─────────────────────────────────┘

                    ┌─────────────────────────────────┐
                    │  OpenAI 호환 API (내부망 LLM)    │
                    │  - 채팅: /chat/completions       │
                    └─────────────────────────────────┘

                    ┌─────────────────────────────────┐
                    │  로컬 임베딩 (sentence-transformers) │
                    │  - 한국어 모델 (CPU)             │
                    └─────────────────────────────────┘
```

### 검색 흐름 (RAG Pipeline)

```
사용자 질의
    │
    ├──→ 벡터 임베딩 ──→ ChromaDB 코사인 유사도 검색 ──→ 문서 청크 (ranked)
    │                                                         │
    ├──→ LLM 엔티티 추출 ──→ KùzuDB 1-hop 관계 탐색 ──→ 관계 트리플
    │                                                         │
    └──→ RRF (K=60) 결합 ◄───────────────────────────────────┘
              │
              ▼
    [참조 문서 청크] + [관련 지식 그래프]
              │
              ▼
    System Prompt + Context + 대화 이력 + 질의
              │
              ▼
    LLM 스트리밍 응답 (SSE)
```

### 임베딩 흐름 (Batch Pipeline)

```
documents/ 스캔
    │
    ├──→ SHA-256 해시 비교 (SQLite) ──→ 변경 없음: SKIP
    │
    ├──→ 신규/변경 문서
    │       │
    │       ├──→ LangChain 파싱 (.txt/.csv/.md)
    │       ├──→ RecursiveCharacterTextSplitter 청킹
    │       ├──→ 로컬 임베딩 (sentence-transformers) → ChromaDB 저장
    │       └──→ LLM 엔티티/관계 추출 → KùzuDB 저장
    │
    └──→ 삭제된 문서 ──→ ChromaDB + KùzuDB + SQLite 정리
```

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

> 가상환경(venv)을 사용하려면 `python -m venv venv && source venv/bin/activate` (Windows: `venv\Scripts\activate`) 후 설치

### 2. 환경변수 설정

`.env` 파일을 프로젝트 루트에 생성:

```env
NH_RAG_OPENAI_API_BASE=<OpenAI 호환 API 엔드포인트>
NH_RAG_OPENAI_API_KEY=<API 키>
NH_RAG_CHAT_MODEL=<채팅 모델명>
NH_RAG_EMBEDDING_MODEL_PATH=./models/ko-sroberta
```

LLM API는 OpenAI 호환 API(`/v1/chat/completions`)를 제공하는 서버라면 어떤 것이든 사용 가능함

임베딩은 sentence-transformers로 로컬 실행하며, 모델 파일을 `models/` 디렉토리에 배치해야 함

> 외부망에서 모델 다운로드 후 내부망으로 복사:
> ```python
> from sentence_transformers import SentenceTransformer
> m = SentenceTransformer("jhgan/ko-sroberta-multitask")
> m.save("./models/ko-sroberta")
> ```

선택적 환경변수:

| 변수                        | 기본값                    | 설명                                          |
| --------------------------- | ------------------------- | --------------------------------------------- |
| `NH_RAG_EMBEDDING_BACKEND`  | `local`                   | 임베딩 백엔드 (`local` 또는 `fastembed`)       |
| `NH_RAG_EMBEDDING_MODEL_PATH` | `./models/ko-sroberta` | sentence-transformers 모델 경로               |
| `NH_RAG_DOCUMENTS_DIR`      | `./documents`             | 임베딩 대상 문서 경로                         |
| `NH_RAG_DATA_DIR`           | `./data`                  | 데이터 저장 경로                              |
| `NH_RAG_CHUNK_SIZE`         | `1500`                    | 청크 크기 (문자 수)                           |
| `NH_RAG_CHUNK_OVERLAP`      | `150`                     | 청크 오버랩 (문자 수)                         |
| `NH_RAG_VECTOR_TOP_K`       | `5`                       | 벡터 검색 결과 수                             |
| `NH_RAG_GRAPH_TOP_K`        | `5`                       | 그래프 검색 결과 수                           |

### 3. 문서 임베딩

`documents/` 디렉토리에 문서 파일(.txt, .csv, .md)을 배치한 후 배치를 실행:

```bash
# 증분 임베딩 (변경된 문서만 처리)
python -m batch.batch

# 전체 재임베딩 (기존 데이터 초기화)
python -m batch.batch --full
```

### 4. 서버 실행

```bash
python -m backend.app
```

브라우저에서 `http://localhost:8080` 으로 접속

## API

| Method | Endpoint                        | 설명                                 |
| ------ | ------------------------------- | ------------------------------------ |
| `POST` | `/api/chat`                     | 채팅 메시지 전송 (SSE 스트리밍 응답) |
| `POST` | `/api/chat/new`                 | 새 세션 생성                         |
| `GET`  | `/api/chat/history?session_id=` | 대화 이력 조회                       |
| `GET`  | `/`                             | 프론트엔드 정적 파일                 |

### POST /api/chat

```json
{
  "message": "사내 규정에 대해 알려줘",
  "session_id": "abc12345"
}
```

SSE 이벤트 스트림으로 응답:

| 이벤트    | 데이터                                     | 설명                |
| --------- | ------------------------------------------ | ------------------- |
| `session` | `{"session_id": "..."}`                    | 세션 ID (첫 이벤트) |
| `token`   | 텍스트 조각                                | 응답 토큰 (반복)    |
| `sources` | `[{"file_name": "...", "excerpt": "..."}]` | 참조 문서 출처      |
| `done`    | 빈 문자열                                  | 응답 완료           |
| `error`   | 에러 메시지                                | 오류 발생           |

## 테스트

```bash
pytest
```

## 지원 문서 형식

- `.txt` - 텍스트 파일
- `.csv` - CSV 파일
- `.md` - 마크다운 파일
