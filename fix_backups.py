import re

with open("manage_backups.php", "r", encoding="utf-8") as f:
    content = f.read()

# Add $stamps_file variable
content = content.replace("$share_file = __DIR__ . '/share.json';", "$share_file = __DIR__ . '/share.json';\n$stamps_file = __DIR__ . '/stamps.json';")

# Add stamps.json to zip creation (download)
content = content.replace("if os.path.exists('\" . $share_file . \"'): zf.write('\" . $share_file . \"', 'share.json')", "if os.path.exists('\" . $share_file . \"'): zf.write('\" . $share_file . \"', 'share.json')\n    if os.path.exists('\" . $stamps_file . \"'): zf.write('\" . $stamps_file . \"', 'stamps.json')")

# Add chmod to extraction
content = content.replace("@chmod($share_file, 0777);", "@chmod($share_file, 0777);\n                @chmod($stamps_file, 0777);")

with open("manage_backups.php", "w", encoding="utf-8") as f:
    f.write(content)
