<?php
/**
 * Web Game Launcher Pro - Backup Management Endpoint
 */

ini_set('display_errors', 0);
error_reporting(E_ALL);

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$response = ["status" => "error", "message" => ""];
$backup_dir = __DIR__ . '/backups';
$games_file = __DIR__ . '/games.json';

// Ensure backup directory exists
if (!is_dir($backup_dir)) {
    @mkdir($backup_dir, 0777, true);
    @chmod($backup_dir, 0777);
}

$action = $_GET['action'] ?? '';

if ($_SERVER['REQUEST_METHOD'] === 'GET' && $action === 'list') {
    $files = glob($backup_dir . '/games_*.json');
    $backups = [];
    if ($files) {
        foreach ($files as $file) {
            $backups[] = [
                'filename' => basename($file),
                'size' => filesize($file),
                'time' => filemtime($file)
            ];
        }
        // Sort by time descending
        usort($backups, function($a, $b) {
            return $b['time'] - $a['time'];
        });
    }
    echo json_encode(["status" => "success", "backups" => $backups], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $json_data = file_get_contents('php://input');
    $decoded = json_decode($json_data, true) ?: [];
    $post_action = $decoded['action'] ?? '';

    if ($post_action === 'create') {
        if (!file_exists($games_file)) {
            $response["message"] = "games.json が存在しません";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
            exit;
        }
        $backup_name = $backup_dir . '/games_manual_' . date('Ymd_His') . '_' . uniqid() . '.json';
        if (copy($games_file, $backup_name)) {
            @chmod($backup_name, 0666);
            $response["status"] = "success";
            $response["message"] = "バックアップを作成しました";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
        } else {
            $response["message"] = "バックアップの作成に失敗しました";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
        }
        exit;
    }

    if ($post_action === 'restore') {
        $filename = $decoded['filename'] ?? '';
        if (empty($filename) || strpos($filename, '/') !== false || strpos($filename, '\\') !== false) {
            $response["message"] = "不正なファイル名です";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
            exit;
        }
        $target_backup = $backup_dir . '/' . $filename;
        if (!file_exists($target_backup)) {
            $response["message"] = "バックアップファイルが見つかりません";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
            exit;
        }
        
        // Before restoring, create an auto-backup of the current state just in case
        if (file_exists($games_file)) {
            copy($games_file, $backup_dir . '/games_pre_restore_' . date('Ymd_His') . '.json');
        }

        if (copy($target_backup, $games_file)) {
            @chmod($games_file, 0777);
            $response["status"] = "success";
            $response["message"] = "バックアップから復元しました";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
        } else {
            $response["message"] = "復元に失敗しました。パーミッションを確認してください。";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
        }
        exit;
    }
    
    $response["message"] = "無効なアクションです";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

http_response_code(400);
echo json_encode(["status" => "error", "message" => "Bad Request"], JSON_UNESCAPED_UNICODE);
