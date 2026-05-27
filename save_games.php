<?php
/**
 * Web Game Launcher Pro - Game Data Save Endpoint (Fixed)
 */

ini_set('display_errors', 0);
error_reporting(E_ALL);

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(["status" => "error", "message" => "POSTメソッドのみ許可されています"], JSON_UNESCAPED_UNICODE);
    exit;
}

$response = ["status" => "error", "message" => ""];
$file_path = __DIR__ . '/games.json';
$max_file_size = 5 * 1024 * 1024; // 5MB
$max_games = 500;

// Rate limiting
$rate_limit_file = __DIR__ . '/.rate_limit_games';
$rate_limit_window = 60;
$rate_limit_max = 30;
$client_ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';

function checkRateLimit($file, $ip, $window, $max) {
    $data = [];
    if (file_exists($file)) {
        $raw = file_get_contents($file);
        $data = json_decode($raw, true) ?: [];
    }
    $now = time();
    $key = md5($ip);
    if (isset($data[$key])) {
        $data[$key] = array_filter($data[$key], function($t) use ($now, $window) {
            return ($now - $t) < $window;
        });
        if (count($data[$key]) >= $max) return false;
    }
    $data[$key][] = $now;
    file_put_contents($file, json_encode($data), LOCK_EX);
    return true;
}

