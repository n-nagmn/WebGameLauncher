import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. HTML Share Sidebar structure
old_html = """        <div class="chat-messages" id="share-preview-area" style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <div id="share-image-preview-container" style="display: none; position: relative; margin: 20px;">
                <img id="share-image-preview-img" style="max-width: 100%; max-height: 250px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2);" />
                <button onclick="App.clearShareImage()" style="position: absolute; top: -10px; right: -10px; background: #ff5252; color: white; border: none; border-radius: 50%; width: 28px; height: 28px; cursor: pointer; font-weight: bold; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 4px rgba(0,0,0,0.5);">×</button>
            </div>
        </div>
        <div class="chat-input-area">"""

new_html = """        <div class="chat-messages" id="share-messages">
            <!-- Share messages will be rendered here -->
        </div>
        <div class="chat-input-area" style="position: relative;">
            <div id="share-image-preview-container" style="display: none; position: absolute; bottom: 100%; right: 0; margin-bottom: 10px; background: #2a2a2a; border-radius: 8px; padding: 5px; box-shadow: 0 -2px 10px rgba(0,0,0,0.5); z-index: 10;">
                <img id="share-image-preview-img" style="max-height: 100px; border-radius: 4px;" />
                <button onclick="App.clearShareImage()" style="position: absolute; top: -8px; right: -8px; background: #ff5252; color: white; border: none; border-radius: 50%; width: 24px; height: 24px; cursor: pointer; font-weight: bold; display: flex; align-items: center; justify-content: center;">×</button>
            </div>"""

content = content.replace(old_html, new_html)

# 2. variables
content = content.replace("let chatMessages = [];", "let chatMessages = [];\n        let shareMessages = [];\n        let initialShareLoaded = false;")

# 3. drag drop target
content = content.replace("const dropZone = document.getElementById('share-preview-area');", "const dropZone = document.getElementById('share-message');")
content = content.replace("dropZone.style.background = 'rgba(255, 255, 255, 0.05)';", "dropZone.style.background = 'rgba(255, 255, 255, 0.1)';")

# 4. Add JS functions above deleteChatMessage
share_funcs = """        async function fetchShare() {
            try {
                const res = await fetch('./share.json?t=' + Date.now());
                if (res.ok) {
                    const newMessages = await res.json();
                    if (JSON.stringify(newMessages) !== JSON.stringify(shareMessages)) {
                        shareMessages = newMessages;
                        initialShareLoaded = true;
                        renderShare();
                    } else {
                        initialShareLoaded = true;
                    }
                }
            } catch (e) {
                console.error(e);
            }
        }

        function renderShare() {
            const container = document.getElementById('share-messages');
            if (!container) return;
            
            if (shareMessages.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: #888; font-size: 13px; margin-top: 20px;">まだ投稿はありません</div>';
                return;
            }

            let html = '';
            shareMessages.forEach(msg => {
                const timeStr = new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                const name = msg.name || '名無しさん';
                let gameHtml = '';
                if (msg.gameId) {
                    const game = games.find(g => g.id == msg.gameId);
                    if (game) {
                        gameHtml = `<div style="font-size: 11px; margin-bottom: 4px; display: inline-block; background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; cursor: pointer;" onclick="App.openChatGame(${game.id})">${escapeHtml(game.name)}</div>`;
                    }
                }
                
                html += `
                    <div class="chat-message" data-id="${msg.id}">
                        <div class="chat-message-header">
                            <div>
                                <span class="chat-message-name">${escapeHtml(name)}</span>
                                
                                <span>${timeStr}</span>
                            </div>
                            ${msg.clientId === myClientId ? `<button onclick="App.deleteShareMessage(${msg.timestamp})" title="削除" style="background: none; border: none; color: #ff5252; cursor: pointer; font-size: 14px; padding: 0 4px; opacity: 0.6;">×</button>` : ''}
                        </div>
                        ${gameHtml}
                        ${msg.imageUrl ? `<div style="margin-top: 8px;"><a href="${escapeHtml(msg.imageUrl)}" target="_blank"><img src="${escapeHtml(msg.imageUrl)}" style="max-width: 100%; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);" alt="Image"></a></div>` : ''}
                        ${(() => { let msgText = msg.message || ''; if (msgText === '') return ''; return `<div class="chat-message-text">${escapeHtml(msgText)}</div>`; })()}
                    </div>
                `;
            });
            container.innerHTML = html;
            container.scrollTop = container.scrollHeight;
        }

        async function deleteShareMessage(timestamp) {
            try {
                const res = await fetch('./post_share.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'delete', timestamp: timestamp, clientId: myClientId })
                });
                if (res.ok) {
                    fetchShare();
                } else {
                    showToast('削除失敗', 'error');
                }
            } catch(e) {
                showToast('通信エラー', 'error');
            }
        }

        async function deleteChatMessage(timestamp) {"""
content = content.replace("        async function deleteChatMessage(timestamp) {", share_funcs)

# 5. submitShare logic update
content = content.replace("const response = await fetch('post_chat.php', {", "const response = await fetch('post_share.php', {")

old_submit_success = """                if (data.status === 'success') {
                    showChatNotification(data.data);
                    localStorage.setItem('chat_name', name);
                    document.getElementById('chat-name').value = name;
                    closeShare();
                    
                    fetchChat();
                } else {"""

new_submit_success = """                if (data.status === 'success') {
                    showChatNotification(data.data);
                    localStorage.setItem('chat_name', name);
                    document.getElementById('share-name').value = name;
                    const msgInput = document.getElementById('share-message');
                    if (msgInput) msgInput.value = '';
                    clearShareImage();
                    
                    fetchShare();
                } else {"""

content = content.replace(old_submit_success, new_submit_success)

# 6. init polling update
content = content.replace("setInterval(fetchChat, 5000);", "setInterval(fetchChat, 5000);\n            fetchShare();\n            setInterval(fetchShare, 5000);")

# 7. export
content = content.replace("openShare, closeShare, submitShare, handleShareImageSelect, clearShareImage", "openShare, closeShare, submitShare, handleShareImageSelect, clearShareImage, deleteShareMessage")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
