with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Preview
old1 = '<div class="chat-input-area">'
new1 = '''<div class="chat-input-area">
            <div id="chat-reply-preview" style="display:none; padding: 8px; background: rgba(0,0,0,0.3); font-size: 11px; color: #aaa; border-left: 3px solid var(--focus-color); border-radius: 0 4px 4px 0;">
                <div style="display:flex; justify-content:space-between; margin-bottom: 2px;">
                    <span id="chat-reply-name" style="font-weight:bold; color: var(--focus-color);"></span>
                    <span style="cursor:pointer; font-size: 14px; line-height: 1;" onclick="App.cancelReply()">✖</span>
                </div>
                <div id="chat-reply-text" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"></div>
            </div>'''
text = text.replace(old1, new1)

# 2. RenderChat
old_html = '''                html += `
                    <div class="chat-message-item">
                        <div class="chat-message-header" style="display: flex; justify-content: space-between; font-size: 11px; color: #888; margin-bottom: 3px; align-items: center;">
                            <div>
                                <span class="chat-message-name">${escapeHtml(name)}</span>
                                <span>${timeStr}</span>
                            </div>
                            <button onclick="App.deleteChatMessage(${msg.timestamp})" title="削除" style="background: none; border: none; color: #ff5252; cursor: pointer; font-size: 14px; padding: 0 4px; opacity: 0.6;">✖</button>
                        </div>
                        ${gameHtml}'''
new_html = '''                let replyHtml = '';
                if (msg.replyTo) {
                    const repliedMsg = chatMessages.find(m => m.id === msg.replyTo);
                    if (repliedMsg) {
                        const rName = repliedMsg.name || '名無しさん';
                        let rText = repliedMsg.message;
                        if (rText.toLowerCase().startsWith('/a')) rText = 'AA (アスキーアート)';
                        replyHtml = `<div class="chat-reply-block" style="padding: 4px 8px; margin-bottom: 4px; background: rgba(0,0,0,0.2); border-left: 3px solid #888; font-size: 11px; color: #aaa; cursor: pointer; border-radius: 0 4px 4px 0;" onclick="document.getElementById('msg-${repliedMsg.id}').scrollIntoView({behavior:'smooth', block:'center'})">
                            <strong>${escapeHtml(rName)}</strong>: ${escapeHtml(rText.substring(0, 50))}${rText.length>50?'...':''}
                        </div>`;
                    } else {
                        replyHtml = `<div class="chat-reply-block" style="padding: 4px 8px; margin-bottom: 4px; background: rgba(0,0,0,0.2); border-left: 3px solid #888; font-size: 11px; color: #777; border-radius: 0 4px 4px 0;">
                            <em>返信元のメッセージは削除されました</em>
                        </div>`;
                    }
                }
                
                const replyBtn = `<button class="chat-reply-btn" style="background:none; border:none; color:var(--focus-color); font-size:11px; cursor:pointer; padding: 0; margin-left: 8px; font-weight: bold; opacity: 0.8;" onclick="App.initiateReply('${msg.id}')">返信</button>`;
                
                html += `
                    <div class="chat-message-item" id="msg-${msg.id}">
                        <div class="chat-message-header" style="display: flex; justify-content: space-between; font-size: 11px; color: #888; margin-bottom: 3px; align-items: center;">
                            <div>
                                <span class="chat-message-name">${escapeHtml(name)}</span>
                                ${replyBtn}
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span>${timeStr}</span>
                                <button onclick="App.deleteChatMessage(${msg.timestamp})" title="削除" style="background: none; border: none; color: #ff5252; cursor: pointer; font-size: 14px; padding: 0; opacity: 0.6; line-height: 1;">✖</button>
                            </div>
                        </div>
                        ${replyHtml}
                        ${gameHtml}'''
text = text.replace(old_html, new_html)

# 3. sendChatMessage variables and payload
old_send = '''        async function sendChatMessage() {'''
new_send = '''        let currentReplyToId = null;

        function initiateReply(msgId) {
            const msg = chatMessages.find(m => m.id === msgId);
            if (!msg) return;
            currentReplyToId = msgId;
            document.getElementById('chat-reply-preview').style.display = 'block';
            document.getElementById('chat-reply-name').textContent = msg.name || '名無しさん';
            let t = msg.message;
            if (t.toLowerCase().startsWith('/a')) t = 'AA (アスキーアート)';
            document.getElementById('chat-reply-text').textContent = t;
            document.getElementById('chat-message').focus();
        }

        function cancelReply() {
            currentReplyToId = null;
            document.getElementById('chat-reply-preview').style.display = 'none';
        }

        async function sendChatMessage() {'''
text = text.replace(old_send, new_send)

old_temp = '''                gameId: gameId,
                timestamp: Date.now(),'''
new_temp = '''                gameId: gameId,
                replyTo: currentReplyToId,
                timestamp: Date.now(),'''
text = text.replace(old_temp, new_temp)

old_fetch = '''            try {
                const res = await fetch('./post_chat.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, message, gameId, clientId: myClientId })
                });'''
new_fetch = '''            const replyTo = currentReplyToId;
            cancelReply();
            
            try {
                const res = await fetch('./post_chat.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, message, gameId, replyTo, clientId: myClientId })
                });'''
text = text.replace(old_fetch, new_fetch)

# 4. Export
old_export = 'openChat, closeChat, sendChatMessage, openChatGame, deleteChatMessage,'
new_export = 'openChat, closeChat, sendChatMessage, openChatGame, deleteChatMessage, initiateReply, cancelReply,'
text = text.replace(old_export, new_export)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)
