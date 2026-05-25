<?php

$file_path = __DIR__ . '/games.json';
if (!file_exists($file_path)) die("games.json not found.\n");

$games = json_decode(file_get_contents($file_path), true);
$is_updated = false;

// 内部サーバーのIPやドメイン（これを含むURLは中身をハッシュ比較する）
$internal_hosts = ['172.23.72.107', 'ubuntu.local'];

foreach ($games as &$game) {
    $url = $game['url'];
    if (empty($url)) continue;

    $parsed_url = parse_url($url);
    $host = $parsed_url['host'] ?? '';

    // 内部ホストかどうかを判定
    $is_internal = in_array($host, $internal_hosts);

    if ($is_internal) {
        /* =========================================================
           [内部ゲーム] HTMLをダウンロードしてハッシュ値を比較する
           ========================================================= */
        $html = @file_get_contents($url);
        if ($html !== false) {
            $current_hash = md5($html);
            
            if (empty($game['lastHash'])) {
                // 【初回】ベースとなるハッシュ値を記録するのみ（UPDATEにはしない）
                $game['lastHash'] = $current_hash;
                $game['remoteUpdatedAt'] = time();
                $is_updated = true; // 記録をgames.jsonに保存するためtrueにする
                echo "[Internal] Initial hash recorded: {$game['name']}\n";
            } elseif ($game['lastHash'] !== $current_hash) {
                // 【2回目以降】前回記録したハッシュ値と異なる場合 ＝ 更新！
                $game['lastHash'] = $current_hash;
                $game['hasUpdate'] = true;
                $game['remoteUpdatedAt'] = time();
                $is_updated = true;
                echo "[Internal] Update detected by Hash: {$game['name']}\n";
            }
        }
    } else {
        /* =========================================================
           [外部ゲーム] 誤検知を防ぐため、HTTPヘッダーのみを確認する
           ========================================================= */
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_NOBODY, true); // 中身はDLしない
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HEADER, true);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 5);
        
        $response = curl_exec($ch);
        $info = curl_getinfo($ch);
        curl_close($ch);

        if ($info['http_code'] == 200) {
            if (preg_match('/Last-Modified:\s*(.+)/i', $response, $matches)) {
                $timestamp = strtotime(trim($matches[1]));
                
                if (empty($game['remoteUpdatedAt'])) {
                    // 【初回】ベースとなるヘッダー日時を記録するのみ（UPDATEにはしない）
                    $game['remoteUpdatedAt'] = $timestamp;
                    $is_updated = true;
                    echo "[External] Initial header recorded: {$game['name']}\n";
                } elseif ($timestamp > $game['remoteUpdatedAt']) {
                    // 【2回目以降】記録されている日時より新しい場合 ＝ 更新！
                    $game['remoteUpdatedAt'] = $timestamp;
                    $game['hasUpdate'] = true;
                    $is_updated = true;
                    echo "[External] Update detected by Header: {$game['name']}\n";
                }
            }
        }
    }
}

if ($is_updated) {
    file_put_contents($file_path, json_encode($games, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
    echo "games.json has been updated.\n";
} else {
    echo "No updates found.\n";
}