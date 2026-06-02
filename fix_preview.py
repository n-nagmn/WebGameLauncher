import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove preview frame background and padding
old_preview = """<div id="share-image-preview-container" style="display: none; position: relative; margin: 0 10px 10px 10px; width: fit-content; background: rgba(128,128,128,0.1); padding: 4px; border-radius: 6px;">"""
new_preview = """<div id="share-image-preview-container" style="display: none; position: relative; margin: 0 10px 10px 10px; width: fit-content;">"""

if old_preview in content:
    content = content.replace(old_preview, new_preview)

# 2. Fix drag and drop style
old_dragover = """            dropZone.addEventListener('dragover', e => {
                e.preventDefault();
                dropZone.style.background = 'rgba(255,255,255,0.05)';
            });
            dropZone.addEventListener('dragleave', e => {
                e.preventDefault();
                dropZone.style.background = '';
            });
            dropZone.addEventListener('drop', e => {
                e.preventDefault();
                dropZone.style.background = '';"""

new_dragover = """            dropZone.addEventListener('dragover', e => {
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

if old_dragover in content:
    content = content.replace(old_dragover, new_dragover)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
