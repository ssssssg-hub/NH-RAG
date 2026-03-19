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
        .replace(/```(\w*)\n([\s\S]*?)```/g, "<pre><code>$2</code></pre>")
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/^- (.+)$/gm, "<li>$1</li>")
        .replace(/(<li>.*<\/li>\n?)+/g, "<ul>$&</ul>")
        .replace(/\n/g, "<br>");
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
