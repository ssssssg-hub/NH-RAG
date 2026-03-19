/** MessageInput 컴포넌트 - 입력 영역.
 *
 * textarea 자동 높이 조절과 Enter/Shift+Enter 키 처리를 담당한다.
 */

import { state } from "../state.js";

const MAX_HEIGHT = 150;

let inputEl;
let sendBtnEl;
let onSendCallback;

export function initMessageInput({ onSend }) {
    inputEl = document.getElementById("messageInput");
    sendBtnEl = document.getElementById("sendBtn");
    onSendCallback = onSend;

    inputEl.addEventListener("input", updateState);
    inputEl.addEventListener("keydown", handleKeyDown);
    sendBtnEl.addEventListener("click", submit);
}

/** 입력값과 스트리밍 상태에 따라 전송 버튼 활성화 + textarea 높이 자동 조절 */
export function updateState() {
    sendBtnEl.disabled = !inputEl.value.trim() || state.isStreaming;
    inputEl.style.height = "auto";
    inputEl.style.height = Math.min(inputEl.scrollHeight, MAX_HEIGHT) + "px";
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
        if (!sendBtnEl.disabled) submit();
    }
}

function submit() {
    const text = getValue();
    if (text && !state.isStreaming) onSendCallback(text);
}
