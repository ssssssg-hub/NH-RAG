# Backend Unit - Code Summary

## 생성된 파일

### backend/
| 파일 | 역할 |
|---|---|
| `backend/__init__.py` | 패키지 초기화 |
| `backend/app.py` | FastAPI 서버, SSE 스트리밍, 세션 관리, 정적 파일 서빙 |
| `backend/rag_engine.py` | Vector+Graph 하이브리드 검색, RRF 결합, LLM 스트리밍 |

### tests/
| 파일 | 테스트 대상 |
|---|---|
| `tests/test_backend_rag_engine.py` | RAG 검색, 에러 처리 |
| `tests/test_backend_app.py` | API 엔드포인트, SSE |

## API 엔드포인트

| Method | Path | 설명 |
|---|---|---|
| POST | `/api/chat` | 채팅 질의 (SSE 스트리밍 응답) |
| POST | `/api/chat/new` | 새 세션 생성 |
| GET | `/` | 프론트엔드 정적 파일 서빙 |

## SSE 이벤트 형식

| event | data | 설명 |
|---|---|---|
| session | `{"session_id": "xxx"}` | 세션 ID |
| token | 텍스트 | LLM 응답 토큰 |
| sources | `[{"file_name": "...", "excerpt": "..."}]` | 출처 정보 |
| done | 빈 문자열 | 스트림 종료 |
| error | 에러 메시지 | 에러 발생 |

## 실행 방법

```bash
python -m backend.app
# → http://localhost:8080
```

## Story 구현 현황
- [x] US-01: 질문 입력 및 전송 (POST /api/chat)
- [x] US-02: 스트리밍 응답 (SSE)
- [x] US-03: 하이브리드 검색 기반 답변 (RAG Engine)
- [x] US-04: 출처 표시 (sources 이벤트)
- [x] US-05: 세션 내 대화 이력 (in-memory sessions)
- [x] US-06: 새 대화 시작 (POST /api/chat/new)
