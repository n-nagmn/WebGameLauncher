import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add CSS for server-backup-select
css_target = "        /* Responsive */"
css_new = """        #server-backup-select {
            padding: 4px;
        }
        #server-backup-select option {
            padding: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            cursor: pointer;
            border-radius: 4px;
        }
        body.light-mode #server-backup-select option {
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }

        /* Responsive */"""

if "#server-backup-select {" not in content:
    content = content.replace(css_target, css_new)

# 2. Remove the "復元するバックアップを選択..." placeholder option which makes no sense in a multiple select list
old_load = """                    if (data.backups.length === 0) {
                        select.innerHTML = '<option value="">バックアップがありません</option>';
                    } else {
                        let html = '<option value="">復元するバックアップを選択...</option>';
                        data.backups.forEach(b => {"""
new_load = """                    if (data.backups.length === 0) {
                        select.innerHTML = '<option value="">バックアップがありません</option>';
                    } else {
                        let html = '';
                        data.backups.forEach(b => {"""

if old_load in content:
    content = content.replace(old_load, new_load)

# 3. Remove confirm popup
old_delete = """            if (filenames.length === 0) {
                showToast('削除するバックアップを選択してください', 'warning');
                return;
            }
            if (!confirm(filenames.length + '件のバックアップを削除しますか？')) return;
            try {"""
new_delete = """            if (filenames.length === 0) {
                showToast('削除するバックアップを選択してください', 'warning');
                return;
            }
            try {"""

if old_delete in content:
    content = content.replace(old_delete, new_delete)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
