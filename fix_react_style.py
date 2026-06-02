import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update window click listener
old_click = """                const isImageModalClick = e.target.closest('#image-modal') || (mousedownTarget && mousedownTarget.closest('#image-modal'));
                
                // Close chat if clicked outside (and not on a chat element or open button)
                const chatSidebar = document.getElementById('chat-sidebar');
                if (chatSidebar.classList.contains('active') && 
                    !chatSidebar.contains(e.target) && 
                    !e.target.closest('.chat-btn') && 
                    !isImageModalClick) {
                    if (mousedownTarget && !chatSidebar.contains(mousedownTarget) && !mousedownTarget.closest('.chat-btn')) {
                        closeChat();
                    }
                }
                
                const shareSidebar = document.getElementById('share-sidebar');
                if (shareSidebar.classList.contains('active') && 
                    !shareSidebar.contains(e.target) && 
                    !e.target.closest('.share-btn') && 
                    !isImageModalClick) {
                    if (mousedownTarget && !shareSidebar.contains(mousedownTarget) && !mousedownTarget.closest('.share-btn')) {
                        closeShare();
                    }
                }"""
new_click = """                const isImageModalClick = e.target.closest('#image-modal') || (mousedownTarget && mousedownTarget.closest('#image-modal'));
                const isPickerClick = e.target.closest('#reaction-picker') || (mousedownTarget && mousedownTarget.closest('#reaction-picker'));
                
                // Close chat if clicked outside (and not on a chat element or open button)
                const chatSidebar = document.getElementById('chat-sidebar');
                if (chatSidebar.classList.contains('active') && 
                    !chatSidebar.contains(e.target) && 
                    !e.target.closest('.chat-btn') && 
                    !isImageModalClick && !isPickerClick) {
                    if (mousedownTarget && !chatSidebar.contains(mousedownTarget) && !mousedownTarget.closest('.chat-btn')) {
                        closeChat();
                    }
                }
                
                const shareSidebar = document.getElementById('share-sidebar');
                if (shareSidebar.classList.contains('active') && 
                    !shareSidebar.contains(e.target) && 
                    !e.target.closest('.share-btn') && 
                    !isImageModalClick && !isPickerClick) {
                    if (mousedownTarget && !shareSidebar.contains(mousedownTarget) && !mousedownTarget.closest('.share-btn')) {
                        closeShare();
                    }
                }"""
if old_click in content:
    content = content.replace(old_click, new_click)

# 2. Add CSS for reaction-btn
css = """        .reaction-btn {
            background: rgba(128,128,128,0.1);
            border: 1px solid rgba(128,128,128,0.3);
            border-radius: 12px;
            padding: 2px 6px;
            font-size: 11px;
            color: inherit;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 4px;
            transition: all 0.2s;
        }
        .reaction-btn:hover {
            background: rgba(128,128,128,0.2);
        }
        .reaction-btn.reacted {
            background: rgba(0, 123, 255, 0.15);
            border-color: #007bff;
            color: #007bff;
        }
        .light-mode .reaction-btn.reacted {
            background: rgba(0, 123, 255, 0.1);
            color: #0056b3;
            border-color: #007bff;
        }"""
content = content.replace("    </style>", css + "\n    </style>")

# 3. Replace inline styles with reaction-btn class
import re

old_chat_render = """                                return `<button style="background: ${reacted ? 'rgba(0,123,255,0.2)' : 'rgba(128,128,128,0.1)'}; border: 1px solid ${reacted ? '#007bff' : 'rgba(128,128,128,0.3)'}; border-radius: 12px; padding: 2px 6px; font-size: 11px; color: inherit; cursor: pointer; display: flex; align-items: center; gap: 4px;" onclick="App.reactMessage('${emoji}', ${msg.timestamp}, false)">${emoji} <span>${count}</span></button>`;"""
new_chat_render = """                                return `<button class="reaction-btn ${reacted ? 'reacted' : ''}" onclick="App.reactMessage('${emoji}', ${msg.timestamp}, false)">${emoji} <span>${count}</span></button>`;"""
content = content.replace(old_chat_render, new_chat_render)

old_chat_add = """                            <button class="add-reaction-btn" style="background: rgba(128,128,128,0.1); border: 1px solid rgba(128,128,128,0.3); border-radius: 12px; padding: 2px 6px; font-size: 11px; color: inherit; cursor: pointer; display: flex; align-items: center; justify-content: center; width: 24px;" onclick="App.toggleReactionPicker(${msg.timestamp}, false, this, event)">+</button>"""
new_chat_add = """                            <button class="add-reaction-btn reaction-btn" style="width: 24px; justify-content: center;" onclick="App.toggleReactionPicker(${msg.timestamp}, false, this, event)">+</button>"""
content = content.replace(old_chat_add, new_chat_add)

old_share_render = """                                return `<button style="background: ${reacted ? 'var(--focus-color)' : 'rgba(128,128,128,0.1)'}; filter: ${reacted ? 'brightness(0.6)' : 'none'}; border: 1px solid ${reacted ? 'var(--focus-color)' : 'rgba(128,128,128,0.3)'}; border-radius: 12px; padding: 2px 6px; font-size: 11px; color: inherit; cursor: pointer; display: flex; align-items: center; gap: 4px;" onclick="App.reactMessage('${emoji}', ${msg.timestamp}, true)">${emoji} <span>${count}</span></button>`;"""
new_share_render = """                                return `<button class="reaction-btn ${reacted ? 'reacted' : ''}" onclick="App.reactMessage('${emoji}', ${msg.timestamp}, true)">${emoji} <span>${count}</span></button>`;"""
content = content.replace(old_share_render, new_share_render)

old_share_add = """                            <button class="add-reaction-btn" style="background: rgba(128,128,128,0.1); border: 1px solid rgba(128,128,128,0.3); border-radius: 12px; padding: 2px 6px; font-size: 11px; color: inherit; cursor: pointer; display: flex; align-items: center; justify-content: center; width: 24px;" onclick="App.toggleReactionPicker(${msg.timestamp}, true, this, event)">+</button>"""
new_share_add = """                            <button class="add-reaction-btn reaction-btn" style="width: 24px; justify-content: center;" onclick="App.toggleReactionPicker(${msg.timestamp}, true, this, event)">+</button>"""
content = content.replace(old_share_add, new_share_add)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
