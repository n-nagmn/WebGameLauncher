import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add Reaction Picker to body
picker_html = """
    <!-- Reaction Picker -->
    <div id="reaction-picker" style="display: none; position: fixed; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 20px; padding: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.4); z-index: 1000; display: flex; gap: 4px;">
        <button class="picker-emoji" onclick="App.reactMessage('👍')" style="background:none;border:none;cursor:pointer;font-size:18px;padding:4px;transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'">👍</button>
        <button class="picker-emoji" onclick="App.reactMessage('❤️')" style="background:none;border:none;cursor:pointer;font-size:18px;padding:4px;transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'">❤️</button>
        <button class="picker-emoji" onclick="App.reactMessage('😂')" style="background:none;border:none;cursor:pointer;font-size:18px;padding:4px;transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'">😂</button>
        <button class="picker-emoji" onclick="App.reactMessage('😢')" style="background:none;border:none;cursor:pointer;font-size:18px;padding:4px;transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'">😢</button>
        <button class="picker-emoji" onclick="App.reactMessage('🎉')" style="background:none;border:none;cursor:pointer;font-size:18px;padding:4px;transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'">🎉</button>
    </div>
</body>"""
if "<!-- Reaction Picker -->" not in content:
    content = content.replace("</body>", picker_html.replace('display: flex;', 'display: none; /* flex when active */'))

# 2. Add App functions for reactions
funcs = """        let currentReactionMsgTs = 0;
        let currentReactionIsShare = false;

        function toggleReactionPicker(timestamp, isShare, btnElem, event) {
            event.stopPropagation();
            const picker = document.getElementById('reaction-picker');
            if (picker.style.display === 'flex' && currentReactionMsgTs === timestamp && currentReactionIsShare === isShare) {
                picker.style.display = 'none';
                return;
            }
            currentReactionMsgTs = timestamp;
            currentReactionIsShare = isShare;
            picker.style.display = 'flex';
            const rect = btnElem.getBoundingClientRect();
            picker.style.top = (rect.bottom + 5) + 'px';
            picker.style.left = Math.min(rect.left, window.innerWidth - 180) + 'px';
        }

        async function reactMessage(emoji, explicitTs = null, explicitIsShare = null) {
            const timestamp = explicitTs !== null ? explicitTs : currentReactionMsgTs;
            const isShare = explicitIsShare !== null ? explicitIsShare : currentReactionIsShare;
            
            document.getElementById('reaction-picker').style.display = 'none';
            if (!timestamp) return;

            try {
                const endpoint = isShare ? './post_share.php' : './post_chat.php';
                const res = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'react', timestamp: timestamp, emoji: emoji, clientId: myClientId })
                });
                if (res.ok) {
                    if (isShare) fetchShare(); else fetchChat();
                } else {
                    showToast('リアクションに失敗しました', 'error');
                }
            } catch(e) {
                console.error(e);
            }
        }

        // Close picker when clicking outside
        window.addEventListener('click', e => {
            const picker = document.getElementById('reaction-picker');
            if (picker && picker.style.display !== 'none' && !e.target.closest('#reaction-picker') && !e.target.closest('.add-reaction-btn')) {
                picker.style.display = 'none';
            }
        });

        async function deleteChatMessage(timestamp) {"""

old_funcs = """        async function deleteChatMessage(timestamp) {"""
if "toggleReactionPicker(" not in content:
    content = content.replace(old_funcs, funcs)

# 3. Modify renderChat
old_render_chat = """                        ${msg.imageUrl ? `<div style="margin-top: 8px;"><a href="${escapeHtml(msg.imageUrl)}" target="_blank"><img src="${escapeHtml(msg.imageUrl)}" style="max-width: 50%; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);" alt="Image"></a></div>` : ''}
                    </div>
                `;
            });
            container.innerHTML = html;"""
