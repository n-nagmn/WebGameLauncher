import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update the chat-input-area HTML for Share
old_input_area = """            <div style="position: relative; width: 100%;">
                <textarea id="share-message" placeholder="メッセージを入力... (画像はドラッグ＆ドロップで添付)" rows="2" style="margin-bottom: 8px; min-height: 50px;"></textarea>
                <div id="share-image-preview-container" style="display: none; position: absolute; bottom: 16px; right: 8px; background: rgba(128,128,128,0.2); border-radius: 4px; padding: 4px; z-index: 10; backdrop-filter: blur(4px);">
                    <img id="share-image-preview-img" style="max-height: 60px; border-radius: 4px;" />
                    <button onclick="App.clearShareImage()" style="position: absolute; top: -6px; right: -6px; background: #ff5252; color: white; border: none; border-radius: 50%; width: 18px; height: 18px; cursor: pointer; font-weight: bold; display: flex; align-items: center; justify-content: center; font-size: 12px; padding: 0;">×</button>
                </div>
            </div>"""

new_input_area = """            <div style="position: relative; width: 100%; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; background: rgba(0,0,0,0.2); display: flex; flex-direction: column; min-height: 80px; box-sizing: border-box; margin-bottom: 8px;" id="share-input-wrapper">
                <textarea id="share-message" placeholder="メッセージを入力... (画像はドラッグ＆ドロップで添付)" rows="2" style="width: 100%; border: none; background: transparent; color: var(--text-color); padding: 10px; font-size: 13px; font-family: inherit; outline: none; resize: none; box-sizing: border-box; flex-grow: 1; margin: 0;"></textarea>
                <div id="share-image-preview-container" style="display: none; position: relative; margin: 0 10px 10px 10px; width: fit-content; background: rgba(128,128,128,0.1); padding: 4px; border-radius: 6px;">
                    <img id="share-image-preview-img" style="max-height: 80px; border-radius: 4px;" />
                    <button onclick="App.clearShareImage()" style="position: absolute; top: -8px; right: -8px; background: #ff5252; color: white; border: none; border-radius: 50%; width: 22px; height: 22px; cursor: pointer; font-weight: bold; display: flex; align-items: center; justify-content: center; font-size: 14px; padding: 0; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">×</button>
                </div>
            </div>"""
content = content.replace(old_input_area, new_input_area)

# 2. Revert the padding-right hacks in handleShareImageSelect and clearShareImage
old_handle_select = """        function handleShareImageSelect() {
            const input = document.getElementById('share-image');
            if(input.files && input.files[0]){
                const r = new FileReader();
                r.onload = e => {
                    document.getElementById('share-image-preview-img').src = e.target.result;
                    document.getElementById('share-image-preview-container').style.display = 'block';
                    document.getElementById('share-message').style.paddingRight = '80px';
                };
                r.readAsDataURL(input.files[0]);
            }
        }"""

new_handle_select = """        function handleShareImageSelect() {
            const input = document.getElementById('share-image');
            if(input.files && input.files[0]){
                const r = new FileReader();
                r.onload = e => {
                    document.getElementById('share-image-preview-img').src = e.target.result;
                    document.getElementById('share-image-preview-container').style.display = 'block';
                };
                r.readAsDataURL(input.files[0]);
            }
        }"""
content = content.replace(old_handle_select, new_handle_select)

old_clear_select = """        function clearShareImage() {
            document.getElementById('share-image').value = '';
            document.getElementById('share-image-preview-container').style.display = 'none';
            document.getElementById('share-message').style.paddingRight = '10px';
        }"""

new_clear_select = """        function clearShareImage() {
            document.getElementById('share-image').value = '';
            document.getElementById('share-image-preview-container').style.display = 'none';
        }"""
content = content.replace(old_clear_select, new_clear_select)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
