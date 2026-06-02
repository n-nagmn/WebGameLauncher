import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

old_notif = """            notif.innerHTML = `
                <div class="chat-notification-header">
                    <span class="chat-notification-name">${escapeHtml(name)}</span>
                    <span>${timeStr}</span>
                </div>
                ${gameHtml}
                ${(() => { let msgText = msg.message; if (msgText.toLowerCase().startsWith('/a')) { return `<div class="chat-notification-text aa-font">${escapeHtml(msgText.replace(/^\\/a(?:\\r?\\n| )?/i, ''))}</div>`; } return `<div class="chat-notification-text">${escapeHtml(msgText)}</div>`; })()}
            `;"""

new_notif = """            let imgHtml = '';
            if (msg.imageUrl) {
                imgHtml = `<div style="margin-top: 6px; margin-bottom: 4px;"><img src="${escapeHtml(msg.imageUrl)}" style="max-height: 80px; max-width: 100%; border-radius: 6px; border: 1px solid rgba(128,128,128,0.2); pointer-events: none;" alt="Image"></div>`;
            }

            notif.innerHTML = `
                <div class="chat-notification-header">
                    <span class="chat-notification-name">${escapeHtml(name)}</span>
                    <span>${timeStr}</span>
                </div>
                ${gameHtml}
                ${imgHtml}
                ${(() => { let msgText = msg.message || ''; if (msgText === '') return ''; if (msgText.toLowerCase().startsWith('/a')) { return `<div class="chat-notification-text aa-font">${escapeHtml(msgText.replace(/^\\/a(?:\\r?\\n| )?/i, ''))}</div>`; } return `<div class="chat-notification-text">${escapeHtml(msgText)}</div>`; })()}
            `;"""
            
if old_notif in content:
    content = content.replace(old_notif, new_notif)
else:
    print("Warning: could not find old_notif snippet.")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
