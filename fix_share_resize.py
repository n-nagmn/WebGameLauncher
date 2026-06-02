import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

old_init = """            }
            setupShareDragAndDrop();
            els.gameModal = document.getElementById('game-modal');"""

new_init = """            }
            
            const shareMsgInput = document.getElementById('share-message');
            if (shareMsgInput) {
                shareMsgInput.addEventListener('keydown', e => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        submitShare();
                    }
                });
                shareMsgInput.addEventListener('input', function() {
                    this.style.height = 'auto';
                    const maxH = window.innerHeight * 0.5;
                    const newHeight = Math.min(this.scrollHeight, maxH);
                    this.style.height = newHeight + 'px';
                    this.style.overflowY = this.scrollHeight > maxH ? 'auto' : 'hidden';
                });
            }

            setupShareDragAndDrop();
            els.gameModal = document.getElementById('game-modal');"""

content = content.replace(old_init, new_init)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
