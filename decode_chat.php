<?php
$chat_file = 'W:/var/www/html/WebGameLauncher/chat.json';
if (file_exists($chat_file)) {
    $data = json_decode(file_get_contents($chat_file), true);
    if ($data) {
        $count = 0;
        foreach ($data as &$msg) {
            if (strpos($msg['name'], '&') !== false) {
                $msg['name'] = htmlspecialchars_decode($msg['name'], ENT_QUOTES);
                $count++;
            }
            if (strpos($msg['message'], '&') !== false) {
                $msg['message'] = htmlspecialchars_decode($msg['message'], ENT_QUOTES);
                $count++;
            }
        }
        if ($count > 0) {
            file_put_contents($chat_file, json_encode($data, JSON_UNESCAPED_UNICODE));
            echo "Decoded $count items.";
        } else {
            echo "No items needed decoding.";
        }
    }
}
