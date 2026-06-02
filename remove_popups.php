<?php
$f = 'W:/var/www/html/WebGameLauncher/index.html';
$content = file_get_contents($f);
$content = preg_replace('/if \(confirm\([^)]+\)\) \{\s*(launchGame\(game\);)\s*\}/s', '$1', $content);
$content = preg_replace('/if \(confirm\([^)]+\)\) \{\s*(games = games\.filter\(g => g\.id !== id\);\s*renderGames\(\);\s*closeGameModal\(\);\s*saveGamesToServer\(\);\s*showToast\([^)]+\);\s*)\}/s', '$1', $content);
$content = preg_replace('/if \(!confirm\([^)]+\)\) \{\s*return;\s*\}\s*let isUpdated/s', 'let isUpdated', $content);
$content = preg_replace('/if \(!confirm\("[^"]+"\)\) return;/s', '', $content);
$content = preg_replace('/if \(!confirm\(`[^`]+`\)\) \{\s*return;\s*\}/s', '', $content);
file_put_contents($f, $content);
echo "Popups removed\n";
