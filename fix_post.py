import re

with open("manage_backups.php", "r", encoding="utf-8") as f:
    content = f.read()

old_post_action = """    $json_data = file_get_contents('php://input');
    $decoded = json_decode($json_data, true) ?: [];
    $post_action = $decoded['action'] ?? '';"""

new_post_action = """    $json_data = file_get_contents('php://input');
    $decoded = json_decode($json_data, true) ?: [];
    $post_action = $decoded['action'] ?? $_POST['action'] ?? '';"""

if old_post_action in content:
    content = content.replace(old_post_action, new_post_action)

with open("manage_backups.php", "w", encoding="utf-8") as f:
    f.write(content)
