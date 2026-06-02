import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update .game-card CSS
old_game_card_css = """        .game-card {
            position: relative;
            background-color: var(--card-bg);
            border-radius: var(--card-radius);
            cursor: pointer;
            overflow: hidden;
            border: 2px solid transparent;
            transition: all var(--transition-normal) cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            display: flex;
            flex-direction: column;
            height: 100%;
            backdrop-filter: blur(8px);
            outline: none;
        }"""

new_game_card_css = """        .game-card {
            position: relative;
            background-color: var(--card-bg);
            border-radius: var(--card-radius);
            cursor: pointer;
            overflow: hidden;
            border: 2px solid transparent;
            transition: all var(--transition-normal) cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            display: block;
            height: 100%;
            backdrop-filter: blur(8px);
            outline: none;
        }"""
content = content.replace(old_game_card_css, new_game_card_css)

# 2. Update .game-card img CSS
old_img_css = """        .game-card img {
            width: 100%;
            aspect-ratio: 16 / 9;
            object-fit: cover;
            pointer-events: none;
            flex-grow: 1;
            background: linear-gradient(135deg, #2a2a2a, #1a1a1a);
            transition: opacity 0.3s;
        }"""

new_img_css = """        .game-card img {
            width: 100%;
            aspect-ratio: 16 / 9;
            object-fit: cover;
            pointer-events: none;
            display: block;
            background: linear-gradient(135deg, #2a2a2a, #1a1a1a);
            transition: transform 0.4s ease, opacity 0.3s;
        }
        .game-card:hover img, .game-card.focused img {
            transform: scale(1.05);
        }"""
content = content.replace(old_img_css, new_img_css)


# 3. Update title-bar and card-category CSS
old_title_css = """        .title-bar {
            background: linear-gradient(to top, rgba(0,0,0,0.9), rgba(0,0,0,0.6));
            padding: 7px 12px;
            font-size: 13px;
            font-weight: 600;
            text-align: center;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            color: white;
            border-top: 1px solid rgba(255,255,255,0.05);
        }

        .card-category {
            font-size: 10px;
            color: #aaa;
            text-align: center;
            padding: 4px 12px;
            background: rgba(0,0,0,0.3);
            border-top: 1px solid rgba(255,255,255,0.03);
        }"""

new_title_css = """        .card-info-overlay {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            background: linear-gradient(to top, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.6) 50%, transparent 100%);
            padding: 30px 60px 10px 12px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            gap: 2px;
            pointer-events: none;
        }
        .title-bar {
            font-size: 15px;
            font-weight: 700;
            text-align: left;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            color: white;
            text-shadow: 0 2px 4px rgba(0,0,0,0.9);
        }

        .card-category {
            font-size: 11px;
            color: #ddd;
            text-align: left;
            text-shadow: 0 1px 3px rgba(0,0,0,0.9);
            font-weight: 500;
        }"""
content = content.replace(old_title_css, new_title_css)

# 4. Light mode adjustments (remove unnecessary ones, or fix them)
# Let's just remove the light mode specific category styling since it's an overlay now
old_light_cat = """        body.light-mode .card-category {
            background: rgba(255,255,255,0.5);
            color: #555;
            border-top: 1px solid rgba(0,0,0,0.05);
        }"""
content = content.replace(old_light_cat, "")

# 5. Modify HTML template in renderGames
old_html_template = """                    <img src="${escapeHtml(imgUrl)}" alt="" loading="lazy" onerror="this.src='${generatePlaceholderImage(game.name)}'" onload="this.classList.add('loaded')">
                    <div class="title-bar" title="${escapeHtml(game.name)}">${escapeHtml(game.name)}</div>
                    ${catHtml}
                `;"""

new_html_template = """                    <img src="${escapeHtml(imgUrl)}" alt="" loading="lazy" onerror="this.src='${generatePlaceholderImage(game.name)}'" onload="this.classList.add('loaded')">
                    <div class="card-info-overlay">
                        <div class="title-bar" title="${escapeHtml(game.name)}">${escapeHtml(game.name)}</div>
                        ${catHtml}
                    </div>
                `;"""
content = content.replace(old_html_template, new_html_template)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)

