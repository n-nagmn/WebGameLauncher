<?php
/**
 * Web Game Launcher Pro - Backup Management Endpoint
 */

ini_set('display_errors', 0);
error_reporting(E_ALL);

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$response = ["status" => "error", "message" => ""];
$backup_dir = __DIR__ . '/backups';
$games_file = __DIR__ . '/games.json';
$share_file = __DIR__ . '/share.json';
$uploads_dir = __DIR__ . '/uploads';

// Ensure backup directory exists
if (!is_dir($backup_dir)) {
    @mkdir($backup_dir, 0777, true);
    @chmod($backup_dir, 0777);
}

$action = $_GET['action'] ?? '';

if ($_SERVER['REQUEST_METHOD'] === 'GET' && $action === 'download') {
    $temp_zip = sys_get_temp_dir() . '/export_' . uniqid() . '.zip';
    $py_cmd = "python3 -c \"
import zipfile, os
with zipfile.ZipFile('" . $temp_zip . "', 'w', zipfile.ZIP_DEFLATED) as zf:
    if os.path.exists('" . $games_file . "'): zf.write('" . $games_file . "', 'games.json')
    if os.path.exists('" . $share_file . "'): zf.write('" . $share_file . "', 'share.json')
    if os.path.exists('" . $uploads_dir . "'):
        for root, dirs, files in os.walk('" . $uploads_dir . "'):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, '" . __DIR__ . "')
                zf.write(filepath, arcname)
\"";
    exec($py_cmd, $out, $ret);
    if ($ret === 0 && file_exists($temp_zip)) {
        header('Content-Type: application/zip');
        header('Content-Disposition: attachment; filename="launcher_backup_' . date('Ymd_His') . '.zip"');
        header('Content-Length: ' . filesize($temp_zip));
        readfile($temp_zip);
        unlink($temp_zip);
        exit;
    } else {
        http_response_code(500);
        echo "Failed to create zip";
        exit;
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'GET' && $action === 'list') {
    header('Content-Type: application/json; charset=utf-8');
    $files = array_merge(glob($backup_dir . '/games_*.json') ?: [], glob($backup_dir . '/backup_*.zip') ?: []);
    $backups = [];
    if ($files) {
        foreach ($files as $file) {
            $backups[] = [
                'filename' => basename($file),
                'size' => filesize($file),
                'time' => filemtime($file)
            ];
        }
        usort($backups, function($a, $b) {
            return $b['time'] - $a['time'];
        });
    }
    echo json_encode(["status" => "success", "backups" => $backups], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    header('Content-Type: application/json; charset=utf-8');
    $json_data = file_get_contents('php://input');
    $decoded = json_decode($json_data, true) ?: [];
    $post_action = $decoded['action'] ?? '';

    if ($post_action === 'create') {
        $backup_name = $backup_dir . '/backup_' . date('Ymd_His') . '_' . uniqid() . '.zip';
        $py_cmd = "python3 -c \"
import zipfile, os
with zipfile.ZipFile('" . $backup_name . "', 'w', zipfile.ZIP_DEFLATED) as zf:
    if os.path.exists('" . $games_file . "'): zf.write('" . $games_file . "', 'games.json')
    if os.path.exists('" . $share_file . "'): zf.write('" . $share_file . "', 'share.json')
    if os.path.exists('" . $uploads_dir . "'):
        for root, dirs, files in os.walk('" . $uploads_dir . "'):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, '" . __DIR__ . "')
                zf.write(filepath, arcname)
\"";
        exec($py_cmd, $out, $ret);
        
        if ($ret === 0 && file_exists($backup_name)) {
            @chmod($backup_name, 0666);
            $response["status"] = "success";
            $response["message"] = "バックアップを作成しました";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
            exit;
        }
        
        $response["message"] = "バックアップの作成に失敗しました";
        echo json_encode($response, JSON_UNESCAPED_UNICODE);
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
        
        if (file_exists($games_file)) {
            @copy($games_file, $backup_dir . '/games_pre_restore_' . date('Ymd_His') . '.json');
        }

        if (pathinfo($target_backup, PATHINFO_EXTENSION) === 'zip') {
            $dest = __DIR__;
            $py_cmd = "python3 -c \"
import zipfile
with zipfile.ZipFile('" . $target_backup . "', 'r') as zf:
    zf.extractall('" . $dest . "')
\"";
            exec($py_cmd, $out, $ret);
            
            if ($ret === 0) {
                @chmod($games_file, 0777);
                @chmod($share_file, 0777);
                $response["status"] = "success";
                $response["message"] = "ZIPバックアップから復元しました";
                echo json_encode($response, JSON_UNESCAPED_UNICODE);
            } else {
                $response["message"] = "ZIPファイルの展開に失敗しました";
                echo json_encode($response, JSON_UNESCAPED_UNICODE);
            }
        } else {
            $backup_content = @file_get_contents($target_backup);
            if ($backup_content !== false && @file_put_contents($games_file, $backup_content) !== false) {
                @chmod($games_file, 0777);
                $response["status"] = "success";
                $response["message"] = "JSONバックアップから復元しました";
                echo json_encode($response, JSON_UNESCAPED_UNICODE);
            } else {
                $response["message"] = "復元に失敗しました。パーミッションを確認してください。";
                echo json_encode($response, JSON_UNESCAPED_UNICODE);
            }
        }
        exit;
    }

    if ($post_action === 'delete') {
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

        if (unlink($target_backup)) {
            $response["status"] = "success";
            $response["message"] = "バックアップを削除しました";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
        } else {
            $response["message"] = "削除に失敗しました。パーミッションを確認してください。";
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
?>