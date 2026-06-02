import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

old_client = "        const myClientId = 'client_' + Math.random().toString(36).substr(2, 9);"
new_client = """        let myClientId = localStorage.getItem('launcher_client_id');
        if (!myClientId) {
            myClientId = 'client_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('launcher_client_id', myClientId);
        }"""
content = content.replace(old_client, new_client)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
