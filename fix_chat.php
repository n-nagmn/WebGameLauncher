<?php
$f = 'W:/var/www/html/WebGameLauncher/index.html';
$c = file_get_contents($f);

$pattern = '/let name = nameInput\.value\.trim\(\).*?localStorage\.setItem\(\'chat_name\', name\);/s';
$replacement = "let inputName = nameInput.value.trim();
            const message = msgInput.value.trim();
            const gameId = gameSelect.value || null;
            
            if (!message) return;
            
            if (inputName && inputName !== '名無し') {
                localStorage.setItem('chat_name', inputName);
            } else {
                localStorage.removeItem('chat_name');
            }
            let name = inputName || '名無し';";

$c = preg_replace($pattern, $replacement, $c);
file_put_contents($f, $c);
echo "Replaced successfully";
