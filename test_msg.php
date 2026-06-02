<?php
$chat_file = 'W:/var/www/html/WebGameLauncher/chat.json';
$data = [];
if (file_exists($chat_file)) {
    $data = json_decode(file_get_contents($chat_file), true);
}
$data[] = [
    'id' => uniqid('msg_'),
    'name' => 'System',
    'message' => "/a \n　 ∧＿∧\n　（　´∀｀） 右下のポップアップ通知のテストです！",
    'gameId' => null,
    'timestamp' => time() * 1000
];
file_put_contents($chat_file, json_encode($data, JSON_UNESCAPED_UNICODE));
echo "Message added.";
