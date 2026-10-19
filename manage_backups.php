<?php
/**
 * Web Game Launcher Pro - Backup Management
 *
 * All ZIP handling is done with PHP's ZipArchive extension (no external
 * processes). Uploads are strictly validated:
 *  - non-zip restore: content must decode to a JSON array before it is
 *    re-encoded and written to games.json
 *  - zip restore: members are whitelisted (exact json filenames at the
 *    archive root, and uploads/ files matching stamp_/img_ basenames);
 *    paths containing '..' or absolute paths are rejected.
 */

header('Content-Type: application/json; charset=utf-8');

$backup_dir = __DIR__ . '/backups';
if (!is_dir($backup_dir)) {
    @mkdir($backup_dir, 0777, true);
    @chmod($backup_dir, 0777);
}

// Strict pattern for server-side backup filenames (created via the create action)
$backup_filename_regex = '/^backup_\d{8}_\d{6}_[0-9a-f]+\.zip$/';

$games_file = __DIR__ . '/games.json';
$share_file = __DIR__ . '/share.json';
$chat_file = __DIR__ . '/chat.json';
$stamps_file = __DIR__ . '/stamps.json';
$config_file = __DIR__ . '/config.json';
$uploads_dir = __DIR__ . '/uploads';

// Files that may be stored at the archive root
$root_json_files = ['games.json', 'share.json', 'chat.json', 'stamps.json', 'config.json'];

// Regex for allowed upload file basenames (inside uploads/ in the archive)
$upload_file_regex = '/^(stamp_|img_)[A-Za-z0-9_-]+\.(png|jpe?g|gif|webp)$/i';

/**
 * Create a backup zip of games.json / share.json / chat.json / stamps.json / uploads/.
 */
function createBackupZip($backup_name, $files, $uploads_dir) {
    if (!class_exists('ZipArchive')) {
        return false;
    }
    $zip = new ZipArchive();
    if ($zip->open($backup_name, ZipArchive::CREATE | ZipArchive::OVERWRITE) !== true) {
        return false;
    }
    foreach ($files as $file) {
        if (file_exists($file)) {
            $zip->addFile($file, basename($file));
        }
    }
    if (is_dir($uploads_dir)) {
        $it = new RecursiveIteratorIterator(
            new RecursiveDirectoryIterator($uploads_dir, FilesystemIterator::SKIP_DOTS),
            RecursiveIteratorIterator::LEAVES_ONLY
        );
        foreach ($it as $f) {
            if ($f->isFile()) {
                $rel = ltrim(str_replace('\\', '/', $f->getPathname()), '/');
                $base = __DIR__ . DIRECTORY_SEPARATOR;
                if (strpos($rel, $base) === 0) {
                    $rel = substr($rel, strlen($base));
                }
                $zip->addFile($f->getPathname(), $rel);
            }
        }
    }
    $zip->close();
    return file_exists($backup_name);
}

/**
 * Extract a backup zip into $dest. Returns [ok, error_message].
 * Members are strictly whitelisted; anything else is rejected.
 */
