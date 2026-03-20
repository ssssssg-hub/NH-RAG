"""FastAPI 백엔드 서버.

SSE(Server-Sent Events) 기반 스트리밍 채팅 API를 제공하고,
frontend/ 디렉토리의 정적 파일을 서빙한다.
"""

import asyncio
import json
import logging
import sys
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.rag_engine import RAGEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    """서버 시작 시 임베딩 모델을 미리 로드하여 첫 질의 지연을 방지한다."""
    from shared.embeddings import embed_text
    await asyncio.to_thread(embed_text, "warm-up")
    logger.info("임베딩 모델 warm-up 완료")
    yield

app = FastAPI(title="NH-RAG", description="내부 문서 기반 RAG 채팅 서비스", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-Memory 세션 저장소: {session_id: {"messages": [...], "last_access": timestamp}}
SESSION_TTL = 3600  # 1시간 미사용 시 만료
MAX_SESSIONS = 100  # 최대 세션 수
sessions: dict[str, dict] = {}

rag_engine = RAGEngine()


def _cleanup_sessions():
    """만료된 세션을 제거한다. 최대 세션 수 초과 시 가장 오래된 세션부터 제거."""
    now = time.time()
    expired = [sid for sid, s in sessions.items() if now - s["last_access"] > SESSION_TTL]
    for sid in expired:
        del sessions[sid]

    # 최대 세션 수 초과 시 가장 오래된 세션 제거
    if len(sessions) > MAX_SESSIONS:
        sorted_sessions = sorted(sessions.items(), key=lambda x: x[1]["last_access"])
        for sid, _ in sorted_sessions[:len(sessions) - MAX_SESSIONS]:
            del sessions[sid]


def _get_or_create_session(session_id: str | None) -> tuple[str, list[dict]]:
    """세션을 조회하거나 새로 생성한다. 접근 시각을 갱신한다."""
    _cleanup_sessions()
    if session_id and session_id in sessions:
        sessions[session_id]["last_access"] = time.time()
        return session_id, sessions[session_id]["messages"]

    new_id = str(uuid.uuid4())[:8]
    sessions[new_id] = {"messages": [], "last_access": time.time()}
    return new_id, sessions[new_id]["messages"]


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None


class NewSessionResponse(BaseModel):
    session_id: str


@app.post("/api/chat/new")
async def new_session() -> NewSessionResponse:
    _cleanup_sessions()
    session_id = str(uuid.uuid4())[:8]
    sessions[session_id] = {"messages": [], "last_access": time.time()}
    return NewSessionResponse(session_id=session_id)


@app.get("/api/chat/history")
async def chat_history(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
    sessions[session_id]["last_access"] = time.time()
    return {"session_id": session_id, "messages": sessions[session_id]["messages"]}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    session_id, history = _get_or_create_session(request.session_id)

    history.append({"role": "user", "content": request.message})

    # 컨텍스트 윈도우 초과 방지: 최근 20턴(40메시지)만 유지
    if len(history) > 40:
        del history[:len(history) - 40]

    async def event_generator() -> AsyncGenerator[dict, None]:
        """SSE 이벤트 순서: session → token(반복) → sources → done"""
        try:
            context, sources = await asyncio.to_thread(rag_engine.search, request.message, history)

            yield {"event": "session", "data": json.dumps({"session_id": session_id})}

            # 검색 결과가 없으면 사용자에게 안내
            if not context:
                yield {"event": "no_results", "data": ""}

            full_response = ""
            async for event in rag_engine.generate_stream(request.message, context, history):
                if event["event"] == "token":
                    full_response += event["data"]
                yield {"event": event["event"], "data": event["data"]}

            if full_response:
                history.append({"role": "assistant", "content": full_response})

            if sources:
                sources_data = [s.model_dump() for s in sources]
                yield {"event": "sources", "data": json.dumps(sources_data, ensure_ascii=False)}

            yield {"event": "done", "data": ""}

        except Exception as e:
            logger.error(f"채팅 처리 실패: {e}")
            yield {"event": "error", "data": "응답 생성에 실패했습니다. 다시 시도해주세요."}

    return EventSourceResponse(event_generator())


# "/" 마운트는 모든 경로를 캐치하므로 API 라우트 등록 후 마지막에 설정
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


def main():
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8080, reload=False)


if __name__ == "__main__":
    main()
