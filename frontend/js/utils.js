/** 유틸리티 함수 */

/** textContent를 이용한 XSS-safe HTML 이스케이프 */
export function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

/** 간이 마크다운 → HTML 변환 (코드블록, 인라인코드, 볼드, 리스트) */
export function renderMarkdown(text) {
    return text
        .replace(/```(\w*)\n([\s\S]*?)```/g, '<div class="code-block-wrapper"><button class="copy-code-btn" title="복사">📋</button><pre><code>$2</code></pre></div>')
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/^- (.+)$/gm, "<li>$1</li>")
        .replace(/(<li>.*<\/li>\n?)+/g, "<ul>$&</ul>")
        .replace(/\n/g, "<br>");
}

/** 코드블록 복사 버튼 이벤트를 바인딩한다. */
export function bindCopyButtons(container) {
    container.querySelectorAll(".copy-code-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const code = btn.nextElementSibling.textContent;
            copyToClipboard(code, btn);
        });
    });
}

/** 메시지 전체 복사 버튼을 추가한다. */
export function addMessageCopyButton(bodyEl, text) {
    const btn = createElement("button", {
        className: "copy-message-btn",
        textContent: "📋 복사",
    });
    btn.addEventListener("click", () => copyToClipboard(text, btn));
    bodyEl.appendChild(btn);
}

function copyToClipboard(text, btn) {
    navigator.clipboard.writeText(text).then(() => {
        const original = btn.textContent;
        btn.textContent = "✅ 복사됨";
        setTimeout(() => { btn.textContent = original; }, 1500);
    });
}

/** DOM 엘리먼트 생성 헬퍼. data-* 속성은 setAttribute로, 나머지는 프로퍼티로 설정. */
export function createElement(tag, props = {}) {
    const el = document.createElement(tag);
    for (const [key, value] of Object.entries(props)) {
        if (key === "className") el.className = value;
        else if (key.startsWith("data-")) el.setAttribute(key, value);
        else el[key] = value;
    }
    return el;
}
