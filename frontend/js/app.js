/** NH-RAG 앱 진입점.
 *
 * 각 컴포넌트를 초기화하고 콜백으로 연결하는 조합(composition) 레이어.
 * 비즈니스 로직은 각 컴포넌트 내부에 캡슐화되어 있다.
 */

import { state } from "./state.js";
import { initHeader } from "./components/Header.js";
import { initChatArea, showWelcome, handleSend, stopStreaming, restoreHistory } from "./components/ChatArea.js";
import { initMessageInput, updateState, reset, focus } from "./components/MessageInput.js";
import { createSession } from "./components/api.js";

async function onSend(text) {
    reset();
    state.isStreaming = true;
    updateState();
    await handleSend(text);
    updateState();
    focus();
}

function onStop() {
    stopStreaming();
    updateState();
    focus();
}

async function onNewChat() {
    await createSession();
    showWelcome();
    reset();
    focus();
}

initHeader({ onNewChat });
initChatArea({ onSend });
initMessageInput({ onSend, onStop });
