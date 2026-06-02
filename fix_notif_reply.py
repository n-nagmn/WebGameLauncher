import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

old_notif_html = """            notif.innerHTML = `
                <div class="chat-notification-header" style="position: relative; padding-right: 20px;">"""

new_notif_html = """            notif.innerHTML = `
                ${msg.replyTo ? `<div class="replied-message" style="margin-bottom: 4px;">
                    <strong>@${escapeHtml(msg.replyTo.name)}</strong>&nbsp; ${escapeHtml(msg.replyTo.message)}
                </div>` : ''}
                <div class="chat-notification-header" style="position: relative; padding-right: 20px;">"""

content = content.replace(old_notif_html, new_notif_html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