new_render_chat = """                        ${msg.imageUrl ? `<div style="margin-top: 8px;"><a href="${escapeHtml(msg.imageUrl)}" target="_blank"><img src="${escapeHtml(msg.imageUrl)}" style="max-width: 50%; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);" alt="Image"></a></div>` : ''}
                        
                        <div style="display: flex; gap: 4px; margin-top: 6px; flex-wrap: wrap;">
                            ${Object.keys(msg.reactions || {}).map(emoji => {
                                const count = msg.reactions[emoji].length;
                                const reacted = msg.reactions[emoji].includes(myClientId);
                                if (count === 0) return '';
                                return `<button style="background: ${reacted ? 'rgba(0,123,255,0.2)' : 'rgba(128,128,128,0.1)'}; border: 1px solid ${reacted ? '#007bff' : 'rgba(128,128,128,0.3)'}; border-radius: 12px; padding: 2px 6px; font-size: 11px; color: inherit; cursor: pointer; display: flex; align-items: center; gap: 4px;" onclick="App.reactMessage('${emoji}', ${msg.timestamp}, false)">${emoji} <span>${count}</span></button>`;
                            }).join('')}
                            <button class="add-reaction-btn" style="background: rgba(128,128,128,0.1); border: 1px solid rgba(128,128,128,0.3); border-radius: 12px; padding: 2px 6px; font-size: 11px; color: inherit; cursor: pointer; display: flex; align-items: center; justify-content: center; width: 24px;" onclick="App.toggleReactionPicker(${msg.timestamp}, false, this, event)">+</button>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;"""
content = content.replace(old_render_chat, new_render_chat)

# 4. Modify renderShare
old_render_share = """                        ${msg.imageUrl ? `<div style="margin-top: 8px;"><img src="${escapeHtml(msg.imageUrl)}" onclick="App.openImageModal('${escapeHtml(msg.imageUrl)}')" style="max-width: 50%; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); cursor: zoom-in;" alt="Image"></div>` : ''}
                    </div>
                `;
            });
            container.innerHTML = html;"""
new_render_share = """                        ${msg.imageUrl ? `<div style="margin-top: 8px;"><img src="${escapeHtml(msg.imageUrl)}" onclick="App.openImageModal('${escapeHtml(msg.imageUrl)}')" style="max-width: 50%; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); cursor: zoom-in;" alt="Image"></div>` : ''}
                        
                        <div style="display: flex; gap: 4px; margin-top: 6px; flex-wrap: wrap;">
                            ${Object.keys(msg.reactions || {}).map(emoji => {
                                const count = msg.reactions[emoji].length;
                                const reacted = msg.reactions[emoji].includes(myClientId);
                                if (count === 0) return '';
                                return `<button style="background: ${reacted ? 'var(--focus-color)' : 'rgba(128,128,128,0.1)'}; filter: ${reacted ? 'brightness(0.6)' : 'none'}; border: 1px solid ${reacted ? 'var(--focus-color)' : 'rgba(128,128,128,0.3)'}; border-radius: 12px; padding: 2px 6px; font-size: 11px; color: inherit; cursor: pointer; display: flex; align-items: center; gap: 4px;" onclick="App.reactMessage('${emoji}', ${msg.timestamp}, true)">${emoji} <span>${count}</span></button>`;
                            }).join('')}
                            <button class="add-reaction-btn" style="background: rgba(128,128,128,0.1); border: 1px solid rgba(128,128,128,0.3); border-radius: 12px; padding: 2px 6px; font-size: 11px; color: inherit; cursor: pointer; display: flex; align-items: center; justify-content: center; width: 24px;" onclick="App.toggleReactionPicker(${msg.timestamp}, true, this, event)">+</button>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;"""
content = content.replace(old_render_share, new_render_share)

# 5. Add to App exports
old_export = """            openImageModal, closeImageModal
        };"""
new_export = """            openImageModal, closeImageModal,
            toggleReactionPicker, reactMessage
        };"""
if "toggleReactionPicker, reactMessage" not in content:
    content = content.replace(old_export, new_export)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
