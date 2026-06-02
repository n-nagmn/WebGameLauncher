with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Preview
target1 = '<div class="chat-input-area">'
repl1 = '<div class="chat-input-area">\n            <div id="chat-reply-preview" style="display:none; padding: 8px; background: rgba(0,0,0,0.3); font-size: 11px; color: #aaa; border-left: 3px solid var(--focus-color); border-radius: 0 4px 4px 0;">\n                <div style="display:flex; justify-content:space-between; margin-bottom: 2px;">\n                    <span id="chat-reply-name" style="font-weight:bold; color: var(--focus-color);"></span>\n                    <span style="cursor:pointer; font-size: 14px; line-height: 1;" onclick="App.cancelReply()">×</span>\n                </div>\n                <div id="chat-reply-text" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"></div>\n            </div>'
text = text.replace(target1, repl1, 1) # Only first occurrence

# 2. RenderChat button
target2 = '<span class="chat-message-name">${escapeHtml(name)}</span>'
repl2 = '<span class="chat-message-name">${escapeHtml(name)}</span>\n                                <button class="chat-reply-btn" style="background:none; border:none; color:var(--focus-color); font-size:11px; cursor:pointer; padding: 0; margin-left: 8px; font-weight: bold; opacity: 0.8;" onclick="App.initiateReply(\'${msg.id}\')">返信</button>'
text = text.replace(target2, repl2, 1)

# 3. RenderChat HTML block
target3 = '                        ${gameHtml}'
repl3 = '''                        ${(() => {
                            if (!msg.replyTo) return '';
                            const repliedMsg = chatMessages.find(m => m.id === msg.replyTo);
                            if (repliedMsg) {
                                const rName = repliedMsg.name || '名無しさん';
                                let rText = repliedMsg.message;
                                if (rText.toLowerCase().startsWith('/a')) rText = 'AA (アスキーアート)';
                                return `<div class="chat-reply-block" style="padding: 4px 8px; margin-bottom: 4px; background: rgba(0,0,0,0.2); border-left: 3px solid #888; font-size: 11px; color: #aaa; cursor: pointer; border-radius: 0 4px 4px 0;" onclick="document.getElementById('msg-${repliedMsg.id}').scrollIntoView({behavior:'smooth', block:'center'})"><strong>${escapeHtml(rName)}</strong>: ${escapeHtml(rText.substring(0, 50))}${rText.length>50?'...':''}</div>`;
                            } else {
                                return `<div class="chat-reply-block" style="padding: 4px 8px; margin-bottom: 4px; background: rgba(0,0,0,0.2); border-left: 3px solid #888; font-size: 11px; color: #777; border-radius: 0 4px 4px 0;"><em>返信元のメッセージは削除されました</em></div>`;
                            }
                        })()}
                        ${gameHtml}'''
text = text.replace(target3, repl3, 1)

# 4. RenderChat ID
target4 = '<div class="chat-message-item">'
repl4 = '<div class="chat-message-item" id="msg-${msg.id}">'
text = text.replace(target4, repl4, 1)

# 5. Functions
target5 = 'async function sendChatMessage() {'
repl5 = '''let currentReplyToId = null;

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
text = text.replace(target5, repl5, 1)

# 6. Payload 1 (Optimistic)
target6 = 'gameId: gameId,\n                timestamp: Date.now(),'
repl6 = 'gameId: gameId,\n                replyTo: currentReplyToId,\n                timestamp: Date.now(),'
text = text.replace(target6, repl6, 1)

# 7. Payload 2 (Fetch)
target7 = 'body: JSON.stringify({ name, message, gameId, clientId: myClientId })'
repl7 = 'body: JSON.stringify({ name, message, gameId, replyTo: currentReplyToId, clientId: myClientId })'
text = text.replace(target7, repl7, 1)

# 8. Post-send cleanup
target8 = "msgInput.style.height = 'auto';"
repl8 = "msgInput.style.height = 'auto';\n            cancelReply();"
text = text.replace(target8, repl8, 1)

# 9. App export
target9 = 'openChat, closeChat, sendChatMessage, openChatGame, deleteChatMessage,'
repl9 = 'openChat, closeChat, sendChatMessage, openChatGame, deleteChatMessage, initiateReply, cancelReply,'
text = text.replace(target9, repl9, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)
