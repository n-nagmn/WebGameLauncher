import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Fix UI for reply preview
old_chat_input = """          <div class="chat-input-area">
              <input type="text" id="chat-name" """
new_chat_input = """          <div class="chat-input-area">
              <div id="chat-reply-preview" style="display: none; font-size: 11px; padding: 4px; background: rgba(128,128,128,0.1); border-left: 3px solid var(--focus-color); margin-bottom: 4px; justify-content: space-between; align-items: center; border-radius: 4px;">
                  <span style="overflow: hidden; white-space: nowrap; text-overflow: ellipsis;"><span style="color:gray;">返信先:</span> <strong id="chat-reply-name"></strong> <span id="chat-reply-text" style="color:gray;"></span></span>
                  <button onclick="App.cancelReply(false)" style="background: none; border: none; cursor: pointer; color: gray;">✕</button>
              </div>
              <input type="text" id="chat-name" """
content = content.replace(old_chat_input, new_chat_input)

old_share_input = """          <div class="chat-input-area" style="position: relative;">
              <input type="text" id="share-name" """
new_share_input = """          <div class="chat-input-area" style="position: relative;">
              <div id="share-reply-preview" style="display: none; font-size: 11px; padding: 4px; background: rgba(128,128,128,0.1); border-left: 3px solid var(--focus-color); margin-bottom: 4px; justify-content: space-between; align-items: center; border-radius: 4px;">
                  <span style="overflow: hidden; white-space: nowrap; text-overflow: ellipsis;"><span style="color:gray;">返信先:</span> <strong id="share-reply-name"></strong> <span id="share-reply-text" style="color:gray;"></span></span>
                  <button onclick="App.cancelReply(true)" style="background: none; border: none; cursor: pointer; color: gray;">✕</button>
              </div>
              <input type="text" id="share-name" """
content = content.replace(old_share_input, new_share_input)

# Fix tempMsg replyTo
old_temp_chat = """                const tempMsg = {
                    id: 'temp_' + Date.now(),
                    name: name,
                    message: message,
                    gameId: gameId,
                    timestamp: Date.now(),
                    clientId: myClientId
                };"""
new_temp_chat = """                const tempMsg = {
                    id: 'temp_' + Date.now(),
                    name: name,
                    message: message,
                    gameId: gameId,
                    timestamp: Date.now(),
                    clientId: myClientId,
                    replyTo: currentReplyToChat
                };"""
content = content.replace(old_temp_chat, new_temp_chat)

old_temp_share = """                const tempMsg = {
                    id: 'temp_share_' + Date.now(),
                    name: name,
                    message: message,
                    gameId: gameId,
                    timestamp: Date.now(),
                    clientId: myClientId,
                    imageUrl: file ? URL.createObjectURL(file) : null
                };"""
new_temp_share = """                const tempMsg = {
                    id: 'temp_share_' + Date.now(),
                    name: name,
                    message: message,
                    gameId: gameId,
                    timestamp: Date.now(),
                    clientId: myClientId,
                    imageUrl: file ? URL.createObjectURL(file) : null,
                    replyTo: currentReplyToShare
                };"""
content = content.replace(old_temp_share, new_temp_share)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
