# Backend Unit - Business Logic Model

## 1. 채팅 API 흐름 (SSE 스트리밍)

```
POST /api/chat {message, session_id?}
    |
    v
[세션 관리]
    |-- session_id 없으면 → 신규 세션 생성 (UUID)
    |-- session_id 있으면 → 메모리에서 세션 조회
    |-- 사용자 메시지를 history에 추가
    |
    v
[RAG 검색]
    |
    +-- [질의 임베딩] shared/embeddings.embed_text(query)
    |
    +-- [Vector 검색] ChromaDB.search(embedding, top_k=5)
    |       → ContextChunk 리스트
    |
    +-- [엔티티 추출] LLM으로 질의에서 엔티티명 추출
    |
    +-- [Graph 검색] KùzuDB.search_related(entity_names, top_k=5)
    |       → 관련 엔티티/관계 리스트
    |
    +-- [결과 결합] Reciprocal Rank Fusion
    |       → 정렬된 context 리스트
    |
    v
[프롬프트 구성]
    |-- system prompt + context + chat history + user query
    |
    v
[LLM 스트리밍 호출]
    |-- OpenAI ChatCompletion (stream=True)
    |-- 토큰 단위로 SSE event 전송: {event: "token", data: "텍스트"}
    |
    v
[응답 완료]
    |-- assistant 메시지를 history에 추가
    |-- 출처 정보 SSE 전송: {event: "sources", data: [Source]}
    |-- 완료 SSE 전송: {event: "done"}
```

## 2. 새 세션 API

```
POST /api/chat/new
    → {session_id: "새 UUID"}
```

## 3. 세션 관리

- 메모리 내 dict로 세션 관리 (브라우저 닫으면 클라이언트에서 세션 폐기)
- 서버 재시작 시 세션 초기화 (세션 기반이므로 문제 없음)
- 세션당 최대 대화 이력: 최근 20턴 (context window 관리)

## 4. Reciprocal Rank Fusion (RRF)

```
score(doc) = Σ 1 / (k + rank_i(doc))
- k = 60 (상수)
- rank_i = i번째 검색 시스템에서의 순위
```

Vector 결과와 Graph 결과를 RRF로 결합하여 최종 context 순위 결정.

## 5. 정적 파일 서빙

- FastAPI StaticFiles로 `frontend/` 디렉토리 서빙
- `/` 접속 시 `frontend/index.html` 반환
