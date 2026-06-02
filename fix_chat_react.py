import re
import os

with open("post_chat.php", "r", encoding="utf-8") as f:
    content = f.read()

react_logic = """    if ($action === 'react') {
        $timestamp = $data['timestamp'] ?? 0;
        $emoji = $data['emoji'] ?? '';
        $clientId = $data['clientId'] ?? '';
        if (!$timestamp || !$emoji || !$clientId) {
            http_response_code(400);
            echo json_encode(["status" => "error", "message" => "Missing react data"]);
            exit;
        }

        $file = __DIR__ . '/chat.json';
        $chat = [];
        if (file_exists($file)) {
            $chat = json_decode(file_get_contents($file), true) ?: [];
        }

        $updated = false;
        foreach ($chat as &$msg) {
            if (isset($msg['timestamp']) && $msg['timestamp'] === $timestamp) {
                if (!isset($msg['reactions'])) {
                    $msg['reactions'] = [];
                }
                if (!isset($msg['reactions'][$emoji])) {
                    $msg['reactions'][$emoji] = [];
                }
                
                $idx = array_search($clientId, $msg['reactions'][$emoji]);
                if ($idx !== false) {
                    // Remove reaction
                    array_splice($msg['reactions'][$emoji], $idx, 1);
                    if (empty($msg['reactions'][$emoji])) {
                        unset($msg['reactions'][$emoji]);
                    }
                } else {
                    // Add reaction
                    $msg['reactions'][$emoji][] = $clientId;
                }
                $updated = true;
                break;
            }
        }
        
        if ($updated) {
            file_put_contents($file, json_encode($chat, JSON_UNESCAPED_UNICODE));
            echo json_encode(["status" => "success"]);
        } else {
            http_response_code(404);
            echo json_encode(["status" => "error", "message" => "Message not found"]);
        }
        exit;
    }

    if ($action === 'delete') {"""

content = content.replace("    if ($action === 'delete') {", react_logic)

with open("post_chat.php", "w", encoding="utf-8") as f:
    f.write(content)
