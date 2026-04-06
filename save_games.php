<?php
// エラー出力を有効化
ini_set('display_errors', 1);
error_reporting(E_ALL);

$file_path = 'games.json';
$json_data = file_get_contents('php://input');

// 状況を可視化するためのデバッグ配列
$response = [
    "status" => "error",
    "message" => "",
    "debug" => [
        "received_data" => $json_data, // 実際にPHPに届いたデータ
        "json_error" => json_last_error_msg(), // JSONのパースエラー内容
        "method" => $_SERVER['REQUEST_METHOD'],
        "content_type" => $_SERVER['CONTENT_TYPE'] ?? 'unknown'
    ]
];

// エラー画面が出ないように一律200で返す（調査用）
http_response_code(200);
header('Content-Type: application/json; charset=utf-8');

// ① データが空っぽの場合
if (empty($json_data)) {
    $response["message"] = "データが空っぽです（NginxがPOSTデータをPHPに渡せていない可能性があります）";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

// ② JSONデータが壊れている場合
$decoded = json_decode($json_data);
if ($decoded === null && strtolower($json_data) !== 'null') {
    $response["message"] = "JSONの形式が壊れています";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

// ③ 保存処理
$result = file_put_contents($file_path, $json_data, LOCK_EX);
if ($result !== false) {
    $response["status"] = "success";
    $response["message"] = "保存成功！";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
} else {
    $response["message"] = "games.json への書き込み権限がありません（パーミッションを666にしてください）";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
}
?>