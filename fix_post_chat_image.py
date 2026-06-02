import re

with open("post_chat.php", "r", encoding="utf-8") as f:
    content = f.read()

# Replace json decoding block to handle multipart
old_decode = """$json_data = file_get_contents('php://input');

if (empty($json_data)) {
    $response["message"] = "データが空です";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

$decoded = json_decode($json_data, true);
if (!is_array($decoded)) {
    $decoded = [];
}"""

new_decode = """$is_multipart = isset($_SERVER['CONTENT_TYPE']) && strpos($_SERVER['CONTENT_TYPE'], 'multipart/form-data') !== false;

if ($is_multipart) {
    $decoded = $_POST;
} else {
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
}"""
content = content.replace(old_decode, new_decode)

# Replace validation block to handle images and avoid requiring message if image exists
old_validation = """if ($name === '' || $message === '') {
    $response["message"] = "名前とメッセージを入力してください";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}"""
new_validation = """if ($name === '' || $message === '') {
    if (!($is_multipart && isset($_FILES['image']) && $_FILES['image']['error'] === UPLOAD_ERR_OK)) {
        if ($message === '') {
            $response["message"] = "名前とメッセージを入力してください";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
            exit;
        }
    }
}"""
content = content.replace(old_validation, new_validation)

# Add image handling logic before new_message
old_new_message = """$new_message = [
    'id' => uniqid('msg_'),"""
new_new_message = """$imageUrl = null;
if ($is_multipart && isset($_FILES['image']) && $_FILES['image']['error'] === UPLOAD_ERR_OK) {
    $uploadDir = __DIR__ . "/uploads/";
    if (!is_dir($uploadDir)) {
        @mkdir($uploadDir, 0777, true);
        @chmod($uploadDir, 0777);
    }
    
    $check = getimagesize($_FILES['image']['tmp_name']);
    if($check !== false) {
        $ext = pathinfo($_FILES['image']['name'], PATHINFO_EXTENSION);
        $filename = uniqid('img_') . '.' . $ext;
        $targetPath = $uploadDir . $filename;
        if (@move_uploaded_file($_FILES['image']['tmp_name'], $targetPath)) {
            @chmod($targetPath, 0666);
            $imageUrl = "uploads/" . rawurlencode($filename);
        } else {
            $response["message"] = "画像の保存に失敗しました。";
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
            exit;
        }
    } else {
        $response["message"] = "画像ファイルではありません。";
        echo json_encode($response, JSON_UNESCAPED_UNICODE);
        exit;
    }
}

$new_message = [
    'id' => uniqid('msg_'),"""
content = content.replace(old_new_message, new_new_message)

# Add imageUrl to new_message
old_clientId = """    'clientId' => $clientId,
    'replyTo' => $replyTo
];"""
new_clientId = """    'clientId' => $clientId,
    'imageUrl' => $imageUrl,
    'replyTo' => $replyTo
];"""
content = content.replace(old_clientId, new_clientId)

with open("post_chat.php", "w", encoding="utf-8") as f:
    f.write(content)
