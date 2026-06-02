import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

old_drag = """            dropZone.addEventListener('dragover', e => {
                e.preventDefault();
                dropZone.style.opacity = '0.8';
            });
            dropZone.addEventListener('dragleave', e => {
                e.preventDefault();
                dropZone.style.opacity = '';
            });
            dropZone.addEventListener('drop', e => {
                e.preventDefault();
                dropZone.style.opacity = '';"""

new_drag = """            dropZone.addEventListener('dragover', e => {
                e.preventDefault();
            });
            dropZone.addEventListener('dragleave', e => {
                e.preventDefault();
            });
            dropZone.addEventListener('drop', e => {
                e.preventDefault();"""

if old_drag in content:
    content = content.replace(old_drag, new_drag)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
