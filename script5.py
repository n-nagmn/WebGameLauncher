import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

start_idx = content.find("function renderShare()")
end_idx = content.find("async function deleteShareMessage", start_idx)

if start_idx != -1 and end_idx != -1:
    new_render = """function renderShare() {
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
                        gameHtml = `<div class="chat-message-game" onclick="App.openChatGame(${game.id})">🎮 ${escapeHtml(game.name)}</div>`;
                    }
                }
                
                html += `
                    <div class="chat-message-item" id="share-msg-${msg.id}">
                        <div class="chat-message-header" style="display: flex; justify-content: space-between; font-size: 11px; color: #888; margin-bottom: 3px; align-items: center;">
                            <div>
                                <span class="chat-message-name">${escapeHtml(name)}</span>
                                
                                <span>${timeStr}</span>
                            </div>
                            <button onclick="App.deleteShareMessage(${msg.timestamp})" title="削除" style="background: none; border: none; color: #ff5252; cursor: pointer; font-size: 14px; padding: 0 4px; opacity: 0.6;">×</button>
                        </div>
                        ${gameHtml}
                        ${msg.imageUrl ? `<div style="margin-top: 8px;"><a href="${escapeHtml(msg.imageUrl)}" target="_blank"><img src="${escapeHtml(msg.imageUrl)}" style="max-width: 100%; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2);" alt="Image"></a></div>` : ''}
                        ${(() => { let msgText = msg.message || ''; if (msgText === '') return ''; if (msgText.toLowerCase().startsWith('/a')) { return `<div class="chat-message-text aa-font">${escapeHtml(msgText.replace(/^\\/a(?:\\r?\\n| )?/i, ''))}</div>`; } return `<div class="chat-message-text">${escapeHtml(msgText)}</div>`; })()}
                    </div>
                `;
            });
            container.innerHTML = html;
            container.scrollTop = container.scrollHeight;
        }

        """
    content = content[:start_idx] + new_render + content[end_idx:]
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)
