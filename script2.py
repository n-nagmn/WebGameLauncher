import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 6. init polling update
content = content.replace("setInterval(fetchChat, 3000);", "setInterval(fetchChat, 3000);\n            fetchShare();\n            setInterval(fetchShare, 3000);")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
