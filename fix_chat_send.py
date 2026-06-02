import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

old_send = """            const msgInput = document.getElementById('chat-message');
            const message = msgInput.value;
            const inputName = document.getElementById('chat-name').value;
            const gameId = document.getElementById('chat-game-select').value;
            
            if (!message.trim()) return;
            
            const isAa = message.toLowerCase().startsWith('/a');
            
            if (isAa) {
                const lines = message.split('\\n');
                if (lines.some(line => line.trim().length > 1000)) {
                    showToast("アスキーアートの1行の最大文字数は1000文字までです", "error");
                    return;
                }
            } else if (message.length > 300) {
                showToast("通常チャットの最大文字数は300文字です", "error");
                return;
            }
            
            const lineCount = (message.match(/\\n/g) || []).length + 1;
            if (lineCount >= 5 && !isAa) {
                showToast("AA（アスキーアート）を送信する場合は先頭に /a を付けてください", "error");
                msgInput.value = '';
                msgInput.style.height = 'auto';
                return;
            }
            if (inputName && inputName !== '名無しさん') {
                localStorage.setItem('chat_name', inputName);
            } else {
                localStorage.removeItem('chat_name');
            }
            let name = inputName || '名無しさん';
            
            // Optimistic update
            const tempMsg = {
                id: 'temp_' + Date.now(),
                name: name,
                message: message,
                gameId: gameId,
                timestamp: Date.now(),
                clientId: myClientId,
                replyTo: currentReplyToChat
            };
            chatMessages.push(tempMsg);
            renderChat();
            
            msgInput.value = '';
            msgInput.style.height = 'auto';
            
            try {
                const res = await fetch('./post_chat.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, message, gameId, clientId: myClientId, replyTo: currentReplyToChat })
                });
                cancelReply(false);
                if (res.ok) {
                    showChatNotification(tempMsg);
                    fetchChat();
                } else {
                    showToast('送信失敗', 'error');
                }
            } catch (error) {
                console.error("Error posting chat:", error);
                showToast('送信エラー', 'error');
            }"""

new_send = """            const msgInput = document.getElementById('chat-message');
            const message = msgInput.value;
            const inputName = document.getElementById('chat-name').value;
            const gameId = document.getElementById('chat-game-select').value;
            const imageInput = document.getElementById('chat-image');
            const file = imageInput.files && imageInput.files.length > 0 ? imageInput.files[0] : null;
            
            if (!message.trim() && !file) return;
            
            const isAa = message.toLowerCase().startsWith('/a');
            
            if (isAa) {
                const lines = message.split('\\n');
                if (lines.some(line => line.trim().length > 1000)) {
                    showToast("アスキーアートの1行の最大文字数は1000文字までです", "error");
                    return;
                }
            } else if (message.length > 300) {
                showToast("通常チャットの最大文字数は300文字です", "error");
                return;
            }
            
            const lineCount = (message.match(/\\n/g) || []).length + 1;
            if (lineCount >= 5 && !isAa) {
                showToast("AA（アスキーアート）を送信する場合は先頭に /a を付けてください", "error");
                msgInput.value = '';
                msgInput.style.height = 'auto';
                return;
            }
            if (inputName && inputName !== '名無しさん') {
                localStorage.setItem('chat_name', inputName);
            } else {
                localStorage.removeItem('chat_name');
            }
            let name = inputName || '名無しさん';
            
            const btn = document.getElementById('chat-submit-btn');
            btn.disabled = true;
            btn.innerText = '送信中...';
            
            // Optimistic update
            const tempMsg = {
                id: 'temp_' + Date.now(),
                name: name,
                message: message,
                gameId: gameId,
                timestamp: Date.now(),
                clientId: myClientId,
                replyTo: currentReplyToChat,
                imageUrl: file ? URL.createObjectURL(file) : null
            };
            chatMessages.push(tempMsg);
            renderChat();
            
            const formData = new FormData();
            formData.append('name', name);
            formData.append('message', message);
            formData.append('clientId', myClientId);
            if (currentReplyToChat) formData.append('replyTo', JSON.stringify(currentReplyToChat));
            if (gameId) formData.append('gameId', gameId);
            if (file) {
                formData.append('image', file);
            }
            cancelReply(false);
            
            try {
                const response = await fetch('./post_chat.php', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    msgInput.value = '';
                    msgInput.style.height = 'auto';
                    clearChatImage();
                    showChatNotification(tempMsg);
                    fetchChat();
                } else {
                    const result = await response.json();
                    showToast(result.message || '送信失敗', 'error');
                }
            } catch (error) {
                console.error("Error submitting chat:", error);
                showToast('送信エラー', 'error');
            } finally {
                btn.disabled = false;
                btn.innerText = '送信';
            }"""

content = content.replace(old_send, new_send)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
