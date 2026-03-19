# Backend Unit - NFR Design Patterns

## DP-BE01: Async Streaming (성능)
- FastAPI async 엔드포인트 + SSE EventSourceResponse
- LLM 스트리밍 호출을 async generator로 처리
- 요청 간 블로킹 없음

## DP-BE02: Graceful Degradation (안정성)
- 검색 실패 → context 없이 LLM 호출
- LLM 실패 → SSE error 이벤트 전송
- 전체 실패 → 사용자 친화적 에러 메시지

## DP-BE03: In-Memory Session Store (확장성)
- dict 기반 세션 저장 (현재)
- 추후 Redis 등으로 교체 가능하도록 SessionStore 인터페이스 분리

## DP-BE04: Layered Architecture (유지보수성)
- app.py: 라우터 (HTTP 레이어)
- rag_engine.py: 비즈니스 로직 (검색 + LLM)
- shared/db.py: 데이터 접근
