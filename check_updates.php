<?php
/**
 * Web Game Launcher Pro - Link Update Checker (Hybrid V2)
 */

$file_path = __DIR__ . '/games.json';
if (!file_exists($file_path)) die("games.json not found.\n");

$games = json_decode(file_get_contents($file_path), true);
$is_updated = false;

// 内部サーバーのIPやドメイン（これを含むURLは中身をハッシュ比較する）
$internal_hosts = ['172.23.72.107', 'ubuntu.local', 'www.momiji.ip-ddns.com'];

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
            $current_hash = md5($html); // ファイルの内容からハッシュ値を生成
            
            // 前回のハッシュ値と異なる場合 ＝ 中身が更新された！
            if (!isset($game['lastHash']) || $game['lastHash'] !== $current_hash) {
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
                if (!isset($game['remoteUpdatedAt']) || $timestamp > $game['remoteUpdatedAt']) {
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