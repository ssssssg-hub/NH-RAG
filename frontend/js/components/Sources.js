/** Sources 컴포넌트 - 출처 접이식 UI */

import { createElement, escapeHtml } from "../utils.js";

export function renderSources(parentEl, sources) {
    const container = createElement("div", {
        className: "sources",
        "data-testid": "sources-container",
    });

    const list = createElement("div", { className: "sources-list" });
    const toggle = createElement("button", {
        className: "sources-toggle",
        textContent: `📄 출처 (${sources.length}건)`,
        "data-testid": "sources-toggle",
    });

    toggle.addEventListener("click", () => {
        const isOpen = list.classList.toggle("open");
        toggle.textContent = isOpen ? "📄 출처 접기" : `📄 출처 (${sources.length}건)`;
    });

    for (const src of sources) {
        const item = createElement("div", { className: "source-item" });
        item.innerHTML =
            `<div class="source-name">${escapeHtml(src.file_name)}</div>` +
            `<div class="source-excerpt">${escapeHtml(src.excerpt)}</div>`;
        list.appendChild(item);
    }

    container.append(toggle, list);
    parentEl.appendChild(container);
}
