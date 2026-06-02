import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

old_click = """            notif.onclick = (e) => {
                e.stopPropagation();
                notif.classList.add('hiding');
                setTimeout(() => notif.remove(), 300);
                let dismissed = JSON.parse(localStorage.getItem('dismissedChatNotifs') || '[]');
                if (!dismissed.includes(msg.id)) {
                    dismissed.push(msg.id);
                    if (dismissed.length > 200) dismissed = dismissed.slice(-200);
                    localStorage.setItem('dismissedChatNotifs', JSON.stringify(dismissed));
                }
                if (msg.gameId) {
                    openChatGame(msg.gameId);
                }
            };"""

new_click = """            notif.onclick = (e) => {
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
                if (msg.gameId) {
                    openChatGame(msg.gameId);
                }
            };"""

if old_click in content:
    content = content.replace(old_click, new_click)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
