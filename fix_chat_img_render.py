import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

old_chat_img_render = """${msg.imageUrl ? `<div style="margin-top: 8px;"><a href="${escapeHtml(msg.imageUrl)}" target="_blank"><img src="${escapeHtml(msg.imageUrl)}" style="max-width: 50%; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);" alt="Image"></a></div>` : ''}"""
new_chat_img_render = """${msg.imageUrl ? `<div style="margin-top: 8px;"><img src="${escapeHtml(msg.imageUrl)}" onclick="App.openImageModal('${escapeHtml(msg.imageUrl)}')" style="max-width: 50%; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); cursor: zoom-in;" alt="Image"></div>` : ''}"""
content = content.replace(old_chat_img_render, new_chat_img_render)

old_paste = """        window.addEventListener('paste', e => {
            if (!document.getElementById('share-sidebar').classList.contains('active')) return;
            const items = e.clipboardData.items;
            for (let i = 0; i < items.length; i++) {
                if (items[i].type.indexOf('image') !== -1) {
                    const file = items[i].getAsFile();
                    const dt = new DataTransfer();
                    dt.items.add(file);
                    document.getElementById('share-image').files = dt.files;
                    handleShareImageSelect();
                    break;
                }
            }
        });"""
new_paste = """        window.addEventListener('paste', e => {
            const shareActive = document.getElementById('share-sidebar').classList.contains('active');
            const chatActive = document.getElementById('chat-sidebar').classList.contains('active');
            if (!shareActive && !chatActive) return;
            
            const items = e.clipboardData.items;
            for (let i = 0; i < items.length; i++) {
                if (items[i].type.indexOf('image') !== -1) {
                    const file = items[i].getAsFile();
                    const dt = new DataTransfer();
                    dt.items.add(file);
                    if (shareActive) {
                        document.getElementById('share-image').files = dt.files;
                        handleShareImageSelect();
                    } else if (chatActive) {
                        document.getElementById('chat-image').files = dt.files;
                        handleChatImageSelect();
                    }
                    break;
                }
            }
        });"""
content = content.replace(old_paste, new_paste)

old_exports = """            openImageModal, closeImageModal,
            toggleReactionPicker, reactMessage,
            startReply, cancelReply
        };"""
new_exports = """            openImageModal, closeImageModal,
            toggleReactionPicker, reactMessage,
            startReply, cancelReply,
            handleChatImageSelect, clearChatImage
        };"""
content = content.replace(old_exports, new_exports)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
