import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update fetchShare to include notification logic
old_fetch_share = """        async function fetchShare() {
            try {
                const res = await fetch('./share.json?t=' + Date.now());
                if (res.ok) {
                    const newMessages = await res.json();
                    if (JSON.stringify(newMessages) !== JSON.stringify(shareMessages)) {
                        shareMessages = newMessages;
                        initialShareLoaded = true;
                        renderShare();
                    } else {
                        initialShareLoaded = true;
                    }
                }
            } catch (e) {
                console.error(e);
            }
        }"""

new_fetch_share = """        async function fetchShare() {
            try {
                const res = await fetch('./share.json?t=' + Date.now());
                if (res.ok) {
                    const newMessages = await res.json();
                    if (JSON.stringify(newMessages) !== JSON.stringify(shareMessages)) {
                        // Remove notifications for deleted messages
                        document.querySelectorAll('.chat-notification').forEach(notif => {
                            const ts = parseInt(notif.dataset.timestamp);
                            const nName = notif.dataset.name;
                            const nMsg = notif.dataset.messageText;
                            if (ts && !newMessages.some(m => 
                                (m.timestamp === ts) || 
                                (m.name === nName && m.message === nMsg && Math.abs(m.timestamp - ts) < 60000)
                            ) && notif.dataset.isShare === 'true') {
                                notif.classList.add('hiding');
                                setTimeout(() => notif.remove(), 300);
                            }
                        });

                        // Check for new messages from others
                        if (initialShareLoaded) {
                            const newItems = newMessages.filter(m => !shareMessages.some(old => old.id === m.id) && m.clientId !== myClientId);
                            newItems.forEach(msg => {
                                showChatNotification(msg, true);
                            });
                        } else {
                            let dismissed = JSON.parse(localStorage.getItem('dismissedShareNotifs') || '[]');
                            const oneDayAgo = Date.now() - (24 * 60 * 60 * 1000);
                            newMessages.forEach(msg => {
                                if (msg.clientId !== myClientId && !dismissed.includes(msg.id) && msg.timestamp > oneDayAgo) {
                                    showChatNotification(msg, true);
                                }
                            });
                        }
                        shareMessages = newMessages;
                        initialShareLoaded = true;
                        renderShare();
                    } else {
                        initialShareLoaded = true;
                    }
                }
            } catch (e) {
                console.error(e);
            }
        }"""
content = content.replace(old_fetch_share, new_fetch_share)

# 2. Update showChatNotification to handle isShare
old_show_notif = """        function showChatNotification(msg) {
            const container = document.getElementById('chat-notification-container');
            const notif = document.createElement('div');
            notif.className = 'chat-notification';
            
            const timeStr = new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            const name = msg.name || '名無しさん';
            
            notif.dataset.timestamp = msg.timestamp;
            notif.dataset.name = name;
            notif.dataset.messageText = msg.message;"""

new_show_notif = """        function showChatNotification(msg, isShare = false) {
            const container = document.getElementById('chat-notification-container');
            const notif = document.createElement('div');
            notif.className = 'chat-notification';
            
            const timeStr = new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            const name = msg.name || '名無しさん';
            
            notif.dataset.timestamp = msg.timestamp;
            notif.dataset.name = name;
            notif.dataset.messageText = msg.message;
            if (isShare) notif.dataset.isShare = 'true';"""
content = content.replace(old_show_notif, new_show_notif)

# Update onclick logic
old_onclick = """            notif.onclick = (e) => {
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
                } else {
                    openChat();
                }
            };"""

new_onclick = """            notif.onclick = (e) => {
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
                } else {
                    if (isShare) openShare(); else openChat();
                }
            };"""
content = content.replace(old_onclick, new_onclick)

# Update submitShare optimistic call
content = content.replace("showChatNotification(tempMsg);", "showChatNotification(tempMsg, true);")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
