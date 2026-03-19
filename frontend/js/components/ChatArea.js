/** ChatArea 컴포넌트 - 메시지 목록 + 웰컴 화면.
 *
 * SSE 이벤트 타입별 처리:
 * - session: 서버가 할당한 세션 ID 저장
 * - token: 스트리밍 토큰을 메시지 영역에 실시간 추가
 * - sources: 참조 문서 출처를 접이식 UI로 렌더링
 * - error: 에러 메시지 표시
 * - done: 스트리밍 완료 (별도 처리 없음)
 */

import { state } from "../state.js";
import { createElement, renderMarkdown, bindCopyButtons, addMessageCopyButton } from "../utils.js";
import { sendChat, processSSEStream, fetchHistory } from "./api.js";
import { renderSources } from "./Sources.js";

const WELCOME_HTML =
    '<div class="welcome" data-testid="welcome-message">' +
        '<div class="welcome-icon">🧠</div>' +
        "<h2>NH-RAG</h2>" +
        "<p>사내 문서 기반 AI 어시스턴트</p>" +
        '<div class="suggestions">' +
            '<button class="suggestion-chip" data-q="사내 규정에 대해 알려줘">📋 사내 규정 안내</button>' +
            '<button class="suggestion-chip" data-q="최근 업데이트된 문서가 있어?">📄 최근 문서 확인</button>' +
            '<button class="suggestion-chip" data-q="업무 프로세스를 설명해줘">⚙️ 업무 프로세스</button>' +
        "</div>" +
    "</div>";

const STATUS_MESSAGES = {
    searching: "🔍 문서 검색 중...",
    generating: "✍️ 응답 생성 중...",
};

let chatArea;
let onSendCallback;
let currentAbort = null;

export function initChatArea({ onSend }) {
    chatArea = document.getElementById("chatArea");
    onSendCallback = onSend;
    bindSuggestionChips();
}

export function showWelcome() {
    chatArea.innerHTML = WELCOME_HTML;
    bindSuggestionChips();
}

/** 스트리밍 중이면 취소한다. */
export function stopStreaming() {
    if (currentAbort) {
        currentAbort();
        currentAbort = null;
    }
}

export async function handleSend(text) {
    removeWelcome();
    appendMessage("user", text);

    state.isStreaming = true;
    const aiRow = appendMessage("ai", "");
    const contentEl = aiRow.querySelector(".message-content");
    showStatusIndicator(contentEl, "searching");

    try {
        const { response, abort } = sendChat(text);
        currentAbort = abort;

        const res = await response;
        showStatusIndicator(contentEl, "generating");

        // 스트리밍 중에는 textContent로 실시간 표시, 완료 후 마크다운 렌더링
        const fullText = await processSSEStream(res, (event, data) => {
            handleSSEEvent(event, data, contentEl, aiRow);
        });
        if (fullText) {
            contentEl.innerHTML = renderMarkdown(fullText);
            bindCopyButtons(contentEl);
            addMessageCopyButton(aiRow.querySelector(".message-body"), fullText);
        }
    } catch (e) {
        if (e.name === "AbortError") {
            // 사용자가 취소한 경우
            removeStatusIndicator(contentEl);
            if (!contentEl.textContent) {
                contentEl.textContent = "응답이 취소되었습니다.";
                aiRow.classList.add("message-cancelled");
            } else {
                contentEl.innerHTML = renderMarkdown(contentEl.textContent);
                bindCopyButtons(contentEl);
                addMessageCopyButton(aiRow.querySelector(".message-body"), contentEl.textContent);
            }
        } else {
            contentEl.textContent = "응답 생성에 실패했습니다. 다시 시도해주세요.";
            aiRow.classList.add("message-error");
        }
    } finally {
        currentAbort = null;
        state.isStreaming = false;
    }
}

function handleSSEEvent(event, data, contentEl, aiRow) {
    switch (event) {
        case "session":
            try { state.sessionId = JSON.parse(data).session_id; } catch {}
            break;
        case "token":
            removeStatusIndicator(contentEl);
            contentEl.textContent += data;
            scrollToBottom();
            break;
        case "no_results":
            removeStatusIndicator(contentEl);
            showNoResultsBanner(aiRow.querySelector(".message-body"));
            break;
        case "sources":
            try {
                const sources = JSON.parse(data);
                if (sources.length) renderSources(aiRow.querySelector(".message-body"), sources);
            } catch {}
            break;
        case "error":
            contentEl.textContent = data || "응답 생성에 실패했습니다.";
            break;
    }
}

/** 메시지 행(row)을 생성하여 채팅 영역에 추가한다. */
function appendMessage(role, text) {
    const isUser = role === "user";
    const row = createElement("div", { className: `message-row ${role}`, "data-testid": `${role}-message` });
    const inner = createElement("div", { className: "message-inner" });
    const avatar = createElement("div", {
        className: `avatar ${isUser ? "user-avatar" : "ai-avatar"}`,
        textContent: isUser ? "👤" : "🧠",
    });
    const body = createElement("div", { className: "message-body" });
    const roleName = createElement("div", { className: "message-role", textContent: isUser ? "나" : "NH-RAG" });
    const content = createElement("div", { className: "message-content" });
    if (isUser) content.textContent = text;

    body.append(roleName, content);
    inner.append(avatar, body);
    row.appendChild(inner);
    chatArea.appendChild(row);
    scrollToBottom();
    return row;
}

function showStatusIndicator(el, phase) {
    const msg = STATUS_MESSAGES[phase] || "";
    el.innerHTML = `<div class="status-indicator">${msg}</div>`;
}

function removeStatusIndicator(el) {
    const indicator = el.querySelector(".status-indicator");
    if (indicator) indicator.remove();
}

function removeWelcome() {
    const welcome = chatArea.querySelector(".welcome");
    if (welcome) welcome.remove();
}

function showNoResultsBanner(bodyEl) {
    const banner = createElement("div", {
        className: "no-results-banner",
        textContent: "⚠️ 관련 문서를 찾지 못했습니다. 임베딩된 문서가 없거나 질문과 관련된 내용이 없을 수 있습니다.",
    });
    bodyEl.insertBefore(banner, bodyEl.querySelector(".message-content").nextSibling);
}

function scrollToBottom() {
    chatArea.scrollTop = chatArea.scrollHeight;
}

/** 제안 칩 클릭 시 해당 텍스트로 메시지를 전송한다. */
function bindSuggestionChips() {
    chatArea.querySelectorAll(".suggestion-chip").forEach((chip) => {
        chip.addEventListener("click", () => onSendCallback(chip.getAttribute("data-q")));
    });
}

/** 서버에서 대화 이력을 불러와 화면에 복원한다. */
export async function restoreHistory() {
    const data = await fetchHistory(state.sessionId);
    if (!data || !data.messages || data.messages.length === 0) return;

    removeWelcome();
    for (const msg of data.messages) {
        const role = msg.role === "assistant" ? "ai" : msg.role;
        const row = appendMessage(role, "");
        const contentEl = row.querySelector(".message-content");
        if (role === "ai") {
            contentEl.innerHTML = renderMarkdown(msg.content);
            bindCopyButtons(contentEl);
            addMessageCopyButton(row.querySelector(".message-body"), msg.content);
        } else {
            contentEl.textContent = msg.content;
        }
    }
}
