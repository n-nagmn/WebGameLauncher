import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace hardcoded reaction picker HTML
old_picker = """    <!-- Reaction Picker -->
    <div id="reaction-picker" style="display: none; position: fixed; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 20px; padding: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.4); z-index: 1000; display: none; /* flex when active */ gap: 4px;">
        <button class="picker-emoji" onclick="App.reactMessage('👍')" style="background:none;border:none;cursor:pointer;font-size:18px;padding:4px;transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'">👍</button>
        <button class="picker-emoji" onclick="App.reactMessage('❤️')" style="background:none;border:none;cursor:pointer;font-size:18px;padding:4px;transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'">❤️</button>
        <button class="picker-emoji" onclick="App.reactMessage('😂')" style="background:none;border:none;cursor:pointer;font-size:18px;padding:4px;transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'">😂</button>
        <button class="picker-emoji" onclick="App.reactMessage('🎉')" style="background:none;border:none;cursor:pointer;font-size:18px;padding:4px;transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'">🎉</button>
        <button class="picker-emoji" onclick="App.reactMessage('草')" style="background:none;border:none;cursor:pointer;font-size:18px;padding:4px;transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'">草</button>
    </div>"""

# Ensure we remove the old one robustly using regex since encoding might have messed up emojis
content = re.sub(r'<!-- Reaction Picker -->\s*<div id="reaction-picker".*?</div>', '<!-- Reaction Picker -->\n    <div id="reaction-picker" style="display: none; position: fixed; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 20px; padding: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.4); z-index: 1000; gap: 4px; flex-wrap: wrap; max-width: 200px;"></div>', content, flags=re.DOTALL)


# 2. Add Settings UI for Stamps
old_settings_html = """                <h3>その他</h3>
                <div class="setting-item">"""

new_settings_html = """                <h3>スタンプ（全体共有）</h3>
                <div class="setting-item" style="flex-direction: column; align-items: flex-start; gap: 8px;">
                    <div style="display: flex; gap: 8px; width: 100%;">
                        <input type="text" id="new-stamp-input" placeholder="新しいスタンプ (例: ✨, 乙, 草)" style="flex-grow: 1; padding: 8px; border-radius: 4px; background: rgba(0,0,0,0.2); color: var(--text-color); border: 1px solid var(--border-color);">
                        <button onclick="App.addCustomStamp()" class="modal-btn" style="background: var(--focus-color); color: #000;">追加</button>
                    </div>
                    <div id="custom-stamps-list" style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;"></div>
                </div>
                <h3>その他</h3>
                <div class="setting-item">"""

content = content.replace(old_settings_html, new_settings_html)


# 3. Add JS for stamps
js_to_add = """
        let customStamps = [];
        const defaultStamps = ['👍', '❤️', '😂', '🎉', '草'];

        async function fetchStamps() {
            try {
                const res = await fetch('post_stamps.php');
                if (res.ok) {
                    customStamps = await res.json();
                    renderReactionPicker();
                    renderSettingsStamps();
                }
            } catch(e) { console.error(e); }
        }

        function renderReactionPicker() {
            const picker = document.getElementById('reaction-picker');
            const allStamps = [...defaultStamps, ...customStamps];
            picker.innerHTML = allStamps.map(s => `
                <button class="picker-emoji" onclick="App.reactMessage('${escapeHtml(s)}')" style="background:none;border:none;cursor:pointer;font-size:18px;padding:4px;transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'">${escapeHtml(s)}</button>
            `).join('');
        }

        function renderSettingsStamps() {
            const list = document.getElementById('custom-stamps-list');
            if(!list) return;
            list.innerHTML = customStamps.map((s, index) => `
                <div style="display: flex; align-items: center; background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 4px; gap: 4px;">
                    <span>${escapeHtml(s)}</span>
                    <button onclick="App.deleteCustomStamp(${index})" style="background: none; border: none; color: #ff5252; cursor: pointer; padding: 0 4px;">&times;</button>
                </div>
            `).join('');
        }

        async function addCustomStamp() {
            const input = document.getElementById('new-stamp-input');
            const val = input.value.trim();
            if(!val) return;
            if(defaultStamps.includes(val) || customStamps.includes(val)) {
                showToast('既に存在するスタンプです', 'error');
                return;
            }
            customStamps.push(val);
            input.value = '';
            await saveCustomStamps();
        }

        async function deleteCustomStamp(index) {
            customStamps.splice(index, 1);
            await saveCustomStamps();
        }

        async function saveCustomStamps() {
            try {
                const res = await fetch('post_stamps.php', {
                    method: 'POST',
                    body: JSON.stringify(customStamps)
                });
                if(res.ok) {
                    renderReactionPicker();
                    renderSettingsStamps();
                    showToast('スタンプを保存しました');
                }
            } catch(e) { console.error(e); }
        }
"""

content = content.replace("let gameHistory = [];", "let gameHistory = [];\n" + js_to_add)

# 4. Add fetchStamps to initialize
content = content.replace("fetchGames();", "fetchGames();\n            fetchStamps();")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
