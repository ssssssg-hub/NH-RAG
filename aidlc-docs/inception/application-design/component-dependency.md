# Component Dependencies

## 의존성 매트릭스

| 컴포넌트 | 의존 대상 | 통신 방식 |
|---|---|---|
| C1: Frontend | C2: API Server | HTTP REST + SSE |
| C2: API Server | S1: ChatService | 내부 함수 호출 |
| S1: ChatService | C3: RAG Engine | 내부 함수 호출 |
| C3: RAG Engine | C6: ChromaDB Repo | 내부 함수 호출 |
| C3: RAG Engine | C6: Kuzu Repo | 내부 함수 호출 |
| C3: RAG Engine | 내부 OpenAI API | HTTP (임베딩 + LLM) |
| C5: Batch Service | S2: EmbeddingService | 내부 함수 호출 |
| S2: EmbeddingService | C4: Embedding Engine | 내부 함수 호출 |
| C4: Embedding Engine | C6: ChromaDB Repo | 내부 함수 호출 |
| C4: Embedding Engine | C6: Kuzu Repo | 내부 함수 호출 |
| C4: Embedding Engine | C6: SQLite Repo | 내부 함수 호출 |
| C4: Embedding Engine | 내부 OpenAI API | HTTP (임베딩 + 엔티티 추출) |

## 데이터 흐름

### 채팅 흐름 (실시간)
```
사용자 질문
    |
    v
[Frontend] --POST /api/chat--> [API Server]
    |                               |
    |                          [ChatService]
    |                               |
    |                          [RAG Engine]
    |                           /       \
    |                    [ChromaDB]   [KùzuDB]
    |                           \       /
    |                        결과 결합 (RRF)
    |                               |
    |                        [내부 OpenAI API]
    |                               |
    |<------SSE 스트리밍 응답--------+
    |
    v
응답 + 출처 표시
```

### 임베딩 흐름 (배치)
```
관리자 실행 (CLI / .bat)
    |
    v
[Batch Service]
    |
[EmbeddingService]
    |
[Embedding Engine]
    |
    +-- 변경 감지 (SQLite 해시 비교)
    |
    +-- 문서 파싱/청킹
    |
    +-- 임베딩 (내부 OpenAI API)
    |       |
    |       +--> [ChromaDB] 벡터 저장
    |
    +-- 엔티티 추출 (내부 OpenAI API)
    |       |
    |       +--> [KùzuDB] 그래프 저장
    |
    +-- 메타데이터 업데이트 --> [SQLite]
    |
    v
실행 결과 출력
```

## 외부 의존성

| 외부 시스템 | 용도 | 통신 |
|---|---|---|
| 내부 OpenAI API | LLM 응답 생성 + 텍스트 임베딩 + 엔티티 추출 | HTTP (OpenAI 호환) |
| ChromaDB | 벡터 저장/검색 | Python 클라이언트 |
| KùzuDB | 지식 그래프 저장/검색 | 임베디드 파일 기반 |
