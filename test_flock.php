<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
$file_path = __DIR__ . '/chat.json';
$fp = fopen($file_path, 'c+');
if (!$fp) {
    echo "fopen failed\n";
    exit;
}
if (!flock($fp, LOCK_EX)) {
    echo "flock failed\n";
    exit;
}
echo "Success!\n";
flock($fp, LOCK_UN);
fclose($fp);
