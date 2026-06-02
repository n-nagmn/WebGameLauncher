import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

old_import = """        async function importData(event) {
            const file = event.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('action', 'upload_restore');
            formData.append('file', file);
            
            try {
                showToast('復元中...', 'info');
                const res = await fetch('./manage_backups.php', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (data.status === 'success') {
                    showToast('インポートが完了しました。ページを再読み込みします。', 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showToast(data.message || 'インポートに失敗しました', 'error');
                }
            } catch(e) {
                showToast('通信エラー', 'error');
                console.error(e);
            }
            event.target.value = '';
        }"""

new_import = """        async function importData(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            if (file.name.endsWith('.json')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    try {
                        const imported = JSON.parse(e.target.result);
                        if (Array.isArray(imported)) {
                            games = imported.map(g => ({ ...g, createdAt: g.createdAt || Date.now() }));
                        } else if (imported && typeof imported === 'object') {
                            if (Array.isArray(imported.games)) games = imported.games;
                            if (imported.serverConfig) {
                                serverConfig = { ...DEFAULT_SERVER_CONFIG, ...imported.serverConfig };
                                saveConfigToServer();
                            } else if (imported.config) {
                                serverConfig = { ...DEFAULT_SERVER_CONFIG, ...imported.config };
                                saveConfigToServer();
                            }
                            if (imported.localConfig) {
                                localConfig = { ...DEFAULT_LOCAL_CONFIG, ...imported.localConfig };
                                localStorage.setItem('launcher_local_config', JSON.stringify(localConfig));
                            }
                        } else {
                            throw new Error("Invalid format");
                        }
                        applyConfig();
                        renderGames();
                        saveGamesToServer();
                        closeSettings();
                        showToast('データのインポートが完了しました', 'success');
                    } catch (error) {
                        showToast('ファイルの読み込みに失敗しました', 'error');
                        console.error(error);
                    }
                    event.target.value = '';
                };
                reader.readAsText(file);
                return;
            }

            const formData = new FormData();
            formData.append('action', 'upload_restore');
            formData.append('file', file);
            
            try {
                showToast('ZIP復元中...', 'info');
                const res = await fetch('./manage_backups.php', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (data.status === 'success') {
                    showToast('インポートが完了しました。ページを再読み込みします。', 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showToast(data.message || 'インポートに失敗しました', 'error');
                }
            } catch(e) {
                showToast('通信エラー', 'error');
                console.error(e);
            }
            event.target.value = '';
        }"""

if old_import in content:
    content = content.replace(old_import, new_import)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
