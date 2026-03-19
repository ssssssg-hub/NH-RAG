/**
 * NH-RAG 채팅 클라이언트
 */
(function () {
    "use strict";

    const chatArea = document.getElementById("chatArea");
    const messageInput = document.getElementById("messageInput");
    const sendBtn = document.getElementById("sendBtn");
    const newChatBtn = document.getElementById("newChatBtn");
    const welcomeMessage = document.getElementById("welcomeMessage");

    let sessionId = null;
    let isStreaming = false;

    // ── 초기화 ──────────────────────────────────────────

    messageInput.addEventListener("input", onInputChange);
    messageInput.addEventListener("keydown", onKeyDown);
    sendBtn.addEventListener("click", sendMessage);
    newChatBtn.addEventListener("click", startNewChat);

    // 제안 칩 클릭
    document.querySelectorAll(".suggestion-chip").forEach(function (chip) {
        chip.addEventListener("click", function () {
            messageInput.value = chip.getAttribute("data-q");
            onInputChange();
            sendMessage();
        });
    });

    // ── 입력 처리 ───────────────────────────────────────

    function onInputChange() {
        sendBtn.disabled = !messageInput.value.trim() || isStreaming;
        messageInput.style.height = "auto";
        messageInput.style.height = Math.min(messageInput.scrollHeight, 150) + "px";
    }

    function onKeyDown(e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn.disabled) sendMessage();
        }
    }

    // ── 메시지 전송 ─────────────────────────────────────

    async function sendMessage() {
        var text = messageInput.value.trim();
        if (!text || isStreaming) return;

        if (welcomeMessage) welcomeMessage.remove();

        appendMessage("user", text);
        messageInput.value = "";
        messageInput.style.height = "auto";
        sendBtn.disabled = true;
        isStreaming = true;

        var aiRow = appendMessage("ai", "");
        var contentEl = aiRow.querySelector(".message-content");
        showTypingIndicator(contentEl);

        try {
            var response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text, session_id: sessionId }),
            });

            if (!response.ok) throw new Error("서버 오류");

            var reader = response.body.getReader();
            var decoder = new TextDecoder();
            var fullText = "";
            var buffer = "";
            var eventType = "";

            while (true) {
                var result = await reader.read();
                if (result.done) break;

                buffer += decoder.decode(result.value, { stream: true });
                var lines = buffer.split("\n");
                buffer = lines.pop() || "";

                for (var i = 0; i < lines.length; i++) {
                    var line = lines[i];
                    if (line.startsWith("event:")) {
                        eventType = line.slice(6).trim();
                    } else if (line.startsWith("data:")) {
                        var data = line.slice(5).trim();
                        handleSSEEvent(eventType, data, contentEl, aiRow);
                        if (eventType === "token") fullText += data;
                    }
                }
            }

            if (buffer.trim()) {
                var remaining = buffer.split("\n");
                for (var j = 0; j < remaining.length; j++) {
                    if (remaining[j].startsWith("data:")) {
                        handleSSEEvent(eventType, remaining[j].slice(5).trim(), contentEl, aiRow);
                    }
                }
            }

            if (fullText) {
                contentEl.innerHTML = renderMarkdown(fullText);
            }

        } catch (err) {
            contentEl.textContent = "응답 생성에 실패했습니다. 다시 시도해주세요.";
            aiRow.classList.add("message-error");
        } finally {
            isStreaming = false;
            onInputChange();
            messageInput.focus();
        }
    }

    // ── SSE 이벤트 처리 ─────────────────────────────────

    function handleSSEEvent(event, data, contentEl, aiRow) {
        switch (event) {
            case "session":
                try { sessionId = JSON.parse(data).session_id; } catch (e) {}
                break;

            case "token":
                var indicator = contentEl.querySelector(".typing-indicator");
                if (indicator) indicator.remove();
                contentEl.textContent += data;
                scrollToBottom();
                break;

            case "sources":
                try {
                    var sources = JSON.parse(data);
                    if (sources.length > 0) renderSources(aiRow.querySelector(".message-body"), sources);
                } catch (e) {}
                break;

            case "error":
                contentEl.textContent = data || "응답 생성에 실패했습니다.";
                break;

            case "done":
                break;
        }
    }

    // ── UI 렌더링 ───────────────────────────────────────

    function appendMessage(role, text) {
        var row = document.createElement("div");
        row.className = "message-row " + role;
        row.setAttribute("data-testid", role + "-message");

        var inner = document.createElement("div");
        inner.className = "message-inner";

        var avatar = document.createElement("div");
        avatar.className = "avatar " + (role === "user" ? "user-avatar" : "ai-avatar");
        avatar.textContent = role === "user" ? "👤" : "🧠";

        var body = document.createElement("div");
        body.className = "message-body";

        var roleName = document.createElement("div");
        roleName.className = "message-role";
        roleName.textContent = role === "user" ? "나" : "NH-RAG";

        var content = document.createElement("div");
        content.className = "message-content";
        if (role === "user") {
            content.textContent = text;
        }

        body.appendChild(roleName);
        body.appendChild(content);
        inner.appendChild(avatar);
        inner.appendChild(body);
        row.appendChild(inner);
        chatArea.appendChild(row);
        scrollToBottom();
        return row;
    }

    function showTypingIndicator(el) {
        el.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
    }

    function renderSources(bodyEl, sources) {
        var container = document.createElement("div");
        container.className = "sources";
        container.setAttribute("data-testid", "sources-container");

        var toggle = document.createElement("button");
        toggle.className = "sources-toggle";
        toggle.textContent = "📄 출처 (" + sources.length + "건)";
        toggle.setAttribute("data-testid", "sources-toggle");

        var list = document.createElement("div");
        list.className = "sources-list";

        sources.forEach(function (src) {
            var item = document.createElement("div");
            item.className = "source-item";
            item.innerHTML =
                '<div class="source-name">' + escapeHtml(src.file_name) + "</div>" +
                '<div class="source-excerpt">' + escapeHtml(src.excerpt) + "</div>";
            list.appendChild(item);
        });

        toggle.addEventListener("click", function () {
            list.classList.toggle("open");
            toggle.textContent = list.classList.contains("open")
                ? "📄 출처 접기"
                : "📄 출처 (" + sources.length + "건)";
        });

        container.appendChild(toggle);
        container.appendChild(list);
        bodyEl.appendChild(container);
    }

    function scrollToBottom() {
        chatArea.scrollTop = chatArea.scrollHeight;
    }

    // ── 새 대화 ─────────────────────────────────────────

    async function startNewChat() {
        try {
            var res = await fetch("/api/chat/new", { method: "POST" });
            var data = await res.json();
            sessionId = data.session_id;
        } catch (e) {
            sessionId = null;
        }

        chatArea.innerHTML =
            '<div class="welcome" data-testid="welcome-message">' +
            '<div class="welcome-icon">🧠</div>' +
            '<h2>NH-RAG</h2>' +
            '<p>사내 문서 기반 AI 어시스턴트</p>' +
            '<div class="suggestions">' +
            '<button class="suggestion-chip" data-q="사내 규정에 대해 알려줘">📋 사내 규정 안내</button>' +
            '<button class="suggestion-chip" data-q="최근 업데이트된 문서가 있어?">📄 최근 문서 확인</button>' +
            '<button class="suggestion-chip" data-q="업무 프로세스를 설명해줘">⚙️ 업무 프로세스</button>' +
            '</div></div>';

        // 제안 칩 이벤트 재바인딩
        document.querySelectorAll(".suggestion-chip").forEach(function (chip) {
            chip.addEventListener("click", function () {
                messageInput.value = chip.getAttribute("data-q");
                onInputChange();
                sendMessage();
            });
        });

        messageInput.value = "";
        messageInput.style.height = "auto";
        messageInput.focus();
    }

    // ── 유틸리티 ────────────────────────────────────────

    function escapeHtml(str) {
        var div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }

    function renderMarkdown(text) {
        return text
            .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/^- (.+)$/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')
            .replace(/\n/g, '<br>');
    }
})();
