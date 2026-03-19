/** MessageInput 컴포넌트 - 입력 영역.
 *
 * textarea 자동 높이 조절, Enter/Shift+Enter 키 처리,
 * 스트리밍 중 Stop 버튼 전환을 담당한다.
 */

import { state } from "../state.js";

const MAX_HEIGHT = 150;
const MAX_LENGTH = 2000;

let inputEl;
let sendBtnEl;
let onSendCallback;
let onStopCallback;
let isComposing = false;

const SEND_ICON = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13"/><path d="M22 2L15 22L11 13L2 9L22 2Z"/></svg>';
const STOP_ICON = '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>';

export function initMessageInput({ onSend, onStop }) {
    inputEl = document.getElementById("messageInput");
    sendBtnEl = document.getElementById("sendBtn");
    onSendCallback = onSend;
    onStopCallback = onStop;

    inputEl.addEventListener("input", updateState);
    inputEl.addEventListener("keydown", handleKeyDown);
    inputEl.addEventListener("compositionstart", () => { isComposing = true; });
    inputEl.addEventListener("compositionend", () => { isComposing = false; });
    sendBtnEl.addEventListener("click", handleClick);
}

/** 입력값과 스트리밍 상태에 따라 전송/Stop 버튼 전환 + textarea 높이 자동 조절 */
export function updateState() {
    if (state.isStreaming) {
        sendBtnEl.disabled = false;
        sendBtnEl.innerHTML = STOP_ICON;
        sendBtnEl.title = "중지";
        sendBtnEl.classList.add("stop-mode");
    } else {
        sendBtnEl.innerHTML = SEND_ICON;
        sendBtnEl.title = "전송";
        sendBtnEl.classList.remove("stop-mode");
        sendBtnEl.disabled = !inputEl.value.trim();
    }
    autoResize();
    updateCharCount();
}

export function reset() {
    inputEl.value = "";
    inputEl.style.height = "auto";
    sendBtnEl.disabled = true;
}

export function focus() {
    inputEl.focus();
}

export function getValue() {
    return inputEl.value.trim();
}

/** Enter: 전송, Shift+Enter: 줄바꿈 */
function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        if (isComposing) return;
        if (!state.isStreaming && inputEl.value.trim()) {
            onSendCallback(inputEl.value.trim());
        }
    }
}

function handleClick() {
    if (state.isStreaming) {
        onStopCallback();
    } else {
        const text = getValue();
        if (text) onSendCallback(text);
    }
}

function autoResize() {
    inputEl.style.height = "auto";
    inputEl.style.height = Math.min(inputEl.scrollHeight, MAX_HEIGHT) + "px";
}

function updateCharCount() {
    const len = inputEl.value.length;
    const hint = document.querySelector(".input-hint");
    if (!hint) return;
    if (len > MAX_LENGTH * 0.9) {
        hint.textContent = `${len}/${MAX_LENGTH}자`;
        hint.classList.add("char-warning");
    } else {
        hint.textContent = "Enter로 전송 · Shift+Enter로 줄바꿈";
        hint.classList.remove("char-warning");
    }
}
