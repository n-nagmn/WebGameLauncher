import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Add CSS rules
css_addition = """        body.light-mode .chat-notification-text { color: #333; }
        
        .share-input-box {
            background: rgba(0,0,0,0.4);
            border: 1px solid rgba(255,255,255,0.1);
        }
        body.light-mode .share-input-box {
            background: #fff;
            border-color: #ccc;
        }
"""
content = content.replace("        body.light-mode .chat-notification-text { color: #333; }", css_addition)

# Update HTML to use the class
old_html = """<div style="position: relative; width: 100%; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; background: rgba(0,0,0,0.2); display: flex; flex-direction: column; min-height: 80px; box-sizing: border-box; margin-bottom: 8px;" id="share-input-wrapper">"""
new_html = """<div class="share-input-box" style="position: relative; width: 100%; border-radius: 6px; display: flex; flex-direction: column; min-height: 80px; box-sizing: border-box; margin-bottom: 8px;" id="share-input-wrapper">"""
content = content.replace(old_html, new_html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
