import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

old_chat = """                        } else {
                            let dismissed = JSON.parse(localStorage.getItem('dismissedChatNotifs') || '[]');
                            const oneDayAgo = Date.now() - (24 * 60 * 60 * 1000);
                            newMessages.forEach(msg => {
                                if (msg.clientId !== myClientId && !dismissed.includes(msg.id) && msg.timestamp > oneDayAgo) {
                                    showChatNotification(msg);
                                }
                            });
                        }"""
new_chat = """                        } else {
                            let dismissed = JSON.parse(localStorage.getItem('dismissedChatNotifs') || '[]');
                            newMessages.forEach(msg => {
                                if (msg.clientId !== myClientId && !dismissed.includes(msg.id)) {
                                    showChatNotification(msg);
                                }
                            });
                        }"""
if old_chat in content:
    content = content.replace(old_chat, new_chat)

old_share = """                        } else {
                            let dismissed = JSON.parse(localStorage.getItem('dismissedShareNotifs') || '[]');
                            const oneDayAgo = Date.now() - (24 * 60 * 60 * 1000);
                            newMessages.forEach(msg => {
                                if (msg.clientId !== myClientId && !dismissed.includes(msg.id) && msg.timestamp > oneDayAgo) {
                                    showChatNotification(msg, true);
                                }
                            });
                        }"""
new_share = """                        } else {
                            let dismissed = JSON.parse(localStorage.getItem('dismissedShareNotifs') || '[]');
                            newMessages.forEach(msg => {
                                if (msg.clientId !== myClientId && !dismissed.includes(msg.id)) {
                                    showChatNotification(msg, true);
                                }
                            });
                        }"""
if old_share in content:
    content = content.replace(old_share, new_share)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
