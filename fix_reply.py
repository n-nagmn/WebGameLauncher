import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. State and Functions
funcs = """        let currentReactionMsgTs = 0;
        let currentReactionIsShare = false;
        
        let currentReplyToChat = null;
        let currentReplyToShare = null;

        function startReply(isShare, timestamp, name, messageSnippet) {
            const replyObj = { timestamp, name, message: messageSnippet.length > 30 ? messageSnippet.substring(0, 30) + '...' : messageSnippet };
            if (isShare) {
                currentReplyToShare = replyObj;
                document.getElementById('share-reply-preview').style.display = 'flex';
                document.getElementById('share-reply-name').textContent = name;
                document.getElementById('share-reply-text').textContent = replyObj.message;
                document.getElementById('share-message').focus();
            } else {
                currentReplyToChat = replyObj;
                document.getElementById('chat-reply-preview').style.display = 'flex';
                document.getElementById('chat-reply-name').textContent = name;
                document.getElementById('chat-reply-text').textContent = replyObj.message;
                document.getElementById('chat-message').focus();
            }
        }

        function cancelReply(isShare) {
            if (isShare) {
                currentReplyToShare = null;
                document.getElementById('share-reply-preview').style.display = 'none';
            } else {
                currentReplyToChat = null;
                document.getElementById('chat-reply-preview').style.display = 'none';
            }
        }"""
content = content.replace("        let currentReactionMsgTs = 0;\n        let currentReactionIsShare = false;", funcs)

# 2. Add Reply Preview HTML to Chat
old_chat_input = """          <div class="chat-input-area">
              <input type="text" id="chat-name" placeholder="名前 (省略可)">"""
new_chat_input = """          <div class="chat-input-area">
              <div id="chat-reply-preview" style="display: none; font-size: 11px; padding: 4px; background: rgba(128,128,128,0.1); border-left: 3px solid var(--focus-color); margin-bottom: 4px; justify-content: space-between; align-items: center; border-radius: 4px;">
                  <span style="overflow: hidden; white-space: nowrap; text-overflow: ellipsis;"><span style="color:gray;">返信先:</span> <strong id="chat-reply-name"></strong> <span id="chat-reply-text" style="color:gray;"></span></span>
                  <button onclick="App.cancelReply(false)" style="background: none; border: none; cursor: pointer; color: gray;">✕</button>
              </div>
              <input type="text" id="chat-name" placeholder="名前 (省略可)">"""
content = content.replace(old_chat_input, new_chat_input)

# 3. Add Reply Preview HTML to Share
old_share_input = """          <div class="chat-input-area" style="position: relative;">
              <input type="text" id="share-name" placeholder="名前 (省略可)">"""
new_share_input = """          <div class="chat-input-area" style="position: relative;">
              <div id="share-reply-preview" style="display: none; font-size: 11px; padding: 4px; background: rgba(128,128,128,0.1); border-left: 3px solid var(--focus-color); margin-bottom: 4px; justify-content: space-between; align-items: center; border-radius: 4px;">
                  <span style="overflow: hidden; white-space: nowrap; text-overflow: ellipsis;"><span style="color:gray;">返信先:</span> <strong id="share-reply-name"></strong> <span id="share-reply-text" style="color:gray;"></span></span>
                  <button onclick="App.cancelReply(true)" style="background: none; border: none; cursor: pointer; color: gray;">✕</button>
              </div>
              <input type="text" id="share-name" placeholder="名前 (省略可)">"""
content = content.replace(old_share_input, new_share_input)

# 4. Modify sendChatMessage
old_send_chat = """                const tempMsg = {
                    id: 'temp_' + Date.now(),
                    name: name,
                    message: message,
                    gameId: gameId,
                    timestamp: Date.now(),
                    clientId: myClientId
                };"""
new_send_chat = """                const tempMsg = {
                    id: 'temp_' + Date.now(),
                    name: name,
                    message: message,
                    gameId: gameId,
                    timestamp: Date.now(),
                    clientId: myClientId,
                    replyTo: currentReplyToChat
                };"""
content = content.replace(old_send_chat, new_send_chat)

old_fetch_chat = """                const res = await fetch('./post_chat.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, message, gameId, clientId: myClientId })
                });"""
new_fetch_chat = """                const res = await fetch('./post_chat.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, message, gameId, clientId: myClientId, replyTo: currentReplyToChat })
                });
                cancelReply(false);"""
content = content.replace(old_fetch_chat, new_fetch_chat)

# 5. Modify submitShare
old_send_share = """                const tempMsg = {
                    id: 'temp_share_' + Date.now(),
                    name: name,
                    message: message,
                    gameId: gameId,
                    timestamp: Date.now(),
                    clientId: myClientId,
                    imageUrl: file ? URL.createObjectURL(file) : null
                };"""
new_send_share = """                const tempMsg = {
                    id: 'temp_share_' + Date.now(),
                    name: name,
                    message: message,
                    gameId: gameId,
                    timestamp: Date.now(),
                    clientId: myClientId,
                    imageUrl: file ? URL.createObjectURL(file) : null,
                    replyTo: currentReplyToShare
                };"""