function extractBackupZip($zip_path, $dest, $root_json_files, $lock_file = null) {
    if (!class_exists('ZipArchive')) {
        return [false, 'ZipArchive拡張機能が利用できません'];
    }

    // Acquire an exclusive lock on the shared restore lock file (same pattern
    // as save_games.php) so a zip restore never races with a game save.
    $fp_lock = null;
    if ($lock_file !== null) {
        $fp_lock = @fopen($lock_file, 'w');
        if ($fp_lock !== false && !flock($fp_lock, LOCK_EX)) {
            fclose($fp_lock);
            return [false, 'サーバーが混雑しています。もう一度お試しください。'];
        }
    }

    $zip = new ZipArchive();
    if ($zip->open($zip_path) !== true) {
        if ($fp_lock !== null) { flock($fp_lock, LOCK_UN); fclose($fp_lock); }
        return [false, 'ZIPファイルを開けません'];
    }

    // Validate every member before extracting anything
    $members = [];
    for ($i = 0; $i < $zip->numFiles; $i++) {
        $name = $zip->getNameIndex($i);
        // Normalize separators; reject absolute paths and ".." traversal
        $normalized = str_replace('\\', '/', (string)$name);
        if ($normalized === '' || $normalized === '.') continue;
        if ($normalized[0] === '/' || preg_match('/^[a-z]:/i', $normalized)) {
            $zip->close();
            if ($fp_lock !== null) { flock($fp_lock, LOCK_UN); fclose($fp_lock); }
            return [false, '不正なファイルパスが含まれています: ' . $name];
        }
        $parts = explode('/', $normalized);
        if (in_array('..', $parts, true)) {
            $zip->close();
            if ($fp_lock !== null) { flock($fp_lock, LOCK_UN); fclose($fp_lock); }
            return [false, '不正なファイルパスが含まれています: ' . $name];
        }

        $base = array_pop($parts);
        if ($base === '') continue;

        $target_path = null;
        if ($parts === [] && in_array($base, $root_json_files, true)) {
            // JSON files must sit at the archive root
            $target_path = $dest . '/' . $base;
        } elseif (count($parts) === 1 && $parts[0] === 'uploads' && preg_match($upload_file_regex, $base)) {
            // Upload files must be inside uploads/ with a whitelisted basename
            $target_path = $dest . '/uploads/' . $base;
        }
        if ($target_path === null) {
            $zip->close();
            if ($fp_lock !== null) { flock($fp_lock, LOCK_UN); fclose($fp_lock); }
            return [false, '許可されていないファイルが含まれています: ' . $name];
        }
        $members[] = ['name' => $name, 'target' => $target_path];
    }

    // Extract (all members already validated).
    // Each member is written atomically: temp file + rename, so a failed
    // restore never leaves a half-written JSON file behind.
    foreach ($members as $m) {
        $dir = dirname($m['target']);
        if (!is_dir($dir)) {
            @mkdir($dir, 0777, true);
            @chmod($dir, 0777);
        }
        $src = $zip->getFromName($m['name']);
        if ($src === false) {
            $zip->close();
            if ($fp_lock !== null) { flock($fp_lock, LOCK_UN); fclose($fp_lock); }
            return [false, 'ZIPメンバーの読み込みに失敗しました: ' . $m['name']];
        }
        $tmp = $m['target'] . '.tmp';
        if (@file_put_contents($tmp, $src, LOCK_EX) === false) {
            $zip->close();
            if ($fp_lock !== null) { flock($fp_lock, LOCK_UN); fclose($fp_lock); }
            return [false, 'ファイルの書き込みに失敗しました: ' . $m['target']];
        }
        if (!@rename($tmp, $m['target'])) {
            @unlink($tmp);
            $zip->close();
            if ($fp_lock !== null) { flock($fp_lock, LOCK_UN); fclose($fp_lock); }
            return [false, 'ファイルの書き込みに失敗しました: ' . $m['target']];
        }
        @chmod($m['target'], 0666);
    }
    $zip->close();
    if ($fp_lock !== null) { flock($fp_lock, LOCK_UN); fclose($fp_lock); }
    return [true, ''];
}

/**
 * Validate and write a non-zip backup to games.json.
 * The content must be valid JSON that decodes to an array of objects.
 */
