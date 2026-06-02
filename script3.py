import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Unhide delete button in renderChat
content = content.replace(
    "${msg.clientId === myClientId ? `<button onclick=\"App.deleteChatMessage(${msg.timestamp})\" title=\"削除\" style=\"background: none; border: none; color: #ff5252; cursor: pointer; font-size: 14px; padding: 0 4px; opacity: 0.6;\">×</button>` : ''}",
    "<button onclick=\"App.deleteChatMessage(${msg.timestamp})\" title=\"削除\" style=\"background: none; border: none; color: #ff5252; cursor: pointer; font-size: 14px; padding: 0 4px; opacity: 0.6;\">×</button>"
)

# 2. Unhide delete button in renderShare
content = content.replace(
    "${msg.clientId === myClientId ? `<button onclick=\"App.deleteShareMessage(${msg.timestamp})\" title=\"削除\" style=\"background: none; border: none; color: #ff5252; cursor: pointer; font-size: 14px; padding: 0 4px; opacity: 0.6;\">×</button>` : ''}",
    "<button onclick=\"App.deleteShareMessage(${msg.timestamp})\" title=\"削除\" style=\"background: none; border: none; color: #ff5252; cursor: pointer; font-size: 14px; padding: 0 4px; opacity: 0.6;\">×</button>"
)

# 3. Optimistic update in submitShare
old_submit_share = """            btn.disabled = true;
            btn.innerText = '送信中...';
            
            const formData = new FormData();"""

new_submit_share = """            btn.disabled = true;
            btn.innerText = '送信中...';
            
            // Optimistic update
            const tempMsg = {
                id: 'temp_share_' + Date.now(),
                name: name,
                message: message,
                gameId: gameId,
                timestamp: Date.now(),
                clientId: myClientId,
                imageUrl: file ? URL.createObjectURL(file) : null
            };
            shareMessages.push(tempMsg);
            renderShare();
            
            const formData = new FormData();"""
content = content.replace(old_submit_share, new_submit_share)

# 4. showChatNotification in submitShare
old_submit_success = """                if (data.status === 'success') {
                    showChatNotification(data.data);"""

new_submit_success = """                if (data.status === 'success') {
                    showChatNotification(tempMsg);"""
content = content.replace(old_submit_success, new_submit_success)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
