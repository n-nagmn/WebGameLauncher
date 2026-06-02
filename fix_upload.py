import re

with open("manage_backups.php", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove the JSON auto-backup
old_backup = """        if (file_exists($games_file)) {
            @copy($games_file, $backup_dir . '/games_pre_restore_' . date('Ymd_His') . '.json');
        }"""
if old_backup in content:
    content = content.replace(old_backup, "")

# 2. Add upload_restore action
old_restore = """    if ($post_action === 'restore') {"""
new_upload = """    if ($post_action === 'upload_restore') {
        if (!isset($_FILES['file']) || $_FILES['file']['error'] !== UPLOAD_ERR_OK) {
            $response["message"] = "アップロードに失敗しました";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
            exit;
        }
        
        $tmp_name = $_FILES['file']['tmp_name'];
        $ext = pathinfo($_FILES['file']['name'], PATHINFO_EXTENSION);
        
        if ($ext === 'zip') {
            $dest = __DIR__;
            $py_cmd = "python3 -c \\"
import zipfile
with zipfile.ZipFile('". $tmp_name ."', 'r') as zf:
    zf.extractall('". $dest ."')
\\"";
            exec($py_cmd, $out, $ret);
            
            if ($ret === 0) {
                @chmod($games_file, 0777);
                @chmod($share_file, 0777);
                $response["status"] = "success";
                $response["message"] = "アップロードされたZIPから復元しました";
                echo json_encode($response, JSON_UNESCAPED_UNICODE);
            } else {
                $response["message"] = "ZIPファイルの展開に失敗しました";
                echo json_encode($response, JSON_UNESCAPED_UNICODE);
            }
        } else {
            // Assume json
            $backup_content = @file_get_contents($tmp_name);
            if ($backup_content !== false && @file_put_contents($games_file, $backup_content) !== false) {
                @chmod($games_file, 0777);
                $response["status"] = "success";
                $response["message"] = "アップロードされたJSONから復元しました";
                echo json_encode($response, JSON_UNESCAPED_UNICODE);
            } else {
                $response["message"] = "復元に失敗しました";
                echo json_encode($response, JSON_UNESCAPED_UNICODE);
            }
        }
        exit;
    }

    if ($post_action === 'restore') {"""

if old_restore in content:
    content = content.replace(old_restore, new_upload)

with open("manage_backups.php", "w", encoding="utf-8") as f:
    f.write(content)
