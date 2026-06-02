import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update <select>
old_select = """                        <select id="server-backup-select">"""
new_select = """                        <select id="server-backup-select" multiple size="8" style="height: auto;">"""
if old_select in content:
    content = content.replace(old_select, new_select)

# 2. Update restoreServerBackup
old_restore = """        async function restoreServerBackup() {
            const select = document.getElementById('server-backup-select');
            const filename = select.value;
            if (!filename) {
                showToast('復元するバックアップを選択してください', 'warning');
                return;
            }"""
new_restore = """        async function restoreServerBackup() {
            const select = document.getElementById('server-backup-select');
            const filenames = Array.from(select.selectedOptions).map(opt => opt.value).filter(v => v !== '');
            if (filenames.length !== 1) {
                showToast('復元するバックアップを「1つだけ」選択してください', 'warning');
                return;
            }
            const filename = filenames[0];"""
if old_restore in content:
    content = content.replace(old_restore, new_restore)

# 3. Update deleteServerBackup
old_delete = """        async function deleteServerBackup() {
            const select = document.getElementById('server-backup-select');
            const filename = select.value;
            if (!filename) {
                showToast('削除するバックアップを選択してください', 'warning');
                return;
            }
            try {
                const res = await fetch('./manage_backups.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'delete', filename: filename })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    showToast(data.message, 'success');
                    loadServerBackups();
                } else {
                    showToast(data.message || '削除失敗', 'error');
                }
            } catch(e) {
                showToast('通信エラー', 'error');
            }
        }"""
new_delete = """        async function deleteServerBackup() {
            const select = document.getElementById('server-backup-select');
            const filenames = Array.from(select.selectedOptions).map(opt => opt.value).filter(v => v !== '');
            if (filenames.length === 0) {
                showToast('削除するバックアップを選択してください', 'warning');
                return;
            }
            if (!confirm(filenames.length + '件のバックアップを削除しますか？')) return;
            try {
                let successCount = 0;
                for (const filename of filenames) {
                    const res = await fetch('./manage_backups.php', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ action: 'delete', filename: filename })
                    });
                    const data = await res.json();
                    if (data.status === 'success') {
                        successCount++;
                    }
                }
                showToast(successCount + '件のバックアップを削除しました', 'success');
                loadServerBackups();
            } catch(e) {
                showToast('通信エラー', 'error');
            }
        }"""
if old_delete in content:
    content = content.replace(old_delete, new_delete)
else:
    print("WARNING: old_delete not found")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
