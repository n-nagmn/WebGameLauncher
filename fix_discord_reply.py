import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Add CSS for .replied-message
css_to_add = """        .chat-message-text { word-break: break-word; line-height: 1.4; color: #eee; white-space: pre-wrap; user-select: text; }
        
        .replied-message {
            display: flex;
            align-items: center;
            font-size: 11px;
            color: #b9bbbe;
            margin-bottom: 2px;
            padding-left: 28px;
            position: relative;
            user-select: none;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .replied-message::before {
            content: '';
            position: absolute;
            display: block;
            top: 50%;
            left: 12px;
            width: 12px;
            height: 10px;
            border-left: 2px solid #4f545c;
            border-top: 2px solid #4f545c;
            border-top-left-radius: 6px;
            box-sizing: border-box;
        }
        body.light-mode .replied-message { color: #5c5e66; }
        body.light-mode .replied-message::before { border-color: #c4c9ce; }"""

content = content.replace("        .chat-message-text { word-break: break-word; line-height: 1.4; color: #eee; white-space: pre-wrap; user-select: text; }", css_to_add)

# Modify renderChat and renderShare replyTo format
old_reply_html = """${msg.replyTo ? `<div style="font-size: 11px; color: gray; margin-bottom: 2px; padding-left: 12px; border-left: 2px solid gray; display: flex; align-items: center; gap: 4px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; border-radius: 2px; background: rgba(128,128,128,0.05); padding: 2px 4px 2px 8px;">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;"><polyline points="9 17 4 12 9 7"></polyline><path d="M20 18v-2a4 4 0 0 0-4-4H4"></path></svg>
                            <strong>${escapeHtml(msg.replyTo.name)}</strong>: ${escapeHtml(msg.replyTo.message)}
                        </div>` : ''}"""

new_reply_html = """${msg.replyTo ? `<div class="replied-message">
                            <strong>@${escapeHtml(msg.replyTo.name)}</strong>&nbsp; ${escapeHtml(msg.replyTo.message)}
                        </div>` : ''}"""

content = content.replace(old_reply_html, new_reply_html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
