import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update exportData
old_export = """        function exportData() {
            const exportObject = { games, serverConfig, localConfig, exportedAt: new Date().toISOString() };
            const blob = new Blob([JSON.stringify(exportObject, null, 2)], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `launcher_backup_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            showToast('データをエクスポートしました', 'success');
        }"""

new_export = """        function exportData() {
            const a = document.createElement("a");
            a.href = './manage_backups.php?action=download';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            showToast('ZIPエクスポートを開始しました', 'success');
        }"""

if old_export in content:
    content = content.replace(old_export, new_export)

# 2. Remove DL button and downloadServerBackup function
old_ui = """                    <div style="display: flex; gap: 10px;">
                        <button class="btn-primary" style="flex:1; padding: 10px;" onclick="App.downloadServerBackup()">DL</button>
                        <button class="btn-danger" style="flex:2; padding: 10px;" onclick="App.restoreServerBackup()">選択したバックアップから復元</button>
                        <button class="btn-danger" style="flex:1; padding: 10px;" onclick="App.deleteServerBackup()">削除</button>
                    </div>"""
new_ui = """                    <div style="display: flex; gap: 10px;">
                        <button class="btn-danger" style="flex:2; padding: 10px;" onclick="App.restoreServerBackup()">選択したバックアップから復元</button>
                        <button class="btn-danger" style="flex:1; padding: 10px;" onclick="App.deleteServerBackup()">削除</button>
                    </div>"""

if old_ui in content:
    content = content.replace(old_ui, new_ui)

old_dl = """        function downloadServerBackup() {
            const select = document.getElementById('server-backup-select');
            const filenames = Array.from(select.selectedOptions).map(opt => opt.value).filter(v => v !== '');
            if (filenames.length !== 1) {
                showToast('ダウンロードするバックアップを「1つだけ」選択してください', 'warning');
                return;
            }
            const filename = filenames[0];
            const a = document.createElement('a');
            a.href = `./backups/${filename}`;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }"""

if old_dl in content:
    content = content.replace(old_dl, "")

old_export_fn = """loadServerBackups, createServerBackup, restoreServerBackup, deleteServerBackup, downloadServerBackup,"""
new_export_fn = """loadServerBackups, createServerBackup, restoreServerBackup, deleteServerBackup,"""
if old_export_fn in content:
    content = content.replace(old_export_fn, new_export_fn)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
