import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Add CSS class
css_target = "        /* Responsive */"
css_new = """        .chat-sidebar.drag-over::after {
            content: '';
            position: absolute;
            top: 10px; left: 10px; right: 10px; bottom: 10px;
            border: 3px dashed var(--focus-color);
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            pointer-events: none;
            z-index: 1000;
        }

        /* Responsive */"""
if "drag-over::after" not in content:
    content = content.replace(css_target, css_new)

# Modify setupShareDragAndDrop
old_drag = """            dropZone.addEventListener('dragover', e => {
                e.preventDefault();
            });
            dropZone.addEventListener('dragleave', e => {
                e.preventDefault();
            });
            dropZone.addEventListener('drop', e => {
                e.preventDefault();"""

new_drag = """            dropZone.addEventListener('dragover', e => {
                e.preventDefault();
                dropZone.classList.add('drag-over');
            });
            dropZone.addEventListener('dragleave', e => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');
            });
            dropZone.addEventListener('drop', e => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');"""

if old_drag in content:
    content = content.replace(old_drag, new_drag)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
