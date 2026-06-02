import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

old_clear = """                    const msgInput = document.getElementById('share-message');
                    if (msgInput) msgInput.value = '';
                    clearShareImage();"""

new_clear = """                    const msgInput = document.getElementById('share-message');
                    if (msgInput) {
                        msgInput.value = '';
                        msgInput.style.height = 'auto';
                    }
                    clearShareImage();"""
content = content.replace(old_clear, new_clear)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
