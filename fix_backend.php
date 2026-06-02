<?php
$f = 'W:/var/www/html/WebGameLauncher/post_chat.php';
$c = file_get_contents($f);

// Fix name line
$name_old = "\$name = isset(\$decoded['name']) ? htmlspecialchars(mb_substr(trim(\$decoded['name']), 0, 30), ENT_QUOTES, 'UTF-8') : '名無し';";
$name_new = "\$name = isset(\$decoded['name']) ? mb_substr(trim(\$decoded['name']), 0, 30, 'UTF-8') : '名無し';";
$c = str_replace($name_old, $name_new, $c);

// Fix message line
$msg_old = "\$message = isset(\$decoded['message']) ? htmlspecialchars(mb_substr(trim(\$decoded['message']), 0, 200), ENT_QUOTES, 'UTF-8') : '';";
$msg_new = "\$message = isset(\$decoded['message']) ? mb_substr(trim(\$decoded['message']), 0, 2000, 'UTF-8') : '';";
$c = str_replace($msg_old, $msg_new, $c);

// Fix gameId line
$game_old = "\$gameId = !empty(\$decoded['gameId']) ? htmlspecialchars(trim(\$decoded['gameId']), ENT_QUOTES, 'UTF-8') : null;";
$game_new = "\$gameId = !empty(\$decoded['gameId']) ? trim(\$decoded['gameId']) : null;";
$c = str_replace($game_old, $game_new, $c);

file_put_contents($f, $c);
echo "Backend fixed";
$chat_file = 'W:/var/www/html/WebGameLauncher/chat.json'; if (file_exists($chat_file)) { $data = json_decode(file_get_contents($chat_file), true); if ($data) { foreach ($data as &$msg) { $msg['name'] = htmlspecialchars_decode($msg['name'], ENT_QUOTES); $msg['message'] = htmlspecialchars_decode($msg['message'], ENT_QUOTES); } file_put_contents($chat_file, json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT)); } }
