/** Header 컴포넌트 */

export function initHeader({ onNewChat }) {
    document.getElementById("newChatBtn").addEventListener("click", onNewChat);

    const themeBtn = document.getElementById("themeToggleBtn");
    const saved = localStorage.getItem("nh-rag-theme");
    if (saved === "light") applyTheme("light", themeBtn);

    themeBtn.addEventListener("click", () => {
        const next = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
        applyTheme(next, themeBtn);
        localStorage.setItem("nh-rag-theme", next);
    });
}

function applyTheme(theme, btn) {
    if (theme === "light") {
        document.documentElement.setAttribute("data-theme", "light");
        btn.textContent = "☀️";
    } else {
        document.documentElement.removeAttribute("data-theme");
        btn.textContent = "🌙";
    }
}
