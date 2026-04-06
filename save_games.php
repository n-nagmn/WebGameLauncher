<?php
// エラー出力を有効化（うまく動かない時の確認用）
ini_set('display_errors', 1);
error_reporting(E_ALL);

// ファイルのパス
$file_path = 'games.json';

// ブラウザから送信されたJSONデータを受け取る
$json_data = file_get_contents('php://input');

// データが空でなく、正しいJSON形式か簡易チェック
if (!empty($json_data) && json_decode($json_data) !== null) {
    // games.json を上書き保存
    $result = file_put_contents($file_path, $json_data, LOCK_EX);
    
    if ($result !== false) {
        http_response_code(200);
        echo json_encode(["status" => "success"]);
    } else {
        http_response_code(500);
        echo json_encode(["status" => "error", "message" => "ファイルの書き込みに失敗しました。games.jsonのパーミッション（666等）を確認してください。"]);
    }
} else {
    http_response_code(400);
    echo json_encode(["status" => "error", "message" => "不正なデータです"]);
}
?>