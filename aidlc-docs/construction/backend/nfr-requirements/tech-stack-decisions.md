# Backend Unit - Tech Stack Decisions

| 기술 | 선택 | 근거 |
|---|---|---|
| 웹 프레임워크 | FastAPI | 비동기, SSE 지원, 자동 API 문서 |
| SSE | sse-starlette | FastAPI용 SSE 라이브러리 |
| ASGI 서버 | uvicorn | FastAPI 표준 서버 |
| OpenAI Client | openai | 내부 API 호출 (스트리밍) |
| 데이터 모델 | pydantic | 요청/응답 검증 |
| 정적 파일 | FastAPI StaticFiles | frontend/ 서빙 |
| DB 접근 | shared/db.py | ChromaDB, KùzuDB, SQLite (공유 모듈) |
