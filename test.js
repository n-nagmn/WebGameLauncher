
    /**
     * ========================================
     * Web Game Launcher Pro - Core Module
     * ========================================
     */
    const App = (function() {
        'use strict';

        // --- Constants & Defaults ---
        const DEFAULT_SERVER_CONFIG = {
            bgImage: '',
            categoryOrder: []
        };

        const DEFAULT_LOCAL_CONFIG = {
            gridSize: '240px',
            clockFormat: '24h',
            accentColor: '#00e6e6',
            borderRadius: '8px',
            cardGap: '20px',
            showTitle: true,
            openInNewTab: true,
            enableAnimations: true,
            isLightMode: false
        };

        const CATEGORY_LABELS = {
            action: 'アクション', puzzle: 'パズル', rpg: 'RPG',
            shooter: 'シューティング', sports: 'スポーツ',
            strategy: 'ストラテジー', casual: 'カジュアル', retro: 'レトロ'
        };

        // --- State ---
        let serverConfig = { ...DEFAULT_SERVER_CONFIG };
        let localConfig = JSON.parse(localStorage.getItem('launcher_local_config')) || { ...DEFAULT_LOCAL_CONFIG };
        
        let games = [];
        let filteredGames = [];
        let dragStartIndex = null;
        let categoryDragStartIndex = null;
        let focusedCardIndex = -1;
        let currentCategory = 'all';
        let isRankingActive = false;
        let serverTimestamps = null;
        let isSaving = false;
        
        // Chat state
        let chatMessages = [];
        let shareMessages = [];
        let initialShareLoaded = false;
        let chatSidebarOpen = false;
        let initialChatLoaded = false;
        const myClientId = 'client_' + Math.random().toString(36).substr(2, 9);

        // --- DOM Elements ---
        const els = {};

        // --- Utilities ---

        function getUniqueUserId() {
            let userId = localStorage.getItem('launcher_user_id');
            if (!userId) {
                userId = 'u_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                localStorage.setItem('launcher_user_id', userId);
            }
            return userId;
        }

        function escapeHtml(str) {
            if (typeof str !== 'string') return '';
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        }

        function showToast(message, type = 'info', duration = 3000) {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;

            const icons = { info: '??', success: '?', error: '?', warning: '??' };
            toast.innerHTML = `<span class="toast-icon">${icons[type] || icons.info}</span><span>${escapeHtml(message)}</span>`;

            container.appendChild(toast);
            requestAnimationFrame(() => toast.classList.add('show'));

            const tId = setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, duration);

            toast.onclick = () => {
                clearTimeout(tId);
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            };
        }

        function showChatNotification(msg) {
            const container = document.getElementById('chat-notification-container');
            const notif = document.createElement('div');
            notif.className = 'chat-notification';
            
            const timeStr = new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            const name = msg.name || '名無しさん';
            
            notif.dataset.timestamp = msg.timestamp;
            notif.dataset.name = name;
            notif.dataset.messageText = msg.message;
            
            let gameHtml = '';
            if (msg.gameId) {
                const game = games.find(g => g.id == msg.gameId);
                if (game) {
                    gameHtml = `<div class="chat-notification-game">?? ${escapeHtml(game.name)}</div>`;
                }
            }

            notif.innerHTML = `
                <div class="chat-notification-header">
                    <span class="chat-notification-name">${escapeHtml(name)}</span>
                    <span>${timeStr}</span>
                </div>
                ${gameHtml}
                ${(() => { let msgText = msg.message; if (msgText.toLowerCase().startsWith('/a')) { return `<div class="chat-notification-text aa-font">${escapeHtml(msgText.replace(/^\/a(?:\r?\n| )?/i, ''))}</div>`; } return `<div class="chat-notification-text">${escapeHtml(msgText)}</div>`; })()}
            `;

            notif.onclick = (e) => {
                e.stopPropagation();
                notif.classList.add('hiding');
                setTimeout(() => notif.remove(), 300);
                let dismissed = JSON.parse(localStorage.getItem('dismissedChatNotifs') || '[]');
                if (!dismissed.includes(msg.id)) {
                    dismissed.push(msg.id);
                    if (dismissed.length > 200) dismissed = dismissed.slice(-200);
                    localStorage.setItem('dismissedChatNotifs', JSON.stringify(dismissed));
                }
                if (msg.gameId) {
                    openChatGame(msg.gameId);
                }
            };

            container.prepend(notif);

            // AA Auto-scaling for notification
            const aaEl = notif.querySelector('.chat-notification-text.aa-font');
            if (aaEl) {
                requestAnimationFrame(() => {
                    aaEl.style.zoom = 1;
                    const maxW = window.innerWidth * 0.85;
                    const maxH = window.innerHeight * 0.85;
                    const scaleW = maxW / aaEl.scrollWidth;
                    const scaleH = maxH / aaEl.scrollHeight;
                    const scale = Math.min(1, scaleW, scaleH) * 0.98;
                    if (scale < 1) {
                        aaEl.style.zoom = scale;
                        aaEl.style.overflow = 'hidden';
                    }
                });
            }

            // Ensure notification can scroll if it's too large
            setTimeout(() => notif.classList.add('show'), 10);
        }

        function hexToRgb(hex) {
            hex = hex.replace('#', '');
            if (hex.length === 3) hex = hex.split('').map(c => c + c).join('');
            const r = parseInt(hex.substring(0, 2), 16);
            const g = parseInt(hex.substring(2, 4), 16);
            const b = parseInt(hex.substring(4, 6), 16);
            return `${r}, ${g}, ${b}`;
        }

        function generateHash(str) {
            let hash = 0;
            for (let i = 0; i < str.length; i++) {
                hash = str.charCodeAt(i) + ((hash << 5) - hash);
            }
            return hash;
        }

        function generatePlaceholderImage(title) {
            const canvas = document.createElement('canvas');
            canvas.width = 400; 
            canvas.height = 225;
            const ctx = canvas.getContext('2d');
            const hash = generateHash(title);

            const c1 = (hash & 0x00FFFFFF).toString(16).toUpperCase().padStart(6, '0');
            const c2 = ((hash >> 1) & 0x00FFFFFF).toString(16).toUpperCase().padStart(6, '0');

            const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
            gradient.addColorStop(0, '#' + c1);
            gradient.addColorStop(1, '#' + c2);
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = '#ffffff';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.font = "bold 100px 'Segoe UI', sans-serif";
            ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
            ctx.shadowBlur = 20;
            ctx.shadowOffsetX = 4;
            ctx.shadowOffsetY = 4;

            const initials = title.substring(0, Math.min(title.length, 2)).toUpperCase();
            ctx.fillText(initials, canvas.width / 2, canvas.height / 2);
            return canvas.toDataURL('image/png');
        }

        // --- Server Communication ---

        async function saveGamesToServer() {
            isSaving = true;
            try {
                const response = await fetch('./save_games.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(games)
                });
                const data = await response.json();
                if (data.status !== 'success') throw new Error(data.message);
                
                try {
                    const tsRes = await fetch('./check_timestamp.php?t=' + Date.now());
                    if (tsRes.ok) serverTimestamps = await tsRes.json();
                } catch(e) {}
                isSaving = false;
                
                return true;
            } catch (error) {
                console.error('Save error:', error);
                showToast('サーバー保存に失敗: ' + error.message, 'error', 5000);
                isSaving = false;
                return false;
            }
        }

        async function saveConfigToServer() {
            isSaving = true;
            try {
                const response = await fetch('./save_config.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(serverConfig)
                });
                const data = await response.json();
                if (data.status !== 'success') throw new Error(data.message);
                showToast('設定を保存しました', 'success');
                
                try {
                    const tsRes = await fetch('./check_timestamp.php?t=' + Date.now());
                    if (tsRes.ok) serverTimestamps = await tsRes.json();
                } catch(e) {}
                isSaving = false;
                
                return true;
            } catch (error) {
                console.error('Config save error:', error);
                showToast('設定の保存に失敗: ' + error.message, 'error', 5000);
                isSaving = false;
                return false;
            }
        }

        // --- Chat Functionality ---

        async function fetchChat() {
            try {
                const res = await fetch('./chat.json?t=' + Date.now());
                if (res.ok) {
                    const newMessages = await res.json();
                    if (JSON.stringify(newMessages) !== JSON.stringify(chatMessages)) {
                        // Remove notifications for deleted messages
                        document.querySelectorAll('.chat-notification').forEach(notif => {
                            const ts = parseInt(notif.dataset.timestamp);
                            const nName = notif.dataset.name;
                            const nMsg = notif.dataset.messageText;
                            if (ts && !newMessages.some(m => 
                                (m.timestamp === ts) || 
                                (m.name === nName && m.message === nMsg && Math.abs(m.timestamp - ts) < 60000)
                            )) {
                                notif.classList.add('hiding');
                                setTimeout(() => notif.remove(), 300);
                            }
                        });

                        // Check for new messages from others
                        if (initialChatLoaded) {
                            const newItems = newMessages.filter(m => !chatMessages.some(old => old.id === m.id) && m.clientId !== myClientId);
                            newItems.forEach(msg => {
                                showChatNotification(msg);
                            });
                        } else {
                            let dismissed = JSON.parse(localStorage.getItem('dismissedChatNotifs') || '[]');
                            const oneDayAgo = Date.now() - (24 * 60 * 60 * 1000);
                            newMessages.forEach(msg => {
                                if (msg.clientId !== myClientId && !dismissed.includes(msg.id) && msg.timestamp > oneDayAgo) {
                                    showChatNotification(msg);
                                }
                            });
                        }
                        chatMessages = newMessages;
                        initialChatLoaded = true;
                        renderChat();
                    } else {
                        initialChatLoaded = true;
                    }
                }
            } catch (e) {
                // Silently fail if chat not ready
            }
        }

        function renderChat() {
            const container = document.getElementById('chat-messages');
            if (!container) return;
            
            if (chatMessages.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: #888; font-size: 13px; margin-top: 20px;">まだメッセージはありません<br>一緒に遊ぶ人を募集してみましょう！</div>';
                return;
            }

            let html = '';
            chatMessages.forEach(msg => {
                const timeStr = new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                const name = msg.name || '名無しさん';
                let gameHtml = '';
                if (msg.gameId) {
                    const game = games.find(g => g.id == msg.gameId);
                    if (game) {
                        gameHtml = `<div class="chat-message-game" onclick="App.openChatGame(${game.id})">?? ${escapeHtml(game.name)}</div>`;
                    }
                }
                
                html += `
                    <div class="chat-message-item" id="msg-${msg.id}">
                        <div class="chat-message-header" style="display: flex; justify-content: space-between; font-size: 11px; color: #888; margin-bottom: 3px; align-items: center;">
                            <div>
                                <span class="chat-message-name">${escapeHtml(name)}</span>
                                
                                <span>${timeStr}</span>
                            </div>
                            <button onclick="App.deleteChatMessage(${msg.timestamp})" title="削除" style="background: none; border: none; color: #ff5252; cursor: pointer; font-size: 14px; padding: 0 4px; opacity: 0.6;">×</button>
                        </div>
                        ${gameHtml}
                        ${msg.imageUrl ? `<div style="margin-top: 8px;"><a href="${escapeHtml(msg.imageUrl)}" target="_blank"><img src="${escapeHtml(msg.imageUrl)}" style="max-width: 100%; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);" alt="Image"></a></div>` : ''}
                        ${(() => { let msgText = msg.message || ''; if (msgText === '') return ''; if (msgText.toLowerCase().startsWith('/a')) { return `<div class="chat-message-text aa-font">${escapeHtml(msgText.replace(/^\/a(?:\r?\n| )?/i, ''))}</div>`; } return `<div class="chat-message-text">${escapeHtml(msgText)}</div>`; })()}
                    </div>
                `;
            });
            container.innerHTML = html;
            
            // AA Auto-scaling to fit within a defined box
            requestAnimationFrame(() => {
                container.querySelectorAll('.chat-message-text.aa-font').forEach(el => {
                    // Reset zoom to measure original size
                    el.style.zoom = 1;
                    const parentW = el.parentElement.clientWidth;
                    const maxW = parentW - 24; // Parent width minus padding
                    const maxH = 250; // Defined box height

                    const scaleW = maxW / el.scrollWidth;
                    const scaleH = maxH / el.scrollHeight;

                    // Scale down with a 2% safety margin to prevent 1px scrollbars
                    const scale = Math.min(1, scaleW, scaleH) * 0.98;
                    
                    if (scale < 1) {
                        el.style.zoom = scale;
                        el.style.overflow = 'hidden';
                    }
                });
            });

            // Scroll to bottom
            setTimeout(() => {
                container.scrollTop = container.scrollHeight;
            }, 10);
        }

        function openChat() {
            document.body.classList.add('chat-open');
            document.getElementById('chat-sidebar').classList.add('active');
            
            // Populate game select
            const select = document.getElementById('chat-game-select');
            let options = '<option value="">ゲーム指定なし</option>';
            games.forEach(g => {
                options += `<option value="${g.id}">${escapeHtml(g.name)}</option>`;
            });
            select.innerHTML = options;
            
            // Restore name
            let savedName = localStorage.getItem('chat_name');
            if (savedName === '名無しさん') {
                localStorage.removeItem('chat_name');
                savedName = null;
            }
            if (savedName) {
                document.getElementById('chat-name').value = savedName;
            } else {
                document.getElementById('chat-name').value = '';
            }

            fetchChat();
        }

        function closeChat() {
            document.body.classList.remove('chat-open');
            document.getElementById('chat-sidebar').classList.remove('active');
        }

        async function sendChatMessage() {
            const nameInput = document.getElementById('chat-name');
            const msgInput = document.getElementById('chat-message');
            const gameSelect = document.getElementById('chat-game-select');
            
            let inputName = nameInput.value.trim();
            const message = msgInput.value.trim();
            const gameId = gameSelect.value ? parseInt(gameSelect.value, 10) : null;
            if (!message) return;
            
            const isAa = message.toLowerCase().startsWith('/a');
            
            if (isAa) {
                const lines = message.split('\n');
                if (lines.some(line => line.trim().length > 1000)) {
                    showToast("アスキーアートの1行の最大文字数は1000文字までです", "error");
                    return;
                }
            } else if (message.length > 300) {
                showToast("通常チャットの最大文字数は300文字です", "error");
                return;
            }
            
            const lineCount = (message.match(/\n/g) || []).length + 1;
            if (lineCount >= 5 && !isAa) {
                showToast("AA（アスキーアート）を送信する場合は先頭に /a を付けてください", "error");
                msgInput.value = '';
                msgInput.style.height = 'auto';
                return;
            }
            if (inputName && inputName !== '名無しさん') {
                localStorage.setItem('chat_name', inputName);
            } else {
                localStorage.removeItem('chat_name');
            }
            let name = inputName || '名無しさん';
            
            // Optimistic update
            const tempMsg = {
                id: 'temp_' + Date.now(),
                name: name,
                message: message,
                gameId: gameId,
                timestamp: Date.now(),
                clientId: myClientId
            };
            chatMessages.push(tempMsg);
            renderChat();
            
            msgInput.value = '';
            msgInput.style.height = 'auto';
            
            try {
                const res = await fetch('./post_chat.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, message, gameId, clientId: myClientId })
                });
                if (res.ok) {
                    showChatNotification(tempMsg);
                    fetchChat();
                } else {
                    showToast('チャット送信失敗', 'error');
                }
            } catch (e) {
                showToast('通信エラー', 'error');
            }
        }

        function openChatGame(id) {
            const game = games.find(g => g.id == id);
            if (game) {
                launchGame(game);
            }
        }

        // --- Rendering ---

        function renderFilters() {
            // Category filter
            const catContainer = document.getElementById('category-filter');
            const availableCategories = Array.from(new Set(games.map(g => g.category).filter(Boolean)));
            
            // サーバーから取得した順序に基づいて並び替え
            const sortedCategories = [...availableCategories].sort((a, b) => {
                const orderA = serverConfig.categoryOrder ? serverConfig.categoryOrder.indexOf(a) : -1;
                const orderB = serverConfig.categoryOrder ? serverConfig.categoryOrder.indexOf(b) : -1;
                
                if (orderA === -1 && orderB === -1) return a.localeCompare(b);
                if (orderA === -1) return 1;
                if (orderB === -1) return -1;
                return orderA - orderB;
            });

            let catHtml = `<div class="category-chip ${currentCategory === 'all' ? 'active' : ''}" data-cat="all" onclick="App.setCategory('all')">すべて</div>`;
            
            sortedCategories.forEach((cat, idx) => {
                const label = CATEGORY_LABELS[cat] || cat;
                const isActive = currentCategory === cat;
                catHtml += `
                    <div class="category-chip ${isActive ? 'active' : ''}" 
                         data-cat="${escapeHtml(cat)}" 
                         draggable="true"
                         oncontextmenu="return false;"
                         onclick="App.setCategory('${escapeHtml(cat)}')"
                         ondragstart="App.handleCategoryDragStart(event, ${idx})"
                         ondragover="App.handleCategoryDragOver(event)"
                         ondrop="App.handleCategoryDrop(event, ${idx})"
                         ondragend="App.handleCategoryDragEnd(event)">
                        ${escapeHtml(label)}
                    </div>`;
            });
            catContainer.innerHTML = catHtml;

            // Ranking Toggle (Separate from categories)
            const rankingContainer = document.getElementById('ranking-toggle-container');
            if (rankingContainer) {
                rankingContainer.innerHTML = `
                    <div class="category-chip ${isRankingActive ? 'active' : ''}" onclick="App.toggleRanking()" style="margin-left: 0; margin-right: 12px; border-color: rgba(255, 215, 0, 0.4);">
                        ?? ランキング
                    </div>
                `;
            }

            // Player filter
            const playerContainer = document.getElementById('player-filter');
            let playerHtml = `<div class="player-chip ${currentPlayerFilter === 'all' ? 'active' : ''}" data-players="all" onclick="App.setPlayerFilter('all')">全人数</div>`;

            const filterOptions = [
                { id: '1', label: '1人', isMulti: false },
                { id: '2', label: '2人', isMulti: true },
                { id: '3', label: '3人', isMulti: true },
                { id: '4', label: '4人', isMulti: true },
                { id: '5plus', label: '5人以上', isMulti: true }
            ];

            filterOptions.forEach(opt => {
                const isActive = currentPlayerFilter === opt.id;
                playerHtml += `<div class="player-chip ${opt.isMulti ? 'multi' : ''} ${isActive ? 'active' : ''}" data-players="${opt.id}" onclick="App.setPlayerFilter('${opt.id}')">${escapeHtml(opt.label)}</div>`;
            });
            playerContainer.innerHTML = playerHtml;
        }

        function renderGames() {
            const grid = els.grid;
            grid.innerHTML = '';

            const searchTerm = els.searchInput.value.toLowerCase().trim();
            
            filteredGames = games.filter(game => {
                const matchesSearch = !searchTerm || game.name.toLowerCase().includes(searchTerm);
                const matchesCategory = currentCategory === 'all' || game.category === currentCategory;

                let matchesPlayers = true;
                if (currentPlayerFilter !== 'all') {
                    const gameMin = parseInt(game.playersMin, 10) || 0;
                    const gameMax = parseInt(game.playersMax, 10) || 0;
                    
                    if (gameMin === 0 && gameMax === 0) {
                        matchesPlayers = false; 
                    } else {
                        const gMin = gameMin || 1;
                        const gMax = gameMax || gMin;
                        
                        if (currentPlayerFilter === '5plus') {
                            matchesPlayers = (gMax >= 5);
                        } else {
                            const target = parseInt(currentPlayerFilter, 10);
                            matchesPlayers = (target >= gMin && target <= gMax);
                        }
                    }
                }

                return matchesSearch && matchesCategory && matchesPlayers;
            });

            if (isRankingActive) {
                // ランキング有効時はプレイ回数順（降順）
                filteredGames.sort((a, b) => (b.playCount || 0) - (a.playCount || 0));
            } else { filteredGames.sort((a, b) => { if (a.isPinned && !b.isPinned) return -1; if (!a.isPinned && b.isPinned) return 1; if (a.hasUpdate && !b.hasUpdate) return -1; if (!a.hasUpdate && b.hasUpdate) return 1; return (b.lastPlayed || 0) - (a.lastPlayed || 0); }); }

            if (filteredGames.length === 0 && games.length > 0) {
                grid.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">??</div>
                        <div class="empty-state-text">該当するゲームが見つかりません</div>
                        <div class="empty-state-hint">検索条件を変更するか、新しいゲームを追加してください</div>
                    </div>`;
                return;
            }

            const fragment = document.createDocumentFragment();

            filteredGames.forEach((game, index) => {
                const card = document.createElement('div');
                card.className = 'game-card' + (game.isPinned ? ' pinned' : '');
                card.dataset.index = index;
                card.dataset.id = game.id;
                card.draggable = true;
                card.tabIndex = 0;
                card.setAttribute('role', 'button');
                card.setAttribute('aria-label', `${game.name}、Enterで起動`);

                // Events for Drag & Drop
                card.addEventListener('dragstart', e => handleDragStart(e, index));
                card.addEventListener('dragover', handleDragOver);
                card.addEventListener('drop', e => handleDrop(e, index));
                card.addEventListener('dragenter', handleDragEnter);
                card.addEventListener('dragleave', handleDragLeave);
                card.addEventListener('dragend', handleDragEnd);
                
                card.addEventListener('keydown', e => handleCardKeydown(e, index));
                card.addEventListener('focus', () => { focusedCardIndex = index; card.classList.add('focused'); });
                card.addEventListener('blur', () => card.classList.remove('focused'));

                card.addEventListener('click', e => {
                    if (e.target.closest('.edit-btn') || e.target.closest('.pin-btn')) return;
                    launchGame(game);
                });

                // --- UPDATE / NEW / PINNED Badge Logic ---
                const readHistory = JSON.parse(localStorage.getItem('gameReadHistory')) || {};
                const lastReadTime = readHistory[game.id] || 0;

                const createdAtMs = game.createdAt ? (game.createdAt > 9999999999 ? game.createdAt : game.createdAt * 1000) : 0;
                const remoteUpdatedMs = game.remoteUpdatedAt ? (game.remoteUpdatedAt > 9999999999 ? game.remoteUpdatedAt : game.remoteUpdatedAt * 1000) : 0;
                const manualUpdatedMs = game.updatedAt ? (game.updatedAt > 9999999999 ? game.updatedAt : game.updatedAt * 1000) : 0;
                const latestUpdateMs = Math.max(remoteUpdatedMs, manualUpdatedMs);

                const isActuallyUpdated = (latestUpdateMs - createdAtMs) > 1000;
                const isNew = createdAtMs && (Date.now() - createdAtMs < 7 * 24 * 60 * 60 * 1000) && (lastReadTime < createdAtMs);
                const isUpdate = (lastReadTime < latestUpdateMs) && (isActuallyUpdated || game.hasUpdate);

                let badge = '';
                if (isUpdate) {
                    badge = '<span class="card-badge" style="background: var(--warning-color); color: #000;">UPDATE</span>';
                } else if (isNew) {
                    badge = '<span class="card-badge new">NEW</span>';
                }
                
                // --- Active Badge Logic ---
                const now = Date.now();
                const lastPlayed = game.lastPlayed || 0;
                const diffMs = now - lastPlayed;
                let activeBadge = '';
                if (isRankingActive) { const plays = game.playCount || 0; activeBadge = `<span class="active-badge" style="background: rgba(0, 0, 0, 0.8); color: #ffd700; border: 1px solid #ff4757; padding: 4px 8px; font-size: 12px; letter-spacing: 0.5px;">?? ${plays}</span>`; } else if (lastPlayed > 0 && diffMs < 3600000) {
                    const diffMins = Math.floor(diffMs / 60000);
                    
                    // ユニークユーザー数のカウント（過去1時間以内）
                    let activeUserCount = 0;
                    if (game.activeUsers) {
                        const oneHourAgo = now - 3600000;
                        activeUserCount = Object.values(game.activeUsers).filter(ts => ts > oneHourAgo).length;
                    }
                    // もしアクティブユーザーがいない（データ不整合など）場合は最低1人とする
                    if (activeUserCount === 0) activeUserCount = 1;

                    activeBadge = `
                        <span class="active-badge">
                            ${diffMins}分前アクティブ<br>
                            <span style="font-size: 9px; opacity: 0.8;">(${activeUserCount}人)</span>
                        </span>`;
                }

                const catLabel = game.category ? (CATEGORY_LABELS[game.category] || game.category) : '';
                const catHtml = catLabel ? `<div class="card-category">${escapeHtml(catLabel)}</div>` : '';

                const imgUrl = game.image || generatePlaceholderImage(game.name);

                let playerBadge = '';
                if (game.playersMin || game.playersMax) {
                    const min = game.playersMin ? parseInt(game.playersMin, 10) : null;
                    const max = game.playersMax ? parseInt(game.playersMax, 10) : null;
                    const isMulti = (min && min > 1) || (max && max > 1) || (!min && max && max > 1);

                    let label = '';
                    if (min && max) {
                        if (min === max) {
                            label = min >= 999 ? '??' : min + '人';
                        } else {
                            const maxLabel = max >= 999 ? '??' : max;
                            label = min + '?' + maxLabel + '人';
                        }
                    } else if (min) {
                        label = min >= 999 ? '??' : min + '人?';
                    } else if (max) {
                        label = max >= 999 ? '???' : '?' + max + '人';
                    }

                    playerBadge = `<span class="player-badge ${isMulti ? 'multi' : ''}">${label}</span>`;
                }

                card.innerHTML = `
                    ${badge}
                    ${activeBadge}
                    ${playerBadge}
                    <button class="pin-btn" title="${game.isPinned ? '固定を解除' : '位置を固定'}" onclick="App.togglePin(${game.id}, event)">${game.isPinned ? '??' : '??'}</button>
                    <button class="edit-btn" title="編集" onclick="App.openGameModal(${game.id}, event)" aria-label="${escapeHtml(game.name)}を編集">?</button>
                    <img src="${escapeHtml(imgUrl)}" alt="" loading="lazy" onerror="this.src='${generatePlaceholderImage(game.name)}'" onload="this.classList.add('loaded')">
                    <div class="title-bar" title="${escapeHtml(game.name)}">${escapeHtml(game.name)}</div>
                    ${catHtml}
                `;
                fragment.appendChild(card);
            });

            // Add button
            const addCard = document.createElement('div');
            addCard.className = 'game-card add-card';
            addCard.id = 'add-card-btn';
            addCard.innerHTML = `
                <div style="width: 100%; aspect-ratio: 16 / 9; flex-grow: 1;"></div>
                <div class="title-bar" style="visibility: hidden;">..</div>
                <div class="card-category" style="visibility: hidden;">..</div>
                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; font-size: 48px;">＋</div>
            `;
            addCard.title = "新しいゲームを追加 (N)";
            addCard.setAttribute('role', 'button');
            addCard.setAttribute('tabindex', '0');
            addCard.setAttribute('aria-label', '新しいゲームを追加');
            addCard.onclick = () => openGameModal();
            addCard.addEventListener('keydown', e => { if (e.key === 'Enter') openGameModal(); });
            fragment.appendChild(addCard);

            grid.appendChild(fragment);
            renderFilters();
        }

        // --- Pin Function ---
        function togglePin(id, event) {
            if (event) event.stopPropagation();
            const index = games.findIndex(g => g.id == id);
            if (index !== -1) {
                games[index].isPinned = !games[index].isPinned;
                games[index].updatedAt = Date.now();
                showToast(games[index].isPinned ? 'ピン留めしました' : 'ピン留めを解除しました', 'success');
                renderGames();
                saveGamesToServer();
            }
        }

        // --- Category Drag & Drop ---
        function handleCategoryDragStart(e, index) {
            categoryDragStartIndex = index;
            e.currentTarget.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
        }

        function handleCategoryDragOver(e) {
            e.preventDefault();
        }

        function handleCategoryDrop(e, dropIndex) {
            e.preventDefault();
            if (categoryDragStartIndex === null || categoryDragStartIndex === dropIndex) return;

            const availableCategories = Array.from(new Set(games.map(g => g.category).filter(Boolean)));
            const sortedCategories = [...availableCategories].sort((a, b) => {
                const orderA = serverConfig.categoryOrder ? serverConfig.categoryOrder.indexOf(a) : -1;
                const orderB = serverConfig.categoryOrder ? serverConfig.categoryOrder.indexOf(b) : -1;
                if (orderA === -1 && orderB === -1) return a.localeCompare(b);
                if (orderA === -1) return 1;
                if (orderB === -1) return -1;
                return orderA - orderB;
            });

            const [movedItem] = sortedCategories.splice(categoryDragStartIndex, 1);
            sortedCategories.splice(dropIndex, 0, movedItem);

            serverConfig.categoryOrder = sortedCategories;
            saveConfigToServer();
            renderFilters();
            showToast('カテゴリーの順序を更新しました', 'success');
        }

        function handleCategoryDragEnd(e) {
            e.currentTarget.classList.remove('dragging');
            categoryDragStartIndex = null;
        }

        // === プレイ時に順番を入れ替える（ピン留め以外） ===
        function launchGame(game) {
            if (!game.url) return;
            window.open(game.url, localConfig.openInNewTab ? '_blank' : '_self', 'noopener,noreferrer');
            
            // 個人の既読時刻を記録
            const readHistory = JSON.parse(localStorage.getItem('gameReadHistory')) || {};
            readHistory[game.id] = Date.now();
            localStorage.setItem('gameReadHistory', JSON.stringify(readHistory));

            // プレイ回数をインクリメント
            game.playCount = (game.playCount || 0) + 1;

            // アクティブユーザー情報を更新（ユニークIDを使用）
            const userId = getUniqueUserId();
            if (!game.activeUsers || Array.isArray(game.activeUsers)) game.activeUsers = {}; 
            game.activeUsers[userId] = Date.now();

            // 1時間以上前の古いユーザーデータを削除して肥大化を防ぐ
            const oneHourAgo = Date.now() - 3600000;
            for (const id in game.activeUsers) {
                if (game.activeUsers[id] < oneHourAgo) {
                    delete game.activeUsers[id];
                }
            }

            // ピン留めされていない場合のみ、先頭（ピン留めの下）に移動
            if (!game.isPinned) {
                const globalIndex = games.findIndex(g => g.id === game.id);
                if (globalIndex > -1) {
                    const [playedGame] = games.splice(globalIndex, 1);
                    playedGame.lastPlayed = Date.now();
                    playedGame.hasUpdate = false;
                    
                    // 最初の非ピン留めアイテムのインデックスを探す
                    let insertIndex = 0;
                    while (insertIndex < games.length && games[insertIndex].isPinned) {
                        insertIndex++;
                    }
                    games.splice(insertIndex, 0, playedGame);
                    
                    saveGamesToServer();       
                    renderGames();             
                }
            } else {
                // ピン留めされている場合は時刻だけ更新
                game.lastPlayed = Date.now();
                game.hasUpdate = false;
                saveGamesToServer();
                renderGames();
            }
        }

        function setCategory(cat) {
            if (currentCategory === cat) {
                currentCategory = 'all';
            } else {
                currentCategory = cat;
            }
            renderGames();
        }

        let currentPlayerFilter = 'all';

        function setPlayerFilter(filter) {
            currentPlayerFilter = filter;
            renderGames();
        }

        // --- Drag & Drop (Games) ---

        function handleDragStart(e, index) {
            if (els.searchInput.value.trim() !== '' || currentCategory !== 'all' || currentPlayerFilter !== 'all') {
                e.preventDefault();
                showToast('検索中またはフィルタ中は並び替えできません', 'warning');
                return;
            }
            dragStartIndex = index;
            e.currentTarget.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', index);
        }

        function handleDragOver(e) { e.preventDefault(); }

        function handleDragEnter(e) {
            e.preventDefault();
            const card = e.currentTarget;
            if (!card.classList.contains('add-card') && !card.classList.contains('dragging')) {
                card.style.transform = `scale(${localConfig.enableAnimations ? '1.02' : '1'})`;
                card.style.borderColor = 'var(--focus-color)';
            }
        }

        function handleDragLeave(e) {
            const card = e.currentTarget;
            if (!card.classList.contains('dragging')) {
                card.style.transform = '';
                card.style.borderColor = '';
            }
        }

        function handleDrop(e, dropIndex) {
            e.preventDefault();
            const card = e.currentTarget;
            card.style.transform = '';
            card.style.borderColor = '';

            if (dragStartIndex === null || dragStartIndex === dropIndex) return;

            // フィルター適用後のリストを元に、元の games 配列を操作
            const movedId = filteredGames[dragStartIndex].id;
            const targetId = filteredGames[dropIndex].id;
            
            const fromIndex = games.findIndex(g => g.id === movedId);
            const toIndex = games.findIndex(g => g.id === targetId);

            const [item] = games.splice(fromIndex, 1);
            games.splice(toIndex, 0, item);
            
            renderGames();
            saveGamesToServer(); 
            showToast('並び順を変更しました', 'success');
        }

        function handleDragEnd() {
            document.querySelectorAll('.game-card').forEach(c => {
                c.classList.remove('dragging');
                c.style.transform = '';
                c.style.borderColor = '';
            });
            dragStartIndex = null;
        }

        // --- Keyboard Navigation ---

        function handleCardKeydown(e, index) {
            const cards = document.querySelectorAll('.game-card:not(.add-card)');
            const cols = Math.floor(els.grid.offsetWidth / (els.grid.children[0]?.offsetWidth || 240));

            switch(e.key) {
                case 'ArrowRight':
                    e.preventDefault();
                    if (index + 1 < cards.length) cards[index + 1].focus();
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    if (index - 1 >= 0) cards[index - 1].focus();
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    if (index + cols < cards.length) cards[index + cols].focus();
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    if (index - cols >= 0) cards[index - cols].focus();
                    break;
                case 'Enter':
                    e.preventDefault();
                    launchGame(filteredGames[index]);
                    break;
                case 'Delete':
                case 'd':
                    if (e.key === 'd' && !e.ctrlKey) break;
                    e.preventDefault();
                    openGameModal(filteredGames[index].id);
                    setTimeout(() => document.getElementById('btn-delete').click(), 100);
                    break;
            }
        }

        document.addEventListener('keydown', e => {
            if (els.gameModal.classList.contains('active') || els.settingsModal.classList.contains('active')) return;


            if (e.key === 'Escape') {
                els.searchInput.value = '';
                els.searchInput.blur();
                currentPlayerFilter = 'all';
                currentCategory = 'all';
                renderGames();
            }
        });

        // --- Modal Management ---

        function openGameModal(id = null, event = null) {
            if (event) event.stopPropagation();

            const idInput = document.getElementById('game-id');
            const nameInput = document.getElementById('game-name');
            const urlInput = document.getElementById('game-url');
            const imageInput = document.getElementById('game-image');
            const categoryInput = document.getElementById('game-category');
            const deleteBtn = document.getElementById('btn-delete');
            const titleEl = document.getElementById('modal-title');

            const defaultCategories = ['action', 'puzzle', 'rpg', 'shooter', 'sports', 'strategy', 'casual', 'retro'];
            const allUsedCategories = new Set(games.map(g => g.category).filter(Boolean));
            
            let optionsHtml = `<option value="">未分類</option>`;
            
            defaultCategories.forEach(cat => {
                optionsHtml += `<option value="${cat}">${CATEGORY_LABELS[cat]}</option>`;
            });
            
            allUsedCategories.forEach(cat => {
                if (!defaultCategories.includes(cat)) {
                    optionsHtml += `<option value="${escapeHtml(cat)}">${escapeHtml(cat)}</option>`;
                }
            });
            
            optionsHtml += `<option value="__new__">＋ 新規カテゴリー...</option>`;
            
            categoryInput.innerHTML = optionsHtml;

            if (id !== null) {
                const game = games.find(g => g.id == id);
                if (!game) return;
                titleEl.textContent = 'ゲームを編集';
                idInput.value = game.id;
                nameInput.value = game.name;
                urlInput.value = game.url;
                imageInput.value = (game.image && !game.image.startsWith('data:')) ? game.image : '';
                const existingOptions = Array.from(categoryInput.options).map(o => o.value);
                if (game.category && !existingOptions.includes(game.category)) {
                    categoryInput.value = '__new__';
                    const newInput = document.getElementById('game-category-new');
                    newInput.style.display = 'block';
                    newInput.value = game.category;
                } else {
                    categoryInput.value = game.category || '';
                    document.getElementById('game-category-new').style.display = 'none';
                    document.getElementById('game-category-new').value = '';
                }
                document.getElementById('game-players-min').value = game.playersMin || '';
                document.getElementById('game-players-max').value = game.playersMax || '';
                deleteBtn.style.display = 'flex';
                deleteBtn.onclick = () => deleteGame(id);
            } else {
                titleEl.textContent = 'ゲームを追加';
                idInput.value = '';
                nameInput.value = '';
                urlInput.value = '';
                imageInput.value = '';
                categoryInput.value = '';
                document.getElementById('game-category-new').style.display = 'none';
                document.getElementById('game-category-new').value = '';
                document.getElementById('game-players-min').value = '';
                document.getElementById('game-players-max').value = '';
                deleteBtn.style.display = 'none';
            }

            els.gameModal.classList.add('active');
            setTimeout(() => nameInput.focus(), 100);
        }

        function closeGameModal() {
            els.gameModal.classList.remove('active');
            if (focusedCardIndex >= 0) {
                const cards = document.querySelectorAll('.game-card:not(.add-card)');
                if (cards[focusedCardIndex]) cards[focusedCardIndex].focus();
            }
        }

        function saveGame() {
            const idStr = document.getElementById('game-id').value;
            const name = document.getElementById('game-name').value.trim();
            const url = document.getElementById('game-url').value.trim();
            let category = document.getElementById('game-category').value;
            if (category === '__new__') {
                category = document.getElementById('game-category-new').value.trim();
            }
            let image = document.getElementById('game-image').value.trim();

            const playersMin = document.getElementById('game-players-min').value;
            const playersMax = document.getElementById('game-players-max').value;

            if (!name || !url) {
                showToast('タイトルとURLは必須項目です', 'warning');
                return;
            }

            if (idStr) {
                const id = parseInt(idStr, 10);
                const index = games.findIndex(g => g.id == id);
                if (index !== -1) {
                    if (!image) {
                        image = (games[index].name !== name) ? generatePlaceholderImage(name) : games[index].image;
                    }
                    const updatedGame = { 
                        ...games[index], 
                        id, name, url, image, category, playersMin, playersMax,
                        updatedAt: Date.now()
                    };
                    
                    // 編集された場合は位置を維持
                    games[index] = updatedGame;
                    showToast('ゲームを更新しました', 'success');
                }
            } else {
                if (!image) image = generatePlaceholderImage(name);
                const newGame = {
                    id: games.length > 0 ? Math.max(...games.map(g => g.id)) + 1 : 1,
                    name, url, image, category, playersMin, playersMax,
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                    isPinned: false
                };
                
                // 新規ゲームを先頭（ピン留めの下）に追加
                let insertIndex = 0;
                while (insertIndex < games.length && games[insertIndex].isPinned) {
                    insertIndex++;
                }
                games.splice(insertIndex, 0, newGame);
                
                showToast('ゲームを追加しました', 'success');
            }

            renderGames();
            closeGameModal();
            saveGamesToServer();
        }

        function deleteGame(id) {
            const game = games.find(g => g.id == id);
            if (game) {
                games = games.filter(g => g.id !== id);
                renderGames();
                closeGameModal();
                saveGamesToServer();
                showToast('ゲームを削除しました', 'success');
            }
        }

        function renderSettingsCategories() {
            const container = document.getElementById('settings-category-list');
            const categories = new Set(games.map(g => g.category).filter(Boolean));

            if (categories.size === 0) {
                container.innerHTML = '<span style="color:#666; font-size:12px;">現在使用されているカテゴリーはありません。</span>';
                return;
            }

            let html = '';
            categories.forEach(cat => {
                const label = CATEGORY_LABELS[cat] || cat;
                const safeCat = escapeHtml(cat).replace(/'/g, "\\'");
                html += `
                    <div class="category-manage-chip">
                        <span>${escapeHtml(label)}</span>
                        <button type="button" title="削除" onclick="App.deleteCategory('${safeCat}')">×</button>
                    </div>
                `;
            });
            container.innerHTML = html;
        }

        function deleteCategory(cat) {
            const label = CATEGORY_LABELS[cat] || cat;
            
            let isUpdated = false;
            games = games.map(g => {
                if (g.category === cat) {
                    isUpdated = true;
                    return { ...g, category: '', updatedAt: Date.now() };
                }
                return g;
            });

            if (isUpdated) {
                saveGamesToServer(); 
                renderGames();       
            }

            if (currentCategory === cat) {
                currentCategory = 'all';
                renderGames();
            }

            renderSettingsCategories(); 
            showToast(`カテゴリー「${label}」を削除しました`, 'success');
        }

        // --- Settings Management (Local & Server) ---

        function openSettings() {
            // Local Config
            const currentSize = localConfig.gridSize || '240px';
            const sizeSelect = document.getElementById('setting-grid-size');
            const sizeCustom = document.getElementById('setting-grid-size-custom');
            let sizeExists = Array.from(sizeSelect.options).some(opt => opt.value === currentSize);
            
            if (sizeExists) {
                sizeSelect.value = currentSize;
                sizeCustom.style.display = 'none';
            } else {
                sizeSelect.value = 'custom';
                sizeCustom.style.display = 'block';
                sizeCustom.value = parseInt(currentSize) || 240;
            }

            document.getElementById('setting-clock-format').value = localConfig.clockFormat || '24h';
            document.getElementById('setting-accent-color').value = localConfig.accentColor || '#00e6e6';
            document.getElementById('setting-border-radius').value = localConfig.borderRadius || '8px';
            document.getElementById('setting-card-gap').value = localConfig.cardGap || '20px';
            
            document.getElementById('setting-show-title').checked = localConfig.showTitle ?? true;
            document.getElementById('setting-new-tab').checked = localConfig.openInNewTab ?? true;
            document.getElementById('setting-animations').checked = localConfig.enableAnimations ?? true;
            document.getElementById('setting-light-mode').checked = localConfig.isLightMode ?? false;

            // Server Config
            document.getElementById('setting-bg-image').value = serverConfig.bgImage || '';

            renderSettingsCategories();
            els.settingsModal.classList.add('active');
            loadServerBackups();

        }

        function closeSettings() {
            els.settingsModal.classList.remove('active');
        }

        function saveSettings() {
            // ローカル（個人）設定の保存
            let newSize = document.getElementById('setting-grid-size').value;
            if (newSize === 'custom') {
                const customVal = document.getElementById('setting-grid-size-custom').value;
                newSize = customVal ? `${customVal}px` : '240px';
            }

            localConfig = {
                gridSize: newSize,
                clockFormat: document.getElementById('setting-clock-format').value,
                accentColor: document.getElementById('setting-accent-color').value,
                borderRadius: document.getElementById('setting-border-radius').value,
                cardGap: document.getElementById('setting-card-gap').value,
                showTitle: document.getElementById('setting-show-title').checked,
                openInNewTab: document.getElementById('setting-new-tab').checked,
                enableAnimations: document.getElementById('setting-animations').checked,
                isLightMode: document.getElementById('setting-light-mode').checked
            };
            localStorage.setItem('launcher_local_config', JSON.stringify(localConfig));

            // サーバー（全体）設定の保存
            serverConfig = {
                ...serverConfig,
                bgImage: document.getElementById('setting-bg-image').value.trim()
            };

            saveConfigToServer();
            applyConfig();
            closeSettings();
        }

        function applyConfig() {
            const root = document.documentElement;

            // Apply Local Config
            root.style.setProperty('--grid-min-width', localConfig.gridSize);
            root.style.setProperty('--focus-color', localConfig.accentColor);
            root.style.setProperty('--focus-color-rgb', hexToRgb(localConfig.accentColor));
            root.style.setProperty('--card-radius', localConfig.borderRadius);
            root.style.setProperty('--grid-gap', localConfig.cardGap);
            root.style.setProperty('--hover-scale', localConfig.enableAnimations ? '1.04' : '1.0');
            document.body.classList.toggle('hide-titles', !localConfig.showTitle);
            document.body.classList.toggle('light-mode', localConfig.isLightMode === true);
            
            // Apply Server Config
            document.body.style.backgroundImage = serverConfig.bgImage ? `url('${serverConfig.bgImage}')` : 'none';
        }

        // --- Data Management ---

        function exportData() {
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
        }

        function handleGridSizeChange() {
            const val = document.getElementById('setting-grid-size').value;
            document.getElementById('setting-grid-size-custom').style.display = (val === 'custom') ? 'block' : 'none';
        }

        function importData(event) {
            const file = event.target.files[0];
            if (!file) return;

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
        }

        async function loadServerBackups() {
            const select = document.getElementById('server-backup-select');
            if(!select) return;
            select.innerHTML = '<option value="">読込中...</option>';
            try {
                const res = await fetch('./manage_backups.php?action=list');
                const data = await res.json();
                if (data.status === 'success') {
                    if (data.backups.length === 0) {
                        select.innerHTML = '<option value="">バックアップがありません</option>';
                    } else {
                        let html = '<option value="">復元するバックアップを選択...</option>';
                        data.backups.forEach(b => {
                            const dateStr = new Date(b.time * 1000).toLocaleString();
                            const sizeKb = Math.round(b.size / 1024);
                            html += `<option value="${b.filename}">${dateStr} (${sizeKb}KB)</option>`;
                        });
                        select.innerHTML = html;
                    }
                } else {
                    select.innerHTML = '<option value="">読み込み失敗</option>';
                }
            } catch(e) {
                select.innerHTML = '<option value="">通信エラー</option>';
            }
        }

        async function createServerBackup() {
            try {
                const res = await fetch('./manage_backups.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'create' })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    showToast(data.message, 'success');
                    loadServerBackups();
                } else {
                    showToast(data.message || '作成失敗', 'error');
                }
            } catch(e) {
                showToast('通信エラー', 'error');
            }
        }

        async function restoreServerBackup() {
            const select = document.getElementById('server-backup-select');
            const filename = select.value;
            if (!filename) {
                showToast('復元するバックアップを選択してください', 'warning');
                return;
            }
            try {
                const res = await fetch('./manage_backups.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'restore', filename: filename })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    showToast(data.message, 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showToast(data.message || '復元失敗', 'error');
                }
            } catch(e) {
                showToast('通信エラー', 'error');
            }
        }

        async function deleteServerBackup() {
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
        }

        function updateClock() {
            // 時計機能は削除されているが、互換性のために残す
        }

        // --- Initialization ---

        async function init() {
            els.grid = document.getElementById('game-grid');
            const chatMsgInput = document.getElementById('chat-message');
            if (chatMsgInput) {
                chatMsgInput.addEventListener('keydown', e => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendChatMessage();
                        chatMsgInput.style.height = 'auto';
                    }
                });
                chatMsgInput.addEventListener('input', function() {
                    this.style.height = 'auto';
                    const maxH = window.innerHeight * 0.5;
                    const newHeight = Math.min(this.scrollHeight, maxH);
                    this.style.height = newHeight + 'px';
                    this.style.overflowY = this.scrollHeight > maxH ? 'auto' : 'hidden';
                });
            }
            setupShareDragAndDrop();
            els.gameModal = document.getElementById('game-modal');
            els.settingsModal = document.getElementById('settings-modal');
            els.searchInput = document.getElementById('search-input');

            try {
                const res = await fetch('./config.json?t=' + Date.now());
                if (res.ok) {
                    const loadedConfig = await res.json();
                    serverConfig = { ...DEFAULT_SERVER_CONFIG, ...loadedConfig };
                }
            } catch (e) {
                console.warn('Config load failed, using defaults');
                const localBackup = localStorage.getItem('config_backup');
                if (localBackup) serverConfig = { ...DEFAULT_SERVER_CONFIG, ...JSON.parse(localBackup) };
            }
            applyConfig();

            // Load Games
            try {
                const res = await fetch('./games.json?t=' + Date.now());
                if (res.ok) {
                    games = await res.json();
                }
            } catch (e) {
                console.warn('Games load failed');
                const localGames = localStorage.getItem('games_backup');
                if (localGames) {
                    games = JSON.parse(localGames);
                    showToast('サーバーから読み込めなかったため、ローカルバックアップを復元しました', 'warning');
                }
            }

            renderGames();

            // Auto Recovery Logic
            const localGamesStr = localStorage.getItem('games_backup');
            if (localGamesStr) {
                try {
                    const localGames = JSON.parse(localGamesStr);
                    let localPlayCount = 0;
                    localGames.forEach(g => localPlayCount += (g.playCount || 0));
                    let serverPlayCount = 0;
                    games.forEach(g => serverPlayCount += (g.playCount || 0));
                    if (localPlayCount > serverPlayCount) {
                        console.log('Recovering games from local storage...', localPlayCount, '>', serverPlayCount);
                        games = localGames;
                        saveGamesToServer();
                        showToast('ローカルからプレイ回数データを自動復元しました', 'success');
                        renderGames();
                    }
                } catch(e) {}
            }

            els.searchInput.addEventListener('input', renderGames);

            let mousedownTarget = null;
            window.addEventListener('mousedown', e => {
                mousedownTarget = e.target;
            });

            window.addEventListener('click', e => {
                if (e.target === els.gameModal && mousedownTarget === els.gameModal) closeGameModal();
                if (e.target === els.settingsModal && mousedownTarget === els.settingsModal) closeSettings();
                // Close chat if clicked outside (and not on a chat element or open button)
                const chatSidebar = document.getElementById('chat-sidebar');
                if (chatSidebar.classList.contains('active') && 
                    !chatSidebar.contains(e.target) && 
                    !e.target.closest('.chat-btn')) {
                    if (mousedownTarget && !chatSidebar.contains(mousedownTarget) && !mousedownTarget.closest('.chat-btn')) {
                        closeChat();
                    }
                }
                
                const shareSidebar = document.getElementById('share-sidebar');
                if (shareSidebar.classList.contains('active') && 
                    !shareSidebar.contains(e.target) && 
                    !e.target.closest('.share-btn')) {
                    if (mousedownTarget && !shareSidebar.contains(mousedownTarget) && !mousedownTarget.closest('.share-btn')) {
                        closeShare();
                    }
                }
            });

            startAutoReload();
        }

        async function startAutoReload() {
            try {
                const res = await fetch('./check_timestamp.php?t=' + Date.now());
                if (res.ok) {
                    serverTimestamps = await res.json();
                }
            } catch(e) {}

            setInterval(async () => {
                if (isSaving) return;
                try {
                    const res = await fetch('./check_timestamp.php?t=' + Date.now());
                    if (!res.ok) return;
                    const ts = await res.json();
                    
                    if (serverTimestamps) {
                        if (ts.games !== serverTimestamps.games || ts.config !== serverTimestamps.config) {
                            console.log('Data changed remotely. Soft reloading...');
                            let shouldRender = false;
                            if (ts.games !== serverTimestamps.games) {
                                const gRes = await fetch('./games.json?t=' + Date.now());
                                if (gRes.ok) { games = await gRes.json(); shouldRender = true; }
                            }
                            if (ts.config !== serverTimestamps.config) {
                                const cRes = await fetch('./config.json?t=' + Date.now());
                                if (cRes.ok) { const loadedConfig = await cRes.json(); serverConfig = { ...DEFAULT_SERVER_CONFIG, ...loadedConfig }; applyConfig(); shouldRender = true; }
                            }
                            if (shouldRender) { renderGames(); renderFilters(); }
                        }
                    } else {
                        serverTimestamps = ts;
                    }
                } catch(e) {}
            }, 3000);

            // 1分ごとに表示を更新して「何分前アクティブ」の時間を最新に保つ
            setInterval(() => {
                renderGames();
            }, 60000);

            // Chat polling (start after games are loaded)
            fetchChat();
            setInterval(fetchChat, 3000);
            fetchShare();
            setInterval(fetchShare, 3000);
            document.addEventListener('visibilitychange', () => {
                if (!document.hidden) {
                    fetchChat();
                }
            });
        }

        function handleCategoryChange(select) {
            const newInput = document.getElementById('game-category-new');
            if (select.value === '__new__') {
                newInput.style.display = 'block';
                newInput.focus();
            } else {
                newInput.style.display = 'none';
                newInput.value = '';
            }
        }

        function toggleRanking() {
            isRankingActive = !isRankingActive;
            renderGames();
        }

        async function fetchShare() {
            try {
                const res = await fetch('./share.json?t=' + Date.now());
                if (res.ok) {
                    const newMessages = await res.json();
                    if (JSON.stringify(newMessages) !== JSON.stringify(shareMessages)) {
                        shareMessages = newMessages;
                        initialShareLoaded = true;
                        renderShare();
                    } else {
                        initialShareLoaded = true;
                    }
                }
            } catch (e) {
                console.error(e);
            }
        }

        function renderShare() {
            const container = document.getElementById('share-messages');
            if (!container) return;
            
            if (shareMessages.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: #888; font-size: 13px; margin-top: 20px;">まだ投稿はありません</div>';
                return;
            }

            let html = '';
            shareMessages.forEach(msg => {
                const timeStr = new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                const name = msg.name || '名無しさん';
                let gameHtml = '';
                if (msg.gameId) {
                    const game = games.find(g => g.id == msg.gameId);
                    if (game) {
                        gameHtml = `<div class="chat-message-game" onclick="App.openChatGame(${game.id})">?? ${escapeHtml(game.name)}</div>`;
                    }
                }
                
                html += `
                    <div class="chat-message-item" id="share-msg-${msg.id}">
                        <div class="chat-message-header" style="display: flex; justify-content: space-between; font-size: 11px; color: #888; margin-bottom: 3px; align-items: center;">
                            <div>
                                <span class="chat-message-name">${escapeHtml(name)}</span>
                                
                                <span>${timeStr}</span>
                            </div>
                            <button onclick="App.deleteShareMessage(${msg.timestamp})" title="削除" style="background: none; border: none; color: #ff5252; cursor: pointer; font-size: 14px; padding: 0 4px; opacity: 0.6;">×</button>
                        </div>
                        ${gameHtml}
                        ${msg.imageUrl ? `<div style="margin-top: 8px;"><a href="${escapeHtml(msg.imageUrl)}" target="_blank"><img src="${escapeHtml(msg.imageUrl)}" style="max-width: 100%; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2);" alt="Image"></a></div>` : ''}
                        ${(() => { let msgText = msg.message || ''; if (msgText === '') return ''; if (msgText.toLowerCase().startsWith('/a')) { return `<div class="chat-message-text aa-font">${escapeHtml(msgText.replace(/^\/a(?:\r?\n| )?/i, ''))}</div>`; } return `<div class="chat-message-text">${escapeHtml(msgText)}</div>`; })()}
                    </div>
                `;
            });
            container.innerHTML = html;
            container.scrollTop = container.scrollHeight;
        }

        async function deleteShareMessage(timestamp) {
            try {
                const res = await fetch('./post_share.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'delete', timestamp: timestamp, clientId: myClientId })
                });
                if (res.ok) {
                    fetchShare();
                } else {
                    showToast('削除失敗', 'error');
                }
            } catch(e) {
                showToast('通信エラー', 'error');
            }
        }

        async function deleteChatMessage(timestamp) {
            try {
                const res = await fetch('./post_chat.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'delete', timestamp: timestamp, clientId: myClientId })
                });
                if (res.ok) {
                    fetchChat();
                } else {
                    showToast('削除失敗', 'error');
                }
            } catch(e) {
                showToast('通信エラー', 'error');
            }
        }

        function openShare() {
            document.getElementById('share-name').value = document.getElementById('chat-name').value || localStorage.getItem('chat_name') || '';
            
            const shareSelect = document.getElementById('share-game-select');
            let options = '<option value="">ゲーム指定なし</option>';
            games.forEach(g => {
                options += `<option value="${g.id}">${escapeHtml(g.name)}</option>`;
            });
            shareSelect.innerHTML = options;
            
            document.getElementById('share-message').value = '';
            clearShareImage();
            document.getElementById('share-sidebar').classList.add('active');
        }

        function closeShare() {
            document.getElementById('share-sidebar').classList.remove('active');
        }
        
        function handleShareImageSelect() {
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
        }
        
        function clearShareImage() {
            document.getElementById('share-image').value = '';
            document.getElementById('share-image-preview-container').style.display = 'none';
            document.getElementById('share-message').style.paddingRight = '10px';
        }
        
        function setupShareDragAndDrop() {
            const dropZone = document.getElementById('share-message');
            const fileInput = document.getElementById('share-image');
            if(!dropZone || !fileInput) return;
            dropZone.addEventListener('dragover', e => {
                e.preventDefault();
                dropZone.style.background = 'rgba(255,255,255,0.05)';
            });
            dropZone.addEventListener('dragleave', e => {
                e.preventDefault();
                dropZone.style.background = '';
            });
            dropZone.addEventListener('drop', e => {
                e.preventDefault();
                dropZone.style.background = '';
                if(e.dataTransfer.files && e.dataTransfer.files[0]) {
                    if(e.dataTransfer.files[0].type.startsWith('image/')) {
                        fileInput.files = e.dataTransfer.files;
                        handleShareImageSelect();
                    }
                }
            });
        }

        async function submitShare() {
            const nameInput = document.getElementById('share-name');
            const messageInput = document.getElementById('share-message');
            const imageInput = document.getElementById('share-image');
            const gameSelect = document.getElementById('share-game-select');
            const btn = document.getElementById('share-submit-btn');
            
            const name = nameInput.value.trim() || '名無しさん';
            const message = messageInput.value.trim();
            const file = imageInput.files[0];
            const gameId = gameSelect.value ? parseInt(gameSelect.value, 10) : null;
            
            if (!message && !file) {
                showToast('メッセージまたは画像を入力してください', 'error');
                return;
            }
            if (message.length > 300) {
                showToast('最大300文字です', 'error');
                return;
            }
            
            btn.disabled = true;
            btn.innerText = '送信中...';
            
            // Optimistic update
            const tempMsg = {
                id: 'temp_share_' + Date.now(),
                name: name,
                message: message,
                gameId: gameId,
                timestamp: Date.now(),
                clientId: myClientId,
                imageUrl: file ? URL.createObjectURL(file) : null
            };
            shareMessages.push(tempMsg);
            renderShare();
            
            const formData = new FormData();
            formData.append('name', name);
            formData.append('message', message);
            formData.append('clientId', myClientId);
            formData.append('isShare', 'true');
            if (gameId) formData.append('gameId', gameId);
            if (file) {
                formData.append('image', file);
            }
            
            try {
                const response = await fetch('post_share.php', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    showChatNotification(tempMsg);
                    localStorage.setItem('chat_name', name);
                    document.getElementById('share-name').value = name;
                    const msgInput = document.getElementById('share-message');
                    if (msgInput) msgInput.value = '';
                    clearShareImage();
                    
                    fetchShare();
                } else {
                    showToast('エラー: ' + data.message, 'error');
                }
            } catch (e) {
                showToast('通信エラー', 'error');
            } finally {
                btn.disabled = false;
                btn.innerText = '投稿する';
            }
        }

        return {
            init,
            openGameModal, closeGameModal, saveGame, deleteGame, deleteCategory,
            openSettings, closeSettings, saveSettings, exportData, importData, handleGridSizeChange,
            setCategory, setPlayerFilter, handleCategoryChange, togglePin, toggleRanking,
            handleCategoryDragStart, handleCategoryDragOver, handleCategoryDrop, handleCategoryDragEnd,
            openChat, closeChat, sendChatMessage, openChatGame, deleteChatMessage,
            loadServerBackups, createServerBackup, restoreServerBackup, deleteServerBackup,
            openShare, closeShare, submitShare, handleShareImageSelect, clearShareImage, deleteShareMessage
        };
    })();

    document.addEventListener('DOMContentLoaded', App.init);
    
