import re

with open("post_chat.php", "r", encoding="utf-8") as f:
    content = f.read()

# Suppress warnings
content = content.replace("fopen($lock_file, 'w')", "@fopen($lock_file, 'w')")
content = content.replace("file_put_contents($file_path,", "@file_put_contents($file_path,")

with open("post_chat.php", "w", encoding="utf-8") as f:
    f.write(content)
