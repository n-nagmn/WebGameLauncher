import re

with open("post_share.php", "r", encoding="utf-8") as f:
    content = f.read()

old_logic = """$clientId = isset($decoded['clientId']) ? trim($decoded['clientId']) : null;

$new_message = [
    'id' => uniqid('msg_'),
    'name' => $name,
    'message' => $message,
    'gameId' => $gameId,
    'timestamp' => $timestamp,
    'clientId' => $clientId,
    'imageUrl' => $imageUrl
];"""

new_logic = """$clientId = isset($decoded['clientId']) ? trim($decoded['clientId']) : null;
$replyTo = isset($decoded['replyTo']) ? (is_string($decoded['replyTo']) ? json_decode($decoded['replyTo'], true) : $decoded['replyTo']) : null;

$new_message = [
    'id' => uniqid('msg_'),
    'name' => $name,
    'message' => $message,
    'gameId' => $gameId,
    'timestamp' => $timestamp,
    'clientId' => $clientId,
    'imageUrl' => $imageUrl,
    'replyTo' => $replyTo
];"""

content = content.replace(old_logic, new_logic)

with open("post_share.php", "w", encoding="utf-8") as f:
    f.write(content)
