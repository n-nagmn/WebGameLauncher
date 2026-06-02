import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

funcs = """        function handleChatImageSelect() {
            const input = document.getElementById('chat-image');
            if(input.files && input.files[0]){
                const r = new FileReader();
                r.onload = e => {
                    document.getElementById('chat-image-preview-img').src = e.target.result;
                    document.getElementById('chat-image-preview-container').style.display = 'block';
                };
                r.readAsDataURL(input.files[0]);
            }
        }
        
        function clearChatImage() {
            document.getElementById('chat-image').value = '';
            document.getElementById('chat-image-preview-container').style.display = 'none';
        }
        
        function handleShareImageSelect() {"""
content = content.replace("        function handleShareImageSelect() {", funcs)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
