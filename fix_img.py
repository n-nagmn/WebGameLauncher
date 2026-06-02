import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Add the Image Modal HTML just before </body>
image_modal_html = """
    <!-- Image Lightbox Modal -->
    <div class="modal" id="image-modal" role="dialog" aria-modal="true" aria-label="画像拡大" onclick="App.closeImageModal()">
        <img id="image-modal-img" src="" style="max-width: 90%; max-height: 90%; object-fit: contain; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); cursor: zoom-out;">
    </div>
</body>"""
if "<!-- Image Lightbox Modal -->" not in content:
    content = content.replace("</body>", image_modal_html)

# Add openImageModal and closeImageModal
funcs = """        function closeShare() {
            document.getElementById('share-sidebar').classList.remove('active');
            document.body.classList.remove('chat-open');
        }

        function openImageModal(url) {
            const modal = document.getElementById('image-modal');
            const img = document.getElementById('image-modal-img');
            img.src = url;
            modal.style.display = 'flex';
            setTimeout(() => modal.style.opacity = '1', 10);
        }

        function closeImageModal() {
            const modal = document.getElementById('image-modal');
            modal.style.opacity = '0';
            setTimeout(() => {
                modal.style.display = 'none';
                document.getElementById('image-modal-img').src = '';
            }, 300);
        }"""
old_funcs = """        function closeShare() {
            document.getElementById('share-sidebar').classList.remove('active');
            document.body.classList.remove('chat-open');
        }"""
if "function openImageModal(" not in content:
    content = content.replace(old_funcs, funcs)

# Add to App exports
old_export = """            openShare, closeShare, submitShare, handleShareImageSelect, clearShareImage, deleteShareMessage
        };"""
new_export = """            openShare, closeShare, submitShare, handleShareImageSelect, clearShareImage, deleteShareMessage,
            openImageModal, closeImageModal
        };"""
if "openImageModal, closeImageModal" not in content:
    content = content.replace(old_export, new_export)

# Replace target="_blank" image links in Share render
old_share_img = """${msg.imageUrl ? `<div style="margin-top: 8px;"><a href="${escapeHtml(msg.imageUrl)}" target="_blank"><img src="${escapeHtml(msg.imageUrl)}" style="max-width: 50%; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2);" alt="Image"></a></div>` : ''}"""
new_share_img = """${msg.imageUrl ? `<div style="margin-top: 8px;"><img src="${escapeHtml(msg.imageUrl)}" onclick="App.openImageModal('${escapeHtml(msg.imageUrl)}')" style="max-width: 50%; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); cursor: zoom-in;" alt="Image"></div>` : ''}"""
content = content.replace(old_share_img, new_share_img)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
