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
if ($decoded === null) {
    $response["message"] = "JSONの形式が不正です";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

if (!isset($decoded['name']) || !isset($decoded['message'])) {
    $response["message"] = "名前とメッセージは必須です";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

$name = htmlspecialchars(mb_substr(trim($decoded['name']), 0, 30), ENT_QUOTES, 'UTF-8');
$message = htmlspecialchars(mb_substr(trim($decoded['message']), 0, 200), ENT_QUOTES, 'UTF-8');
$gameId = isset($decoded['gameId']) ? intval($decoded['gameId']) : null;
$timestamp = time() * 1000;

if ($name === '' || $message === '') {
    $response["message"] = "名前とメッセージを入力してください";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

$new_message = [
    'id' => uniqid('msg_'),
    'name' => $name,
    'message' => $message,
    'gameId' => $gameId,
    'timestamp' => $timestamp
];

$existing_messages = [];
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
$result = file_put_contents($file_path, $json_output, LOCK_EX);

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
