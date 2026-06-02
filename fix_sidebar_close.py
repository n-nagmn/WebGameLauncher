import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

old_click = """                const chatSidebar = document.getElementById('chat-sidebar');
                if (chatSidebar.classList.contains('active') && 
                    !chatSidebar.contains(e.target) && 
                    !e.target.closest('.chat-btn')) {
                    if (mousedownTarget && !chatSidebar.contains(mousedownTarget) && !mousedownTarget.closest('.chat-btn')) {
                        closeChat();
                    }
                }

                const shareSidebar = document.getElementById('share-sidebar');
                if (shareSidebar.classList.contains('active') && 
                    !shareSidebar.contains(e.target) && 
                    !e.target.closest('.share-btn')) {
                    if (mousedownTarget && !shareSidebar.contains(mousedownTarget) && !mousedownTarget.closest('.share-btn')) {
                        closeShare();
                    }
                }"""

new_click = """                const isImageModalClick = e.target.closest('#image-modal') || (mousedownTarget && mousedownTarget.closest('#image-modal'));

                const chatSidebar = document.getElementById('chat-sidebar');
                if (chatSidebar.classList.contains('active') && 
                    !chatSidebar.contains(e.target) && 
                    !e.target.closest('.chat-btn') && !isImageModalClick) {
                    if (mousedownTarget && !chatSidebar.contains(mousedownTarget) && !mousedownTarget.closest('.chat-btn')) {
                        closeChat();
                    }
                }

                const shareSidebar = document.getElementById('share-sidebar');
                if (shareSidebar.classList.contains('active') && 
                    !shareSidebar.contains(e.target) && 
                    !e.target.closest('.share-btn') && !isImageModalClick) {
                    if (mousedownTarget && !shareSidebar.contains(mousedownTarget) && !mousedownTarget.closest('.share-btn')) {
                        closeShare();
                    }
                }"""

if old_click in content:
    content = content.replace(old_click, new_click)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
