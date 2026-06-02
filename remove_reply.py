import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove chat-reply-preview block
reply_preview_html = """            <div id="chat-reply-preview" style="display:none; padding: 8px; background: rgba(0,0,0,0.3); font-size: 11px; color: #aaa; border-left: 3px solid var(--focus-color); border-radius: 0 4px 4px 0;">
                <div style="display:flex; justify-content:space-between; margin-bottom: 2px;">
                    <span id="chat-reply-name" style="font-weight:bold; color: var(--focus-color);"></span>
                    <span style="cursor:pointer; font-size: 14px; line-height: 1;" onclick="App.cancelReply()">×</span>
                </div>
                <div id="chat-reply-text" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"></div>
            </div>
"""
html = html.replace(reply_preview_html, '')

# 2. Remove chat-reply-btn
html = re.sub(r'<button class="chat-reply-btn"[^>]*>返信</button>', '', html)

# 3. Remove msg.replyTo render block
reply_block_re = r"\s*\$\(\(\) => \{\s*if \(!msg\.replyTo\) return '';\s*const repliedMsg = chatMessages\.find\(m => m\.id === msg\.replyTo\);\s*if \(repliedMsg\) \{\s*let rName = repliedMsg\.name \|\| '名無しさん';\s*let rText = repliedMsg\.message \|\| '';\s*return `<div class=\"chat-reply-block\"[^>]*><strong>\$\{escapeHtml\(rName\)\}</strong>: \$\{escapeHtml\(rText\.substring\(0, 50\)\)\}\$\{rText\.length>50\?'\.\.\.':''\}</div>`;\s*\} else \{\s*return `<div class=\"chat-reply-block\"[^>]*><em>返信元のメッセージは削除されました</em></div>`;\s*\}\s*\}\)\(\)\}"
html = re.sub(reply_block_re, '', html)

# 4. Remove currentReplyToId and functions
funcs_re = r"\s*let currentReplyToId = null;\s*function initiateReply\(msgId\) \{.*?\}\s*function cancelReply\(\) \{.*?\}"
html = re.sub(funcs_re, '', html, flags=re.DOTALL)

# 5. Remove cancelReply calls
html = re.sub(r'\s*if \(typeof cancelReply === \'function\'\) cancelReply\(\);', '', html)
html = re.sub(r'\s*cancelReply\(\);', '', html)

# 6. Remove replyTo from payload
html = re.sub(r',\s*replyTo:\s*currentReplyToId', '', html)

# 7. Remove from exports
html = re.sub(r',\s*initiateReply,\s*cancelReply', '', html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
