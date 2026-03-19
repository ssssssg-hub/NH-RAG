"""FastAPI 백엔드 서버.

SSE(Server-Sent Events) 기반 스트리밍 채팅 API를 제공하고,
frontend/ 디렉토리의 정적 파일을 서빙한다.
"""

import json
import logging
import sys
import uuid
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

app = FastAPI(title="NH-RAG", description="내부 문서 기반 RAG 채팅 서비스")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-Memory 세션 저장소: {session_id: [{"role": "user"|"assistant", "content": "..."}]}
sessions: dict[str, list[dict]] = {}

rag_engine = RAGEngine()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None


class NewSessionResponse(BaseModel):
    session_id: str


@app.post("/api/chat/new")
async def new_session() -> NewSessionResponse:
    session_id = str(uuid.uuid4())[:8]
    sessions[session_id] = []
    return NewSessionResponse(session_id=session_id)


@app.get("/api/chat/history")
async def chat_history(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
    return {"session_id": session_id, "messages": sessions[session_id]}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    session_id = request.session_id
    if not session_id or session_id not in sessions:
        session_id = str(uuid.uuid4())[:8]
        sessions[session_id] = []

    history = sessions[session_id]
    history.append({"role": "user", "content": request.message})

    # 컨텍스트 윈도우 초과 방지: 최근 20턴(40메시지)만 유지
    if len(history) > 40:
        sessions[session_id] = history[-40:]
        history = sessions[session_id]

    async def event_generator() -> AsyncGenerator[dict, None]:
        """SSE 이벤트 순서: session → token(반복) → sources → done"""
        try:
            context, sources = rag_engine.search(request.message)

            yield {"event": "session", "data": json.dumps({"session_id": session_id})}

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
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8080, reload=True)


if __name__ == "__main__":
    main()
