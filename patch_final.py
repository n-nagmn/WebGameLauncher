with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Preview
for i, line in enumerate(lines):
    if '<div class="chat-input-area">' in line:
        lines[i] = '''        <div class="chat-input-area">
            <div id="chat-reply-preview" style="display:none; padding: 8px; background: rgba(0,0,0,0.3); font-size: 11px; color: #aaa; border-left: 3px solid var(--focus-color); border-radius: 0 4px 4px 0;">
                <div style="display:flex; justify-content:space-between; margin-bottom: 2px;">
                    <span id="chat-reply-name" style="font-weight:bold; color: var(--focus-color);"></span>
                    <span style="cursor:pointer; font-size: 14px; line-height: 1;" onclick="App.cancelReply()">✖</span>
                </div>
                <div id="chat-reply-text" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"></div>
            </div>\n'''
        break

# 2. sendChatMessage (functions)
for i, line in enumerate(lines):
    if 'async function sendChatMessage() {' in line:
        lines[i] = '''        let currentReplyToId = null;

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

        async function sendChatMessage() {\n'''
        break

# 3. sendChatMessage (tempMsg payload update)
for i in range(len(lines)):
    if 'timestamp: Date.now(),' in lines[i] and 'clientId: myClientId' in lines[i+1]:
        if i > 1650 and i < 1780:
            lines[i] = "                replyTo: currentReplyToId,\n" + lines[i]
            break

# 4. sendChatMessage (fetch update)
for i in range(len(lines)):
    if 'body: JSON.stringify({ name, message, gameId, clientId: myClientId })' in lines[i]:
        if i > 1650 and i < 1780:
            # We want to put replyTo assignment before try {
            # Let's find the `try {` line going backwards
            for k in range(i, 1650, -1):
                if 'try {' in lines[k]:
                    lines[k] = "            const replyTo = currentReplyToId;\n            cancelReply();\n\n            try {\n"
                    break
            lines[i] = lines[i].replace('gameId, clientId', 'gameId, replyTo, clientId')
            break

# 5. renderChat update
in_render = False
for i in range(len(lines)):
    if 'function renderChat()' in lines[i]:
        in_render = True
    if in_render and 'let gameHtml = \'\';' in lines[i]:
        # find html += `
        start_idx = -1
        for j in range(i, len(lines)):
            if 'html += `' in lines[j]:
                start_idx = j
                break
        
        end_idx = -1
        if start_idx != -1:
            for j in range(start_idx, len(lines)):
                if '`;' in lines[j] and '</div>' in lines[j-1]:
                    end_idx = j
                    break
        
        if start_idx != -1 and end_idx != -1:
            replacement = '''                let replyHtml = '';
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
                        ${gameHtml}
                        ${(() => { let msgText = msg.message; if (msgText.toLowerCase().startsWith('/a')) { return `<div class="chat-message-text aa-font">${escapeHtml(msgText.replace(/^\\/a(?:\\r?\\n| )?/i, ''))}</div>`; } return `<div class="chat-message-text">${escapeHtml(msgText)}</div>`; })()}
                    </div>
                `;\n'''
            for k in range(start_idx, end_idx + 1):
                lines[k] = ''
            lines[start_idx] = replacement
        break

# 6. window.App export
for i in range(len(lines)):
    if 'openChat, closeChat, sendChatMessage, openChatGame, deleteChatMessage,' in lines[i]:
        lines[i] = lines[i].replace('deleteChatMessage,', 'deleteChatMessage, initiateReply, cancelReply,')
        break

with open('index.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)
