<?php
/**
 * Web Game Launcher Pro - Chat/Bulletin Board Post Endpoint
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
$file_path = __DIR__ . '/chat.json';
$max_messages = 100;

$json_data = file_get_contents('php://input');

if (empty($json_data)) {
    $response["message"] = "データが空です";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

$decoded = json_decode($json_data, true);
if (!is_array($decoded)) {
    $decoded = [];
}

$action = $decoded['action'] ?? 'post';

if ($action === 'delete') {
    $timestamp_to_delete = isset($decoded['timestamp']) ? intval($decoded['timestamp']) : 0;
    if ($timestamp_to_delete > 0) {
        $chat_data = [];
        if (file_exists($file_path)) {
            $raw = file_get_contents($file_path);
            $chat_data = json_decode($raw, true) ?: [];
        }
        // Filter out the message
        $chat_data = array_values(array_filter($chat_data, function($msg) use ($timestamp_to_delete) {
            return (!isset($msg['timestamp']) || $msg['timestamp'] !== $timestamp_to_delete);
        }));
        
        @file_put_contents($file_path, json_encode($chat_data, JSON_UNESCAPED_UNICODE));
        echo json_encode(["status" => "success"]);
    } else {
        http_response_code(400);
        echo json_encode(["status" => "error", "message" => "Invalid timestamp"]);
    }
    exit;
}

// Default post action
$name = isset($decoded['name']) ? mb_substr(trim($decoded['name']), 0, 30, 'UTF-8') : '名無しさん';
$message = isset($decoded['message']) ? trim($decoded['message']) : '';
$gameId = !empty($decoded['gameId']) ? trim($decoded['gameId']) : null;
$timestamp = time() * 1000;

if ($name === '' || $message === '') {
    $response["message"] = "名前とメッセージを入力してください";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

$line_count = substr_count($message, "\n") + 1;
$is_aa = stripos(trim($message), '/a') === 0;

if ($is_aa) {
    $lines = explode("\n", $message);
    foreach ($lines as $line) {
        if (mb_strlen(trim($line, "\r\n"), 'UTF-8') > 1000) {
            $response["message"] = "アスキーアートの1行の最大文字数は1000文字までです。";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
            exit;
        }
    }
} else if (mb_strlen($message, 'UTF-8') > 300) {
    $response["message"] = "通常チャットの最大文字数は300文字です。";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

if ($line_count >= 5 && !$is_aa) {
    $response["message"] = "複数行のAA（アスキーアート）を送信する場合は、メッセージの先頭に /a を付けてください。";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

$clientId = isset($decoded['clientId']) ? trim($decoded['clientId']) : null;

$new_message = [
    'id' => uniqid('msg_'),
    'name' => $name,
    'message' => $message,
    'gameId' => $gameId,
    'timestamp' => $timestamp,
    'clientId' => $clientId
];

$existing_messages = [];
$result = false;

$lock_file = __DIR__ . '/chat.lock';
$fp_lock = @fopen($lock_file, 'w');

if ($fp_lock && flock($fp_lock, LOCK_EX)) {
    if (file_exists($file_path)) {
        $existing_raw = file_get_contents($file_path);
        $existing_messages = json_decode($existing_raw, true) ?: [];
    }
    
    array_push($existing_messages, $new_message);
    
    // Keep only the last $max_messages
    if (count($existing_messages) > $max_messages) {
        $existing_messages = array_slice($existing_messages, -$max_messages);
    }
    
    $json_output = json_encode($existing_messages, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    if ($json_output !== false) {
        @file_put_contents($file_path, $json_output);
        $result = true;
    }
    flock($fp_lock, LOCK_UN);
}
if ($fp_lock) {
    fclose($fp_lock);
}

if ($result !== false) {
    @chmod($file_path, 0666);
    $response["status"] = "success";
    $response["message"] = "投稿しました";
    $response["data"] = $new_message;
    http_response_code(200);
} else {
    $response["message"] = "chat.json への書き込みに失敗しました。";
    http_response_code(500);
}

echo json_encode($response, JSON_UNESCAPED_UNICODE);

