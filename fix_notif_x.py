import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

old_notif = """            notif.innerHTML = `
                <div class="chat-notification-header">
                    <span class="chat-notification-name">${escapeHtml(name)}</span>
                    <span>${timeStr}</span>
                </div>"""

new_notif = """            notif.innerHTML = `
                <div class="chat-notification-header" style="position: relative; padding-right: 20px;">
                    <span class="chat-notification-name">${escapeHtml(name)}</span>
                    <span>${timeStr}</span>
                    <button class="notif-close-btn" title="閉じる" style="position: absolute; right: -8px; top: -4px; background: none; border: none; color: inherit; font-size: 18px; cursor: pointer; padding: 4px; line-height: 1; opacity: 0.6;">&times;</button>
                </div>"""

if old_notif in content:
    content = content.replace(old_notif, new_notif)

old_onclick = """            notif.onclick = (e) => {"""
new_onclick = """            const closeBtn = notif.querySelector('.notif-close-btn');
            if (closeBtn) {
                closeBtn.onclick = (e) => {
                    e.stopPropagation();
                    notif.classList.add('hiding');
                    setTimeout(() => notif.remove(), 300);
                    const storageKey = isShare ? 'dismissedShareNotifs' : 'dismissedChatNotifs';
                    let dismissed = JSON.parse(localStorage.getItem(storageKey) || '[]');
                    if (!dismissed.includes(msg.id)) {
                        dismissed.push(msg.id);
                        if (dismissed.length > 200) dismissed = dismissed.slice(-200);
                        localStorage.setItem(storageKey, JSON.stringify(dismissed));
                    }
                };
            }

            notif.onclick = (e) => {"""

if old_onclick in content:
    content = content.replace(old_onclick, new_onclick)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
