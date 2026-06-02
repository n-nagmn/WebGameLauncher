import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Swap in renderShare
old_render_share = """                        ${msg.imageUrl ? `<div style="margin-top: 8px;"><a href="${escapeHtml(msg.imageUrl)}" target="_blank"><img src="${escapeHtml(msg.imageUrl)}" style="max-width: 100%; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2);" alt="Image"></a></div>` : ''}
                        ${(() => { let msgText = msg.message || ''; if (msgText === '') return ''; if (msgText.toLowerCase().startsWith('/a')) { return `<div class="chat-message-text aa-font">${escapeHtml(msgText.replace(/^\\/a(?:\\r?\\n| )?/i, ''))}</div>`; } return `<div class="chat-message-text">${escapeHtml(msgText)}</div>`; })()}"""

new_render_share = """                        ${(() => { let msgText = msg.message || ''; if (msgText === '') return ''; if (msgText.toLowerCase().startsWith('/a')) { return `<div class="chat-message-text aa-font">${escapeHtml(msgText.replace(/^\\/a(?:\\r?\\n| )?/i, ''))}</div>`; } return `<div class="chat-message-text">${escapeHtml(msgText)}</div>`; })()}
                        ${msg.imageUrl ? `<div style="margin-top: 8px;"><a href="${escapeHtml(msg.imageUrl)}" target="_blank"><img src="${escapeHtml(msg.imageUrl)}" style="max-width: 100%; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2);" alt="Image"></a></div>` : ''}"""

if old_render_share in content:
    content = content.replace(old_render_share, new_render_share)

# 2. Swap in renderChat
old_render_chat = """                        ${msg.imageUrl ? `<div style="margin-top: 8px;"><a href="${escapeHtml(msg.imageUrl)}" target="_blank"><img src="${escapeHtml(msg.imageUrl)}" style="max-width: 100%; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2);" alt="Image"></a></div>` : ''}
                        ${(() => { let msgText = msg.message || ''; if (msgText === '') return ''; if (msgText.toLowerCase().startsWith('/a')) { return `<div class="chat-message-text aa-font">${escapeHtml(msgText.replace(/^\\/a(?:\\r?\\n| )?/i, ''))}</div>`; } return `<div class="chat-message-text">${escapeHtml(msgText)}</div>`; })()}"""

# Note: old_render_share and old_render_chat are identical strings in the file. Since replace() will replace all occurrences, both will be fixed by the single replace call above.
# Just to be safe, we will just use replace which replaces all occurrences of that block.

# 3. Swap in showChatNotification
old_notif = """                ${imgHtml}
                ${(() => { let msgText = msg.message || ''; if (msgText === '') return ''; if (msgText.toLowerCase().startsWith('/a')) { return `<div class="chat-notification-text aa-font">${escapeHtml(msgText.replace(/^\\/a(?:\\r?\\n| )?/i, ''))}</div>`; } return `<div class="chat-notification-text">${escapeHtml(msgText)}</div>`; })()}
            `;"""

new_notif = """                ${(() => { let msgText = msg.message || ''; if (msgText === '') return ''; if (msgText.toLowerCase().startsWith('/a')) { return `<div class="chat-notification-text aa-font">${escapeHtml(msgText.replace(/^\\/a(?:\\r?\\n| )?/i, ''))}</div>`; } return `<div class="chat-notification-text">${escapeHtml(msgText)}</div>`; })()}
                ${imgHtml}
            `;"""

if old_notif in content:
    content = content.replace(old_notif, new_notif)

# 4. Modify Drag and Drop DropZone
old_dnd = """        function setupShareDragAndDrop() {
            const dropZone = document.getElementById('share-message');"""
new_dnd = """        function setupShareDragAndDrop() {
            const dropZone = document.getElementById('share-sidebar');"""

if old_dnd in content:
    content = content.replace(old_dnd, new_dnd)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
