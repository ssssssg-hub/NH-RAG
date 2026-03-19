# Components

## C1: Frontend (웹 채팅 UI)

| 항목 | 내용 |
|---|---|
| **기술** | VanillaJS + HTML + CSS |
| **책임** | 채팅 UI 렌더링, 사용자 입력 처리, SSE 스트리밍 수신, 출처 표시 |
| **인터페이스** | HTTP REST (질문 전송), SSE (스트리밍 응답 수신) |

**주요 역할:**
- 채팅 메시지 입력/전송 UI
- SSE를 통한 스트리밍 응답 실시간 렌더링
- 세션 내 대화 이력 표시 (클라이언트 메모리)
- 출처(문서명 + 원문 발췌) 표시
- 새 대화 시작 기능

---

## C2: API Server (백엔드)

| 항목 | 내용 |
|---|---|
| **기술** | Python 3.11.9 + FastAPI |
| **책임** | HTTP 요청 처리, SSE 스트리밍 응답, 서비스 레이어 호출 |
| **인터페이스** | REST API + SSE endpoint |

**주요 역할:**
- `/api/chat` - 채팅 질의 수신 및 SSE 스트리밍 응답
- `/api/chat/new` - 새 세션 생성
- 요청 유효성 검증
- 서비스 레이어로 위임

---

## C3: RAG Engine (검색 엔진)

| 항목 | 내용 |
|---|---|
| **기술** | Python (langchain 또는 자체 구현) |
| **책임** | Vector 검색 + Graph 검색 수행, 결과 결합, LLM 프롬프트 구성 및 호출 |
| **인터페이스** | 내부 Python 모듈 (Service에서 호출) |

**주요 역할:**
- 사용자 질의 임베딩 (내부 OpenAI API)
- ChromaDB Vector 유사도 검색
- KùzuDB Graph 엔티티/관계 검색
- 검색 결과 결합 (Reciprocal Rank Fusion)
- LLM 프롬프트 구성 및 스트리밍 호출
- 출처 정보 추출

---

## C4: Embedding Engine (임베딩 엔진)

| 항목 | 내용 |
|---|---|
| **기술** | Python |
| **책임** | 문서 파싱, 청킹, 임베딩, Vector/Graph DB 저장 |
| **인터페이스** | CLI 스크립트 (Batch 서비스에서 호출) |

**주요 역할:**
- 문서 파일 읽기 (.txt, .csv, .md)
- 문서 청킹 (적절한 크기로 분할)
- 텍스트 임베딩 (내부 OpenAI API)
- ChromaDB에 벡터 저장
- KùzuDB에 엔티티/관계 추출 및 저장
- 파일 해시 기반 변경 감지 (증분 임베딩)

---

## C5: Batch Service (배치 서비스)

| 항목 | 내용 |
|---|---|
| **기술** | Python 스크립트 + .bat 파일 |
| **책임** | 임베딩 실행 오케스트레이션, 증분/전체 모드 관리 |
| **인터페이스** | CLI (python batch.py [--full]) |

**주요 역할:**
- 증분 임베딩 실행 (기본)
- 전체 재임베딩 실행 (`--full` 옵션)
- 실행 결과 콘솔 출력 (처리 건수, 성공/실패)
- .bat 파일 제공 (Windows 스케줄러 등록용)

---

## C6: Data Access Layer (데이터 액세스)

| 항목 | 내용 |
|---|---|
| **기술** | Python (sqlite3, chromadb, kuzu) |
| **책임** | 각 DB에 대한 CRUD 추상화 |
| **인터페이스** | 내부 Python 모듈 |

**하위 모듈:**
- **ChromaDB Repository**: 벡터 저장/검색/삭제
- **KuzuRepository**: 그래프 노드/관계 저장/검색/삭제
- **SQLite Repository**: 세션 메타데이터, 문서 메타데이터(해시), Batch 실행 이력
