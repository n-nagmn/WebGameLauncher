import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

old_func = """        async function deleteServerBackup() {
            const select = document.getElementById('server-backup-select');
            const filenames = Array.from(select.selectedOptions).map(opt => opt.value).filter(v => v !== '');
            if (filenames.length === 0) {
                showToast('削除するバックアップを選択してください', 'warning');
                return;
            }
            if (confirm(`選択した${filenames.length}件のバックアップを削除しますか？`)) {
                try {
                    let successCount = 0;
                    for (const filename of filenames) {
                        const res = await fetch('./manage_backups.php', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ action: 'delete', filename: filename })
                        });
                        const data = await res.json();
                        if (data.status === 'success') successCount++;
                    }
                    showToast(successCount + '件のバックアップを削除しました', 'success');
                    loadServerBackups();
                } catch(e) {
                    showToast('通信エラー', 'error');
                }
            }
        }"""

new_func = old_func + """

        function downloadServerBackup() {
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

if old_func in content:
    content = content.replace(old_func, new_func)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
