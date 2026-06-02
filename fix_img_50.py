import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('style="max-width: 25%; border-radius: 8px;', 'style="max-width: 50%; border-radius: 8px;')

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
