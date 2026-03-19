/** API 통신 + SSE 스트림 처리 모듈.
 *
 * 백엔드의 SSE(Server-Sent Events) 응답을 ReadableStream으로 읽어
 * event/data 쌍을 파싱한 뒤 콜백으로 전달한다.
 */

import { state } from "../state.js";

const API = {
    CHAT: "/api/chat",
    NEW_SESSION: "/api/chat/new",
};

export async function createSession() {
    try {
        const res = await fetch(API.NEW_SESSION, { method: "POST" });
        state.sessionId = (await res.json()).session_id;
    } catch {
        state.sessionId = null;
    }
}

/** 세션 이력을 조회한다. 세션이 없거나 만료되면 null 반환. */
export async function fetchHistory(sessionId) {
    if (!sessionId) return null;
    try {
        const res = await fetch(`${API.CHAT}/history?session_id=${sessionId}`);
        if (!res.ok) return null;
        return await res.json();
    } catch {
        return null;
    }
}

/**
 * 채팅 메시지를 전송한다. AbortController를 반환하여 취소를 지원한다.
 * @returns {{ response: Promise<Response>, abort: Function }}
 */
export function sendChat(message) {
    const controller = new AbortController();
    const response = fetch(API.CHAT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, session_id: state.sessionId }),
        signal: controller.signal,
    }).then((res) => {
        if (!res.ok) throw new Error("서버 오류");
        return res;
    });
    return { response, abort: () => controller.abort() };
}

/**
 * SSE 스트림을 청크 단위로 읽어 이벤트를 파싱한다.
 *
 * SSE 프로토콜: "event: <type>\ndata: <payload>\n\n" 형식.
 * 네트워크 청크 경계가 줄 중간에 올 수 있으므로 buffer로 불완전한 줄을 보관한다.
 *
 * @param {Response} response - fetch 응답 (ReadableStream)
 * @param {Function} onEvent - (eventType, data) 콜백
 * @returns {string} 전체 응답 텍스트 (token 이벤트 누적)
 */
export async function processSSEStream(response, onEvent) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let eventType = "";
    let fullText = "";

    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            // 마지막 줄은 불완전할 수 있으므로 다음 청크와 합친다
            buffer = lines.pop() || "";

            for (const line of lines) {
                if (line.startsWith("event:")) {
                    eventType = line.slice(6).trim();
                } else if (line.startsWith("data:")) {
                    const data = line.slice(5).trim();
                    if (eventType === "token") fullText += data;
                    onEvent(eventType, data);
                }
            }
        }
    } catch (e) {
        // AbortError는 사용자가 취소한 것이므로 무시
        if (e.name !== "AbortError") throw e;
    }

    return fullText;
}
