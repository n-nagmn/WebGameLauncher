import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update renderShare to match renderChat exactly
old_render_share = """        function renderShare() {
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
                            <button onclick="App.deleteShareMessage(${msg.timestamp})" title="削除" style="background: none; border: none; color: #ff5252; cursor: pointer; font-size: 14px; padding: 0 4px; opacity: 0.6;">×</button>
                        </div>
                        ${gameHtml}
                        ${msg.imageUrl ? `<div style="margin-top: 8px;"><a href="${escapeHtml(msg.imageUrl)}" target="_blank"><img src="${escapeHtml(msg.imageUrl)}" style="max-width: 100%; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);" alt="Image"></a></div>` : ''}
                        ${(() => { let msgText = msg.message || ''; if (msgText === '') return ''; return `<div class="chat-message-text">${escapeHtml(msgText)}</div>`; })()}
                    </div>
                `;
            });
            container.innerHTML = html;
            container.scrollTop = container.scrollHeight;
        }"""

new_render_share = """        function renderShare() {
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
                        ${(() => { let msgText = msg.message || ''; if (msgText === '') return ''; if (msgText.toLowerCase().startsWith('/a')) { return `<div class="chat-message-text aa-font">${escapeHtml(msgText.replace(/^\/a(?:\r?\n| )?/i, ''))}</div>`; } return `<div class="chat-message-text">${escapeHtml(msgText)}</div>`; })()}
                    </div>
                `;
            });
            container.innerHTML = html;
            container.scrollTop = container.scrollHeight;
        }"""
content = content.replace(old_render_share, new_render_share)

# 2. Update Image Preview container HTML
old_input_area = """        <div class="chat-input-area" style="position: relative;">
            <div id="share-image-preview-container" style="display: none; position: absolute; bottom: 100%; right: 0; margin-bottom: 10px; background: #2a2a2a; border-radius: 8px; padding: 5px; box-shadow: 0 -2px 10px rgba(0,0,0,0.5); z-index: 10;">
                <img id="share-image-preview-img" style="max-height: 100px; border-radius: 4px;" />
                <button onclick="App.clearShareImage()" style="position: absolute; top: -8px; right: -8px; background: #ff5252; color: white; border: none; border-radius: 50%; width: 24px; height: 24px; cursor: pointer; font-weight: bold; display: flex; align-items: center; justify-content: center;">×</button>
            </div>
            <input type="text" id="share-name" placeholder="名前 (省略可)">
            <select id="share-game-select">
                <option value="">ゲーム指定なし</option>
            </select>
            <textarea id="share-message" placeholder="メッセージを入力... (画像はドラッグ＆ドロップで添付)" rows="2"></textarea>
            <input type="file" id="share-image" accept="image/*" onchange="App.handleShareImageSelect()" style="display: none;">
            <button class="btn-save" style="width: 100%; justify-content: center;" onclick="App.submitShare()" id="share-submit-btn">送信</button>
        </div>"""

new_input_area = """        <div class="chat-input-area" style="position: relative;">
            <input type="text" id="share-name" placeholder="名前 (省略可)">
            <select id="share-game-select">
                <option value="">ゲーム指定なし</option>
            </select>
            <div style="position: relative; width: 100%;">
                <textarea id="share-message" placeholder="メッセージを入力... (画像はドラッグ＆ドロップで添付)" rows="2" style="margin-bottom: 8px; min-height: 50px;"></textarea>
                <div id="share-image-preview-container" style="display: none; position: absolute; bottom: 16px; right: 8px; background: rgba(128,128,128,0.2); border-radius: 4px; padding: 4px; z-index: 10; backdrop-filter: blur(4px);">
                    <img id="share-image-preview-img" style="max-height: 60px; border-radius: 4px;" />
                    <button onclick="App.clearShareImage()" style="position: absolute; top: -6px; right: -6px; background: #ff5252; color: white; border: none; border-radius: 50%; width: 18px; height: 18px; cursor: pointer; font-weight: bold; display: flex; align-items: center; justify-content: center; font-size: 12px; padding: 0;">×</button>
                </div>
            </div>
            <input type="file" id="share-image" accept="image/*" onchange="App.handleShareImageSelect()" style="display: none;">
            <button class="btn-save" style="width: 100%; justify-content: center;" onclick="App.submitShare()" id="share-submit-btn">送信</button>
        </div>"""
content = content.replace(old_input_area, new_input_area)


# 3. Ensure handleShareImageSelect adds padding to textarea to prevent text overlap
old_handle_select = """        function handleShareImageSelect() {
            const input = document.getElementById('share-image');
            if(input.files && input.files[0]){
                const r = new FileReader();
                r.onload = e => {
                    document.getElementById('share-image-preview-img').src = e.target.result;
                    document.getElementById('share-image-preview-container').style.display = 'block';
                };
                r.readAsDataURL(input.files[0]);
            }
        }"""

new_handle_select = """        function handleShareImageSelect() {
            const input = document.getElementById('share-image');
            if(input.files && input.files[0]){
                const r = new FileReader();
                r.onload = e => {
                    document.getElementById('share-image-preview-img').src = e.target.result;
                    document.getElementById('share-image-preview-container').style.display = 'block';
                    document.getElementById('share-message').style.paddingRight = '80px';
                };
                r.readAsDataURL(input.files[0]);
            }
        }"""
content = content.replace(old_handle_select, new_handle_select)

old_clear_select = """        function clearShareImage() {
            document.getElementById('share-image').value = '';
            document.getElementById('share-image-preview-container').style.display = 'none';
        }"""

new_clear_select = """        function clearShareImage() {
            document.getElementById('share-image').value = '';
            document.getElementById('share-image-preview-container').style.display = 'none';
            document.getElementById('share-message').style.paddingRight = '10px';
        }"""
content = content.replace(old_clear_select, new_clear_select)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
