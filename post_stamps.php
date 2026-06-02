<?php
header('Content-Type: application/json; charset=utf-8');

$stamps_file = __DIR__ . '/stamps.json';

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (file_exists($stamps_file)) {
        echo file_get_contents($stamps_file);
    } else {
        echo json_encode([]);
    }
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $json_data = file_get_contents('php://input');
    $decoded = json_decode($json_data, true);

    if ($decoded !== null) {
        $stamps = array_values($decoded);
        $encoded = json_encode($stamps, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
        
        $lock_file = $stamps_file . '.lock';
        $lock_fp = fopen($lock_file, 'w');
        if (flock($lock_fp, LOCK_EX)) {
            file_put_contents($stamps_file, $encoded);
            chmod($stamps_file, 0666);
            flock($lock_fp, LOCK_UN);
        }
        fclose($lock_fp);
        
        echo json_encode(['status' => 'success']);
    } else {
        http_response_code(400);
        echo json_encode(['status' => 'error', 'message' => 'Invalid JSON']);
    }
    exit;
}
