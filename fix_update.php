<?php
$file = __DIR__ . '/games.json';
$data = json_decode(file_get_contents($file), true);
foreach($data as &$game) {
    if (isset($game['createdAt'])) {
        $game['updatedAt'] = $game['createdAt'];
    }
}
file_put_contents($file, json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
echo "Fixed";
