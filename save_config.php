<?php
// エラー出力を有効化
ini_set('display_errors', 1);
error_reporting(E_ALL);

$file_path = 'config.json';
$json_data = file_get_contents('php://input');

$response = [
    "status" => "error",
    "message" => ""
];

http_response_code(200);
header('Content-Type: application/json; charset=utf-8');

if (empty($json_data)) {
    $response["message"] = "データが空っぽです";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

$decoded = json_decode($json_data);
if ($decoded === null && strtolower($json_data) !== 'null') {
    $response["message"] = "JSONの形式が壊れています";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

$result = file_put_contents($file_path, $json_data, LOCK_EX);
if ($result !== false) {
    $response["status"] = "success";
    $response["message"] = "保存成功！";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
} else {
    $response["message"] = "config.json への書き込み権限がありません（パーミッションを666にしてください）";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
}
?>