import re

with open("post_share.php", "r", encoding="utf-8") as f:
    content = f.read()

# Fix error messages
content = content.replace('"chat.json への書き込みに失敗しました。"', '"share.json への書き込みに失敗しました。"')

# Suppress warnings
content = content.replace("fopen($lock_file, 'w')", "@fopen($lock_file, 'w')")
content = content.replace("file_put_contents($file_path,", "@file_put_contents($file_path,")
content = content.replace("move_uploaded_file(", "@move_uploaded_file(")

with open("post_share.php", "w", encoding="utf-8") as f:
    f.write(content)