if (!checkRateLimit($rate_limit_file, $client_ip, $rate_limit_window, $rate_limit_max)) {
    http_response_code(429);
    $response["message"] = "リクエストが多すぎます。しばらく経ってからお試しください。";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

$json_data = file_get_contents('php://input');

if (empty($json_data)) {
    $response["message"] = "データが空です";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

if (strlen($json_data) > $max_file_size) {
    $response["message"] = "データサイズが大きすぎます（最大5MB）";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

$decoded = json_decode($json_data, true);
if ($decoded === null && strtolower(trim($json_data)) !== 'null') {
    $response["message"] = "JSONの形式が不正です: " . json_last_error_msg();
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

if (!is_array($decoded)) {
    $response["message"] = "ゲームデータは配列である必要があります";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

if (count($decoded) > $max_games) {
    $response["message"] = "ゲーム数が上限（{$max_games}件）を超えています";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

// --- Start of Active User Merge Logic ---
$existing_games = [];
if (file_exists($file_path)) {
    $existing_raw = file_get_contents($file_path);
    $existing_games = json_decode($existing_raw, true) ?: [];
}
// 既存のアクティブユーザー情報をIDをキーにしたマップにする
$existing_active_map = [];
foreach ($existing_games as $ex_game) {
    if (isset($ex_game['id']) && isset($ex_game['activeUsers']) && is_array($ex_game['activeUsers'])) {
        $existing_active_map[$ex_game['id']] = $ex_game['activeUsers'];
    }
}
$one_hour_ago_ms = (time() - 3600) * 1000;
// --- End of Active User Merge Logic ---

// Validate each game entry
$required_fields = ['id', 'name', 'url'];
$validated = [];
foreach ($decoded as $index => $game) {
    if (!is_array($game)) {
        $response["message"] = "インデックス {$index} のデータが不正です";
        echo json_encode($response, JSON_UNESCAPED_UNICODE);
        exit;
    }

    foreach ($required_fields as $field) {
        if (!isset($game[$field]) || (is_string($game[$field]) && trim($game[$field]) === '')) {
            $response["message"] = "インデックス {$index} の {$field} が不正です";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
            exit;
        }
    }

    $game_id = is_int($game['id']) ? $game['id'] : intval($game['id']);
    
    // アクティブユーザーのマージ処理
    $new_active = isset($game['activeUsers']) && is_array($game['activeUsers']) ? $game['activeUsers'] : [];
    $merged_active = $new_active;
    
    if (isset($existing_active_map[$game_id])) {
        foreach ($existing_active_map[$game_id] as $uid => $ts) {
            // サーバー側で保持している情報の方が新しい場合、または送られてきたデータにそのユーザーがいない場合は保持
            if (!isset($merged_active[$uid]) || $ts > $merged_active[$uid]) {
                $merged_active[$uid] = $ts;
            }
        }
    }
    
    // ついでにサーバー側でも1時間以上前の古いデータを掃除
    $merged_active = array_filter($merged_active, function($ts) use ($one_hour_ago_ms) {
        return $ts > $one_hour_ago_ms;
    });

    $validated[] = [
        'id' => $game_id,
        'name' => htmlspecialchars(mb_substr(trim($game['name']), 0, 100), ENT_QUOTES, 'UTF-8'),
        'url' => filter_var(trim($game['url']), FILTER_VALIDATE_URL) ?: '',
        'image' => isset($game['image']) ? htmlspecialchars(trim($game['image']), ENT_QUOTES, 'UTF-8') : '',    
        'category' => isset($game['category']) ? htmlspecialchars(mb_substr(trim($game['category']), 0, 50), ENT_QUOTES, 'UTF-8') : '',
        'playersMin' => isset($game['playersMin']) ? max(0, intval($game['playersMin'])) : 0,
        'playersMax' => isset($game['playersMax']) ? max(0, intval($game['playersMax'])) : 0,
        'createdAt' => isset($game['createdAt']) ? intval($game['createdAt']) : time() * 1000,
        'updatedAt' => isset($game['updatedAt']) ? intval($game['updatedAt']) : time() * 1000,
        'lastPlayed' => isset($game['lastPlayed']) ? intval($game['lastPlayed']) : 0,
        'hasUpdate' => isset($game['hasUpdate']) ? filter_var($game['hasUpdate'], FILTER_VALIDATE_BOOLEAN) : false,
        'remoteUpdatedAt' => isset($game['remoteUpdatedAt']) ? intval($game['remoteUpdatedAt']) : 0,
        'lastHash' => isset($game['lastHash']) ? htmlspecialchars(trim($game['lastHash']), ENT_QUOTES, 'UTF-8') : '',
        'isPinned' => isset($game['isPinned']) ? filter_var($game['isPinned'], FILTER_VALIDATE_BOOLEAN) : false,
        'activeUsers' => $merged_active
    ];
}

// Try backup (non-critical)
$backup_success = false;
$backup_name = null;

if (file_exists($file_path)) {
    $backup_dir = __DIR__ . '/backups';

    // Try to create backup directory
    if (!is_dir($backup_dir)) {
        $old_umask = umask(0);
        $dir_created = @mkdir($backup_dir, 0755, true);
        umask($old_umask);
    } else {
        $dir_created = true;
    }

    if ($dir_created && is_writable($backup_dir)) {
        $backup_name = $backup_dir . '/games_' . date('Ymd_His') . '_' . uniqid() . '.json';
        if (@copy($file_path, $backup_name)) {
            $backup_success = true;

            // Cleanup old backups (keep 5)
            $backups = glob($backup_dir . '/games_*.json');
            if ($backups && count($backups) > 5) {
                usort($backups, function($a, $b) {
                    return filemtime($a) - filemtime($b);
                });
                foreach (array_slice($backups, 0, count($backups) - 5) as $old) {
                    @unlink($old);
                }
            }
        }
    }
}

// Write data (main operation)
$json_output = json_encode($validated, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
if ($json_output === false) {
    $response["message"] = "JSONエンコードに失敗しました";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

$result = file_put_contents($file_path, $json_output, LOCK_EX);
if ($result !== false) {
    @chmod($file_path, 0644);
    $response["status"] = "success";
    $response["message"] = "保存成功！";
    $response["count"] = count($validated);
    $response["backup"] = $backup_success ? ($backup_name ? basename($backup_name) : 'created') : 'skipped';    
    http_response_code(200);
} else {
    $response["message"] = "games.json への書き込みに失敗しました。パーミッションを確認してください（chmod 666 games.json）";
    http_response_code(500);
}

echo json_encode($response, JSON_UNESCAPED_UNICODE);
