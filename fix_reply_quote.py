import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Fix function startReply
old_func = """        function startReply(isShare, timestamp, name, messageSnippet) {
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
        }"""

new_func = """        function startReply(isShare, timestamp) {
            const msgs = isShare ? shareMessages : chatMessages;
            const msg = msgs.find(m => m.timestamp === timestamp);
            if (!msg) return;
            const name = msg.name;
            const messageText = msg.message || '';
            const messageSnippet = messageText.length > 30 ? messageText.substring(0, 30) + '...' : messageText;
            
            const replyObj = { timestamp, name, message: messageSnippet.replace(/\\n/g, " ") };
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
        }"""
content = content.replace(old_func, new_func)

# Fix chat button
old_chat_btn = """<button class="reaction-btn" style="width: 24px; justify-content: center;" onclick="App.startReply(false, ${msg.timestamp}, '${escapeHtml(msg.name).replace(/'/g, "\\'")}', '${escapeHtml(msg.message || '').replace(/'/g, "\\'").replace(/\\n/g, " ")}')" title="返信">↩</button>"""
new_chat_btn = """<button class="reaction-btn" style="width: 24px; justify-content: center;" onclick="App.startReply(false, ${msg.timestamp})" title="返信">↩</button>"""
# Using regex for button to avoid encoding string issues
content = re.sub(r'<button class="reaction-btn"[^>]*onclick="App\.startReply\(false,[^>]*>[^<]*</button>', new_chat_btn, content)

# Fix share button
new_share_btn = """<button class="reaction-btn" style="width: 24px; justify-content: center;" onclick="App.startReply(true, ${msg.timestamp})" title="返信">↩</button>"""
content = re.sub(r'<button class="reaction-btn"[^>]*onclick="App\.startReply\(true,[^>]*>[^<]*</button>', new_share_btn, content)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
