<?php
/**
 * Web Game Launcher Pro - Link Update Checker
 * cron等で定期実行することを想定（例: 1日1回）
 */

$file_path = __DIR__ . '/games.json';
if (!file_exists($file_path)) {
    die("games.json not found.\n");
}

$json_data = file_get_contents($file_path);
$games = json_decode($json_data, true);
$is_updated = false;

foreach ($games as &$game) {
    $url = $game['url'];
    if (empty($url)) continue;

    // cURLでHEADリクエストを送信（ファイル本体はダウンロードしない）
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_NOBODY, true);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HEADER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 5); // タイムアウト5秒
    
    $response = curl_exec($ch);
    $info = curl_getinfo($ch);
    curl_close($ch);

    if ($info['http_code'] == 200) {
        // ヘッダーから Last-Modified を抽出
        if (preg_match('/Last-Modified:\s*(.+)/i', $response, $matches)) {
            $last_modified_str = trim($matches[1]);
            $timestamp = strtotime($last_modified_str);

            // 前回の更新記録がない、または前回より新しい場合
            if (!isset($game['remoteUpdatedAt']) || $timestamp > $game['remoteUpdatedAt']) {
                $game['remoteUpdatedAt'] = $timestamp;
                $game['hasUpdate'] = true; // クライアント側に知らせるフラグ
                $is_updated = true;
                echo "Updated detected: {$game['name']}\n";
            }
        }
    }
}

// 変更があった場合のみ保存
if ($is_updated) {
    file_put_contents($file_path, json_encode($games, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
    echo "games.json has been updated.\n";
} else {
    echo "No updates found.\n";
}