content = content.replace(old_send_share, new_send_share)

old_fetch_share = """            formData.append('clientId', myClientId);
            formData.append('isShare', 'true');
            if (gameId) formData.append('gameId', gameId);
            if (file) {
                formData.append('image', file);
            }
            
            try {
                const response = await fetch('./post_share.php', {"""
new_fetch_share = """            formData.append('clientId', myClientId);
            formData.append('isShare', 'true');
            if (currentReplyToShare) formData.append('replyTo', JSON.stringify(currentReplyToShare));
            if (gameId) formData.append('gameId', gameId);
            if (file) {
                formData.append('image', file);
            }
            cancelReply(true);
            
            try {
                const response = await fetch('./post_share.php', {"""
content = content.replace(old_fetch_share, new_fetch_share)

# 6. Render Chat UI
old_render_chat_html = """                        <div class="chat-message-header">
                            <div>
                                <strong>${escapeHtml(msg.name)}</strong>"""
new_render_chat_html = """                        ${msg.replyTo ? `<div style="font-size: 11px; color: gray; margin-bottom: 2px; padding-left: 12px; border-left: 2px solid gray; display: flex; align-items: center; gap: 4px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; border-radius: 2px; background: rgba(128,128,128,0.05); padding: 2px 4px 2px 8px;">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;"><polyline points="9 17 4 12 9 7"></polyline><path d="M20 18v-2a4 4 0 0 0-4-4H4"></path></svg>
                            <strong>${escapeHtml(msg.replyTo.name)}</strong>: ${escapeHtml(msg.replyTo.message)}
                        </div>` : ''}
                        <div class="chat-message-header">
                            <div>
                                <strong>${escapeHtml(msg.name)}</strong>"""
content = content.replace(old_render_chat_html, new_render_chat_html)

old_chat_add_btn = """                            <button class="add-reaction-btn reaction-btn" style="width: 24px; justify-content: center;" onclick="App.toggleReactionPicker(${msg.timestamp}, false, this, event)">+</button>
                        </div>"""
new_chat_add_btn = """                            <button class="add-reaction-btn reaction-btn" style="width: 24px; justify-content: center;" onclick="App.toggleReactionPicker(${msg.timestamp}, false, this, event)">+</button>
                            <button class="reaction-btn" style="width: 24px; justify-content: center;" onclick="App.startReply(false, ${msg.timestamp}, '${escapeHtml(msg.name).replace(/'/g, "\\'")}', '${escapeHtml(msg.message || '').replace(/'/g, "\\'").replace(/\\n/g, " ")}')" title="返信">↩</button>
                        </div>"""
content = content.replace(old_chat_add_btn, new_chat_add_btn)

# 7. Render Share UI
old_render_share_html = """                        <div class="chat-message-header">
                            <div>
                                <strong>${escapeHtml(msg.name)}</strong>"""
new_render_share_html = """                        ${msg.replyTo ? `<div style="font-size: 11px; color: gray; margin-bottom: 2px; padding-left: 12px; border-left: 2px solid gray; display: flex; align-items: center; gap: 4px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; border-radius: 2px; background: rgba(128,128,128,0.05); padding: 2px 4px 2px 8px;">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;"><polyline points="9 17 4 12 9 7"></polyline><path d="M20 18v-2a4 4 0 0 0-4-4H4"></path></svg>
                            <strong>${escapeHtml(msg.replyTo.name)}</strong>: ${escapeHtml(msg.replyTo.message)}
                        </div>` : ''}
                        <div class="chat-message-header">
                            <div>
                                <strong>${escapeHtml(msg.name)}</strong>"""
content = content.replace(old_render_share_html, new_render_share_html)

old_share_add_btn = """                            <button class="add-reaction-btn reaction-btn" style="width: 24px; justify-content: center;" onclick="App.toggleReactionPicker(${msg.timestamp}, true, this, event)">+</button>
                        </div>"""
new_share_add_btn = """                            <button class="add-reaction-btn reaction-btn" style="width: 24px; justify-content: center;" onclick="App.toggleReactionPicker(${msg.timestamp}, true, this, event)">+</button>
                            <button class="reaction-btn" style="width: 24px; justify-content: center;" onclick="App.startReply(true, ${msg.timestamp}, '${escapeHtml(msg.name).replace(/'/g, "\\'")}', '${escapeHtml(msg.message || '').replace(/'/g, "\\'").replace(/\\n/g, " ")}')" title="返信">↩</button>
                        </div>"""
content = content.replace(old_share_add_btn, new_share_add_btn)

# 8. Export new functions
old_exports = """            openImageModal, closeImageModal,
            toggleReactionPicker, reactMessage
        };"""
new_exports = """            openImageModal, closeImageModal,
            toggleReactionPicker, reactMessage,
            startReply, cancelReply
        };"""
content = content.replace(old_exports, new_exports)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
