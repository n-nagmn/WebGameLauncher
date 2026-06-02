<?php
$f = 'W:/var/www/html/WebGameLauncher/index.html';
$c = file_get_contents($f);

// 1. CSS
$css_old = '.chat-message-text { word-break: break-word; line-height: 1.4; color: #eee; white-space: pre-wrap; }';
$css_new = $css_old . "\n        .aa-font {\n            font-family: 'MS PGothic', 'Mona', 'IPAMonaPGothic', 'Saitamaar', sans-serif !important;\n            font-size: 16px !important;\n            line-height: 1.1 !important;\n            white-space: pre !important;\n            overflow-x: auto;\n            padding-bottom: 4px;\n        }";
$c = str_replace($css_old, $css_new, $c);

// 2. Notification
$notif_old = '<div class="chat-notification-text">${escapeHtml(msg.message)}</div>';
$notif_new = '${(() => {
                    let msgText = msg.message;
                    if (msgText.startsWith(\'/aa\n\') || msgText.startsWith(\'/aa \')) {
                        return `<div class="chat-notification-text aa-font">${escapeHtml(msgText.substring(4))}</div>`;
                    }
                    return `<div class="chat-notification-text">${escapeHtml(msgText)}</div>`;
                })()}';
$c = str_replace($notif_old, $notif_new, $c);

// 3. RenderChat
$chat_old = '<div class="chat-message-text">${escapeHtml(msg.message)}</div>';
$chat_new = '${(() => {
                            let msgText = msg.message;
                            if (msgText.startsWith(\'/aa\n\') || msgText.startsWith(\'/aa \')) {
                                return `<div class="chat-message-text aa-font">${escapeHtml(msgText.substring(4))}</div>`;
                            }
                            return `<div class="chat-message-text">${escapeHtml(msgText)}</div>`;
                        })()}';
$c = str_replace($chat_old, $chat_new, $c);

file_put_contents($f, $c);
echo "AA feature added";