function restoreJsonBackup($content, $games_file) {
    if ($content === false || $content === '') {
        return false;
    }
    $decoded = json_decode($content, true);
    if (!is_array($decoded)) {
        return false;
    }
    // Re-encode the validated data (strips any malformed trailing content)
    $json_output = json_encode(array_values($decoded), JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    if ($json_output === false) {
        return false;
    }
    $tmp = $games_file . '.tmp';
    if (@file_put_contents($tmp, $json_output, LOCK_EX) === false) {
        return false;
    }
    if (!@rename($tmp, $games_file)) {
        @unlink($tmp);
        return false;
    }
    @chmod($games_file, 0666);
    return true;
}

$json_data = file_get_contents('php://input');
$decoded = json_decode($json_data, true) ?: [];
$action = $_GET['action'] ?? $decoded['action'] ?? $_POST['action'] ?? '';

if ($_SERVER['REQUEST_METHOD'] === 'GET' && $action === 'download') {
    $filename = $_GET['filename'] ?? '';
    if (empty($filename) || strpos($filename, '/') !== false || strpos($filename, '\\') !== false) {
        http_response_code(400);
        echo "Invalid filename";
        exit;
    }
    $target_file = $backup_dir . '/' . $filename;
    if (!file_exists($target_file)) {
        http_response_code(404);
        echo "File not found";
        exit;
    }
    header('Content-Type: application/zip');
    header('Content-Disposition: attachment; filename="' . basename($target_file) . '"');
    header('Content-Length: ' . filesize($target_file));
    readfile($target_file);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'GET' && $action === 'export') {
    $backup_name = $backup_dir . '/export_' . date('Ymd_His') . '_' . uniqid() . '.zip';
    $files = [$games_file, $share_file, $chat_file, $stamps_file, $config_file];
    if (createBackupZip($backup_name, $files, $uploads_dir)) {
        header('Content-Type: application/zip');
        header('Content-Disposition: attachment; filename="backup.zip"');
        header('Content-Length: ' . filesize($backup_name));
        readfile($backup_name);
        unlink($backup_name);
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

    if ($action === 'create') {
        $backup_name = $backup_dir . '/backup_' . date('Ymd_His') . '_' . uniqid() . '.zip';
        $files = [$games_file, $share_file, $chat_file, $stamps_file, $config_file];
        if (createBackupZip($backup_name, $files, $uploads_dir)) {
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

    if ($action === 'upload_restore') {
        if (!isset($_FILES['file']) || $_FILES['file']['error'] !== UPLOAD_ERR_OK) {
            $response["message"] = "アップロードに失敗しました";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
            exit;
        }

        $tmp_name = $_FILES['file']['tmp_name'];
        $ext = strtolower(pathinfo($_FILES['file']['name'], PATHINFO_EXTENSION));
        $lock_file = __DIR__ . '/games.lock';

        if ($ext === 'zip') {
            $dest = __DIR__;
            list($ok, $err) = extractBackupZip($tmp_name, $dest, $root_json_files, $lock_file);

            if ($ok) {
                @chmod($games_file, 0666);
                @chmod($share_file, 0666);
                @chmod($chat_file, 0666);
                @chmod($stamps_file, 0666);
                @chmod($config_file, 0666);
                $response["status"] = "success";
                $response["message"] = "アップロードされたZIPから復元しました";
                echo json_encode($response, JSON_UNESCAPED_UNICODE);
            } else {
                $response["message"] = "ZIPファイルの展開に失敗しました: " . $err;
                echo json_encode($response, JSON_UNESCAPED_UNICODE);
            }
        } else {
            $backup_content = @file_get_contents($tmp_name);
            if (restoreJsonBackup($backup_content, $games_file)) {
                @chmod($games_file, 0666);
                $response["status"] = "success";
                $response["message"] = "アップロードされたJSONから復元しました";
                echo json_encode($response, JSON_UNESCAPED_UNICODE);
            } else {
                $response["message"] = "復元に失敗しました。有効なJSONファイル（ゲームデータ配列）をアップロードしてください。";
                echo json_encode($response, JSON_UNESCAPED_UNICODE);
            }
        }
        exit;
    }

    if ($action === 'restore') {
        $filename = $decoded['filename'] ?? '';
        if (empty($filename) || strpos($filename, '/') !== false || strpos($filename, '\\') !== false) {
            $response["message"] = "不正なファイル名です";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
            exit;
        }
        // Strict filename validation: only server-side backup zips (backup_YYYYMMDD_HHMMSS_<hex>.zip)
        if (!preg_match($backup_filename_regex, $filename)) {
            $response["message"] = "ファイル名が不正です（backup_YYYYMMDD_HHMMSS_<hex>.zip の形式のみ許可）";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
            exit;
        }
        $target_backup = $backup_dir . '/' . $filename;
        if (!file_exists($target_backup)) {
            $response["message"] = "バックアップファイルが見つかりません";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
            exit;
        }

        // Zip restore (the strict regex above guarantees this is a .zip file)
        $lock_file = __DIR__ . '/games.lock';
        list($ok, $err) = extractBackupZip($target_backup, __DIR__, $root_json_files, $lock_file);

        if ($ok) {
            @chmod($games_file, 0666);
            @chmod($share_file, 0666);
            @chmod($chat_file, 0666);
            @chmod($stamps_file, 0666);
            @chmod($config_file, 0666);
            $response["status"] = "success";
            $response["message"] = "ZIPバックアップから復元しました";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
        } else {
            $response["message"] = "ZIPファイルの展開に失敗しました: " . $err;
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
        }
        exit;
    }

    if ($action === 'delete') {
        $filename = $decoded['filename'] ?? '';
        if (empty($filename) || strpos($filename, '/') !== false || strpos($filename, '\\') !== false) {
            $response["message"] = "不正なファイル名です";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
            exit;
        }
        // Strict filename validation: only server-side backup zips may be deleted
        if (!preg_match($backup_filename_regex, $filename)) {
            $response["message"] = "ファイル名が不正です（backup_YYYYMMDD_HHMMSS_<hex>.zip の形式のみ許可）";
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
