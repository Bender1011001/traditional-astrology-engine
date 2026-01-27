
/* Engine Chat Logic */
const askOracleBtn = document.getElementById('askOracleBtn');
if (askOracleBtn) {
    askOracleBtn.addEventListener('click', () => {
        if (!currentResult) {
            alert("Run a chart first.");
            return;
        }

        modalBody.innerHTML = `
            <style>
                .chat-container { display: flex; flex-direction: column; height: 500px; }
                .chat-history { flex: 1; overflow-y: auto; padding: 1rem; background: rgba(0,0,0,0.3); margin-bottom: 1rem; border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; }
                .chat-input-area { display: flex; gap: 0.5rem; }
                #chatInput { flex: 1; padding: 0.8rem; background: rgba(0,0,0,0.5); border: 1px solid var(--gold); color: #e0e0e0; font-family: 'Outfit', sans-serif; }
                #sendChatBtn { padding: 0 1.5rem; background: var(--gold); color: #000; font-weight: bold; border: none; cursor: pointer; transition: all 0.3s ease; }
                #sendChatBtn:hover { background: #fff; box-shadow: 0 0 15px var(--gold); }
                .chat-message { margin-bottom: 1rem; padding: 0.8rem; border-radius: 4px; line-height: 1.5; font-size: 0.95rem; }
                .chat-message.user { background: rgba(255, 215, 0, 0.1); border-left: 3px solid var(--gold); text-align: right; }
                .chat-message.assistant { background: rgba(255, 255, 255, 0.05); border-left: 3px solid #fff; }
                .chat-message.system { font-style: italic; opacity: 0.7; text-align: center; }
                .chat-message.error { color: #ef5350; }
            </style>
            <div class="modal-header">
                <h2>CONSULT THE ORACLE (GEMINI FLASH)</h2>
                <div class="ornament"></div>
            </div>
            <div class="chat-container">
                <div id="chatHistory" class="chat-history">
                    <div class="chat-message system">
                        The Codex Caelestis is listening. Ask regarding this nativity.
                    </div>
                </div>
                <div class="chat-input-area">
                    <input type="text" id="chatInput" placeholder="Ask your question..." autocomplete="off">
                    <button id="sendChatBtn">SEND</button>
                </div>
            </div>
        `;
        modalOverlay.classList.remove("hidden");

        // Chat Logic binding
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendChatBtn');
        const history = document.getElementById('chatHistory');

        async function sendQuery() {
            const query = chatInput.value.trim();
            if (!query) return;

            // Add user message
            history.innerHTML += `<div class="chat-message user">${query}</div>`;
            chatInput.value = '';
            history.scrollTop = history.scrollHeight;

            // Add loading
            const loadingId = 'loading-' + Date.now();
            history.innerHTML += `<div id="${loadingId}" class="chat-message system loading">Divining...</div>`;
            history.scrollTop = history.scrollHeight;

            // Prepare context (Forensic Report + Predictions)
            const contextData = {
                forensic: currentResult.forensic_report,
                prediction: currentResult.advanced_prediction
            };
            const context = JSON.stringify(contextData, null, 2);

            try {
                const response = await fetch(apiUrl('/api/ask_oracle'), {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query, context: context })
                });

                const data = await response.json();

                // Remove loading
                const loader = document.getElementById(loadingId);
                if (loader) loader.remove();

                // Add answer
                let text = data.answer || "No response from engine.";
                // Simple markdown parsing
                text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                text = text.replace(/\n/g, '<br>');

                history.innerHTML += `<div class="chat-message assistant">${text}</div>`;
                history.scrollTop = history.scrollHeight;

            } catch (err) {
                const loader = document.getElementById(loadingId);
                if (loader) loader.remove();
                history.innerHTML += `<div class="chat-message system error">Connection lost: ${err.message}</div>`;
            }
        }

        sendBtn.onclick = sendQuery;
        chatInput.onkeypress = (e) => {
            if (e.key === 'Enter') sendQuery();
        };

        // Focus input
        setTimeout(() => chatInput.focus(), 100);
    });
}
