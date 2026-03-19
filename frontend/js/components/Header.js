/** Header 컴포넌트 */

export function initHeader({ onNewChat }) {
    document.getElementById("newChatBtn").addEventListener("click", onNewChat);
}
