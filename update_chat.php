<?php
$f = 'W:/var/www/html/WebGameLauncher/index.html';
$c = file_get_contents($f);

// 1 & 2. Change /aa to /a
$c = str_replace("startsWith('/aa')", "startsWith('/a')", $c);
$c = str_replace("replace(/^\/aa[\\s\\r\\n]*/i, '')", "replace(/^\/a[\\s\\r\\n]*/i, '')", $c);

// 3. Reset height on send
$c = str_replace("msgInput.value = '';", "msgInput.value = '';\n            msgInput.style.height = 'auto';", $c);

// 4. Auto-expand on input
$listener_old = <<<EOT
            document.getElementById('chat-message')?.addEventListener('keydown', e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendChatMessage();
                }
            });
EOT;
$listener_new = <<<EOT
            const chatMsgInput = document.getElementById('chat-message');
            if (chatMsgInput) {
                chatMsgInput.addEventListener('keydown', e => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendChatMessage();
                    }
                });
                chatMsgInput.addEventListener('input', function() {
                    this.style.height = 'auto';
                    const newHeight = Math.min(this.scrollHeight, 150);
                    this.style.height = newHeight + 'px';
                    this.style.overflowY = this.scrollHeight > 150 ? 'auto' : 'hidden';
                });
            }
EOT;
$c = str_replace($listener_old, $listener_new, $c);

// 5. CSS
$css_old = '.chat-input-area textarea { resize: none; }';
$css_new = '.chat-input-area textarea { resize: none; overflow-y: hidden; max-height: 150px; }';
$c = str_replace($css_old, $css_new, $c);

file_put_contents($f, $c);
echo "Changes applied successfully";
