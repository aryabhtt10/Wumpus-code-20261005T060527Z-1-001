import pygame
import math
import os

from config import *
from core.enemy import SuperBat


class GameRenderer:
    def __init__(self, engine):
        self.engine = engine
        # Load all text files from assets/texts/
        self.texts_dir = os.path.join('assets', 'texts')
        self.menu_controls = self._load_text_lines('menu_controls.txt')
        self.menu_scoring = self._load_text_lines('menu_scoring.txt')
        self.handbook_instructions = self._load_text_lines('handbook_instructions.txt')
        self.handbook_stats = self._load_text_lines('handbook_stats.txt')
        self.handbook_keybinds = self._load_text_lines('handbook_keybinds.txt')
        self.score_breakdown_template = self._load_text_file('gameover_score_breakdown.txt')

    def _load_text_lines(self, filename):
        """Load a text file and return as list of lines."""
        filepath = os.path.join(self.texts_dir, filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    # Return lines while preserving empty lines
                    return [line.rstrip() for line in f.readlines()]
        except Exception as e:
            print(f"Warning: Could not load {filepath}: {e}")
        return []

    def _load_text_file(self, filename):
        """Load a text file and return as single string (for templates)."""
        filepath = os.path.join(self.texts_dir, filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Warning: Could not load {filepath}: {e}")
        return ""

    def apply_background_blur(self):
        temp_surf = self.engine.screen.copy()
        small_surf = pygame.transform.smoothscale(temp_surf, (10, 10))
        blurred_surf = pygame.transform.smoothscale(small_surf, (WIDTH, HEIGHT))
        self.engine.screen.blit(blurred_surf, (0, 0))

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            if '\n' in word:
                parts = word.split('\n')
                for idx, part in enumerate(parts):
                    test_line = ' '.join(current_line + [part])
                    w, _ = font.size(test_line)
                    if w > max_width and current_line:
                        lines.append(' '.join(current_line))
                        current_line = [part]
                    else:
                        current_line.append(part)
                    if idx < len(parts) - 1:
                        lines.append(' '.join(current_line))
                        current_line = []
            else:
                test_line = ' '.join(current_line + [word])
                w, _ = font.size(test_line)
                if w > max_width:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
                        current_line = []
                else:
                    current_line.append(word)
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def draw(self):
        engine = self.engine
        if engine.state == "MENU":
            engine.screen.fill(C_BG)

            title = engine.big_font.render("HUNT THE WUMPUS", True, C_GOLD)
            engine.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

            t1 = engine.font.render("Press 1 for EASY (Less mobs)", True, C_TEXT)
            t2 = engine.font.render("Press 2 for MEDIUM (Normal)", True, C_TEXT)
            t3 = engine.font.render("Press 3 for HARD (More mobs)", True, C_TEXT)
            engine.screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, 160))
            engine.screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, 200))
            engine.screen.blit(t3, (WIDTH // 2 - t3.get_width() // 2, 240))

            # Draw controls from external file
            if self.menu_controls:
                for i, c in enumerate(self.menu_controls):
                    if c == "CONTROLS:":
                        ct = engine.font.render(c, True, (255, 200, 50))
                        engine.screen.blit(ct, (40, 310 + i * 30))
                    elif c.strip():  # Only render non-empty lines
                        ct = engine.sub_font.render(c, True, (150, 150, 150))
                        engine.screen.blit(ct, (40, 310 + i * 30))
            else:
                # Fallback controls
                ctrls = [
                    "CONTROLS:",
                    "WASD - Move",
                    "SHIFT + WASD - Shoot Normal",
                    "CTRL + WASD - Shoot Explosive",
                    "Q + WASD - Shoot TNT",
                    "E - Open Shop"
                ]
                for i, c in enumerate(ctrls):
                    if c == "CONTROLS:":
                        ct = engine.font.render(c, True, (255, 200, 50))
                        engine.screen.blit(ct, (40, 310 + i * 30))
                    else:
                        ct = engine.sub_font.render(c, True, (150, 150, 150))
                        engine.screen.blit(ct, (40, 310 + i * 30))

            # Draw scoring from external file
            if self.menu_scoring:
                for i, s in enumerate(self.menu_scoring):
                    if s == "SCORING:":
                        st = engine.font.render(s, True, (255, 200, 50))
                        engine.screen.blit(st, (300, 310 + i * 30))
                    elif s.strip():  # Only render non-empty lines
                        st = engine.sub_font.render(s, True, (150, 200, 150))
                        engine.screen.blit(st, (300, 310 + i * 30))
            else:
                # Fallback scoring
                scores = [
                    "SCORING:",
                    "Number of Turns = +1",
                    "Gold Coins = +1",
                    "Number of Arrows = +5",
                    "Kill Wumpus = +50"
                ]
                for i, s in enumerate(scores):
                    if s == "SCORING:":
                        st = engine.font.render(s, True, (255, 200, 50))
                        engine.screen.blit(st, (300, 310 + i * 30))
                    else:
                        st = engine.sub_font.render(s, True, (150, 200, 150))
                        engine.screen.blit(st, (300, 310 + i * 30))

            hs_title = engine.font.render("TOP SCORES:", True, (255, 200, 50))
            engine.screen.blit(hs_title, (550, 310))
            if not getattr(engine, 'high_scores', []):
                hst = engine.sub_font.render("No scores yet!", True, (150, 150, 150))
                engine.screen.blit(hst, (550, 340))
            else:
                for i, hs in enumerate(engine.high_scores):
                    name = hs.get("name", "Unknown")
                    score = hs.get("score", 0)
                    cave = hs.get("cave", "MEDIUM")
                    hst = engine.sub_font.render(f"{i+1}. {name} - {score} pts ({cave})", True, (255, 255, 200))
                    engine.screen.blit(hst, (550, 340 + i * 28))

            pygame.display.flip()
            return

        room = engine.cave.get(engine.current_room_id)
        if room:
            engine.screen.blit(engine.bg_image, (0, 0))
            overlay_bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay_bg.fill((0, 0, 0, 100))
            engine.screen.blit(overlay_bg, (0, 0))

            room.portal_angle += 3

            portal_tiles = []
            for y in range(ROWS):
                for x in range(COLS):
                    if room.grid[y][x] == 2:
                        portal_tiles.append((x, y))

            for y in range(ROWS):
                for x in range(COLS):
                    rect = (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if room.grid[y][x] == 1:
                        wall_color = C_WALL
                        for px, py in portal_tiles:
                            if (px == 0 and x == 0) or (px == COLS - 1 and x == COLS - 1) or \
                               (py == 0 and y == 0) or (py == ROWS - 1 and y == ROWS - 1):
                                dist = abs(px - x) + abs(py - y)
                                if dist <= 4:
                                    factor = (5 - dist) / 5.0
                                    wall_color = (
                                        min(255, int(C_WALL[0] * (1-factor) + 180 * factor)),
                                        min(255, int(C_WALL[1] * (1-factor) + 50 * factor)),
                                        min(255, int(C_WALL[2] * (1-factor) + 200 * factor))
                                    )
                        pygame.draw.rect(engine.screen, wall_color, rect)
                    elif room.grid[y][x] == 2:
                        color = C_PORTAL if engine.lockdown_timer <= 0 else (50, 20, 50)
                        pygame.draw.rect(engine.screen, color, rect)
                        if engine.lockdown_timer <= 0:
                            center = (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2)
                            r1 = 30 + math.sin(math.radians(room.portal_angle)) * 10
                            r2 = 20 + math.cos(math.radians(room.portal_angle * 1.5)) * 8
                            r3 = 10 + math.sin(math.radians(room.portal_angle * 2.5)) * 5
                            pygame.draw.circle(engine.screen, (180, 100, 255), center, int(r1), 2)
                            pygame.draw.circle(engine.screen, (220, 150, 255), center, int(r2), 2)
                            pygame.draw.circle(engine.screen, (255, 200, 255), center, int(r3), 0)

            for drop in room.gold_drops:
                if not drop['collected']:
                    dist = math.hypot(drop['rect'].centerx - engine.player.rect.centerx, drop['rect'].centery - engine.player.rect.centery)
                    if dist <= engine.light_radius + 20:
                        for i in range(min(5, drop['amount'])):
                            cx = drop['rect'].x + i * 5 + 5
                            cy = drop['rect'].y + i * 5 + 5
                            pygame.draw.circle(engine.screen, (255, 215, 0), (cx, cy), 8)
                            pygame.draw.circle(engine.screen, (200, 150, 0), (cx, cy), 4)

        if engine.current_room_id == engine.wumpus_grid_pos and engine.wumpus.hp > 0:
            engine.wumpus.draw(engine.screen, engine.wumpus_img)

        if engine.player_invincible_timer == 0 or (engine.player_invincible_timer // 4) % 2 == 0:
            engine.player.draw(engine.screen, engine.player_img)

        for enemy in engine.enemies:
            dist = math.hypot(enemy.rect.centerx - engine.player.rect.centerx, enemy.rect.centery - engine.player.rect.centery)
            if dist <= engine.light_radius + 20 or isinstance(enemy, SuperBat):
                enemy.draw(engine.screen)

        for w in engine.combat_manager.active_weapons:
            w.draw(engine.screen, engine.arrow_img if not w.is_tnt else None)

        engine.floating_text_manager.draw(engine.screen, engine.font)

        light_mask = pygame.Surface((WIDTH, HEIGHT))
        light_mask.fill((70, 70, 70))
        for r in range(engine.light_radius, 0, -4):
            val = min(255, 70 + int(185 * (1 - r / engine.light_radius) ** 1.2))
            pygame.draw.circle(light_mask, (val, val, val), engine.player.rect.center, r)
        engine.screen.blit(light_mask, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        engine.transition.draw(engine.screen)

        ui_top_y = HEIGHT - UI_HEIGHT
        pygame.draw.rect(engine.screen, (15, 15, 20), (0, ui_top_y, WIDTH, UI_HEIGHT))
        pygame.draw.line(engine.screen, (120, 50, 180), (0, ui_top_y), (WIDTH, ui_top_y), 4)

        info_text = f"Health: {engine.player.health}/{engine.player.max_health}   |   Gold: {engine.coins}   |   Score: {engine.score}"
        info_surf = engine.font.render(info_text, True, C_TEXT)
        engine.screen.blit(info_surf, (25, ui_top_y + 15))

        if hasattr(engine, 'game_timer'):
            mins = int(engine.game_timer // 60)
            secs = int(engine.game_timer % 60)
            timer_text = f"Time: {mins:02d}:{secs:02d}"
            timer_surf = engine.font.render(timer_text, True, (255, 200, 100))
            engine.screen.blit(timer_surf, (25, ui_top_y + 68))

        ui_txt2 = engine.font.render(
            f"Arrows: {engine.arrows}   |   Explosive: {engine.explosive_arrows}   |   TNT: {engine.tnt}",
            True, (200, 180, 220)
        )
        engine.screen.blit(ui_txt2, (25, ui_top_y + 45))

        info_btn_txt = engine.font.render("[I] Game Info", True, (100, 255, 100))
        btn_rect = pygame.Rect(WIDTH - 350, ui_top_y + 45, 120, 30)
        pygame.draw.rect(engine.screen, (20, 50, 20), btn_rect)
        pygame.draw.rect(engine.screen, (100, 255, 100), btn_rect, 2)
        engine.screen.blit(info_btn_txt, (btn_rect.centerx - info_btn_txt.get_width() // 2, btn_rect.centery - info_btn_txt.get_height() // 2))

        if getattr(engine, 'warning_timer', 0) > 0 and engine.warning_messages:
            warning_lines = engine.warning_messages[-4:]
            warning_font = engine.warning_font
            warning_height = 18 + len(warning_lines) * (warning_font.get_height() + 6)
            warning_width = min(WIDTH - 120, max(warning_font.size(line)[0] for line in warning_lines) + 32)
            warning_surf = pygame.Surface((warning_width, warning_height), pygame.SRCALPHA)
            warning_surf.fill((20, 20, 30, 220))
            pygame.draw.rect(warning_surf, (255, 180, 100), warning_surf.get_rect(), 2)
            for i, line in enumerate(warning_lines):
                warn_txt = warning_font.render(line, True, (255, 230, 160))
                warning_surf.blit(warn_txt, (16, 10 + i * (warning_font.get_height() + 6)))
            engine.screen.blit(warning_surf, ((WIDTH - warning_width) // 2, 80))

        if engine.lockdown_timer > 0:
            fight_txt = engine.font.render(f"LOCKDOWN: {engine.lockdown_timer // FPS}s | WUMPUS HP: {engine.wumpus.hp}", True, (255, 60, 60))
            engine.screen.blit(fight_txt, (WIDTH - 20 - fight_txt.get_width(), ui_top_y + 15))
        elif engine.wumpus.awake:
            dist_x = abs(engine.wumpus_grid_pos[0] - engine.current_room_id[0])
            dist_y = abs(engine.wumpus_grid_pos[1] - engine.current_room_id[1])
            dist = dist_x + dist_y
            status_txt = engine.font.render(f"WUMPUS HP: {engine.wumpus.hp} | CHASING (Dist: {dist})", True, (255, 100, 100))
            engine.screen.blit(status_txt, (WIDTH - 20 - status_txt.get_width(), ui_top_y + 15))

        def wrap_log_lines(messages, font, max_width):
            wrapped = []
            for display_msg, orig_msg in messages:
                for line in display_msg.split('\n'):
                    for wrapped_line in self.wrap_text(line, font, max_width):
                        wrapped.append((wrapped_line, orig_msg))
            return wrapped

        # Prepare messages for the log box. Keep original msg (to detect warnings)
        # but wrap the display text without the '>>>' prefix so warnings render cleanly.
        messages_for_box = []
        for msg in engine.message_log:
            if isinstance(msg, str) and msg.startswith('>>>'):
                display = msg.lstrip('>').strip()
                messages_for_box.append((display, msg))
            else:
                messages_for_box.append((msg, msg))

        log_font = engine.sub_font
        text_box_width = 240
        message_box = pygame.Rect(20, ui_top_y + 90, text_box_width, 110)

        pygame.draw.rect(engine.screen, (20, 20, 30), message_box)
        pygame.draw.rect(engine.screen, (100, 100, 120), message_box, 2)

        msg_title = engine.font.render("Messages", True, (180, 180, 180))
        engine.screen.blit(msg_title, (message_box.left + 8, message_box.top + 4))

        normal_lines = wrap_log_lines(messages_for_box, log_font, text_box_width - 16)[-5:]

        msg_start_y = message_box.top + 28
        line_height = log_font.get_height() + 2
        for i, (text, orig_msg) in enumerate(normal_lines):
            # Yellow for warnings that originated with '>>>', default grey otherwise
            if isinstance(orig_msg, str) and orig_msg.startswith('>>>'):
                color = (255, 220, 100)  # Yellow for warnings
            else:
                color = (150, 150, 160)  # Grey for normal messages
            msg_txt = log_font.render(text, True, color)
            engine.screen.blit(msg_txt, (message_box.left + 8, msg_start_y + (i * line_height)))

        mm_x_start = WIDTH - 200
        mm_y_start = HEIGHT - 160
        cell_w, cell_h = 25, 25
        gap = 5
        for gx in range(MAP_COLS):
            for gy in range(MAP_ROWS):
                if not hasattr(engine, 'cave') or (gx, gy) not in getattr(engine, 'cave', {}):
                    continue
                cx = mm_x_start + gx * (cell_w + gap)
                cy = mm_y_start + gy * (cell_h + gap)

                center_x = cx + cell_w // 2
                center_y = cy + cell_h // 2
                r = cell_w // 2 + 1

                hex_points = []
                for i in range(6):
                    angle_rad = math.radians(60 * i + 30)
                    px = center_x + r * math.cos(angle_rad)
                    py = center_y + r * math.sin(angle_rad)
                    hex_points.append((px, py))
                hex_color = (50, 255, 50) if (gx, gy) == engine.wumpus_seen_room else (120, 100, 180)
                pygame.draw.polygon(engine.screen, hex_color, hex_points, 2)

                if (gx, gy) == engine.current_room_id:
                    pygame.draw.circle(engine.screen, (255, 230, 100), (center_x, center_y), 5)

                if (gx, gy) == engine.wumpus_seen_room:
                    tx = center_x + 5
                    ty = center_y + 4
                    pygame.draw.line(engine.screen, (50, 255, 50), (tx - 3, ty), (tx, ty + 3), 2)
                    pygame.draw.line(engine.screen, (50, 255, 50), (tx, ty + 3), (tx + 4, ty - 4), 2)

        if hasattr(engine, 'secrets'):
            for sec in engine.secrets:
                if sec['type'] == 'row':
                    sy = mm_y_start + sec['index'] * (cell_h + gap) + cell_h // 2
                    sx = mm_x_start - 20
                    pygame.draw.polygon(engine.screen, (150, 50, 255), [(sx, sy - 5), (sx + 10, sy), (sx, sy + 5)])
                else:
                    sx = mm_x_start + sec['index'] * (cell_w + gap) + cell_w // 2
                    sy = mm_y_start - 20
                    pygame.draw.polygon(engine.screen, (150, 50, 255), [(sx - 5, sy), (sx + 5, sy), (sx, sy + 10)])

        if getattr(engine, 'wumpus', None) and engine.wumpus.awake and getattr(engine, 'collapse_stage', 9) < 9:
            if engine.state in ["PLAYING", "TELEPORT_SELECT", "GAMEOVER"]:
                warn_txt = engine.font.render(f"CAVE COLLAPSE IN: {engine.collapse_timer // FPS}s", True, (255, 255, 0))
                engine.screen.blit(warn_txt, (WIDTH // 2 - warn_txt.get_width() // 2, 50))

            if engine.collapse_stage < 4:
                sy = mm_y_start + engine.collapse_stage * (cell_h + gap) + cell_h // 2
                sx = mm_x_start - 20
                pygame.draw.polygon(engine.screen, (255, 255, 0), [(sx, sy - 5), (sx + 10, sy), (sx, sy + 5)])
            else:
                target_x = engine.collapse_stage - 4
                sx = mm_x_start + target_x * (cell_w + gap) + cell_w // 2
                sy = mm_y_start + 4 * (cell_h + gap) + cell_h + 10
                pygame.draw.polygon(engine.screen, (255, 255, 0), [(sx - 5, sy), (sx + 5, sy), (sx, sy - 10)])

        if engine.state == "SHOP":
            self.apply_background_blur()
            engine.shop.draw(engine.screen, engine)

        if engine.state in ["TRIVIA", "PIT_TRIVIA"] and getattr(engine, 'current_q', None):
            self.apply_background_blur()
            overlay = pygame.Surface((WIDTH, HEIGHT))
            if engine.state == "PIT_TRIVIA":
                overlay.set_alpha(180)
                overlay.fill((20, 10, 30))
            else:
                overlay.set_alpha(200)
                overlay.fill((15, 10, 20))
            engine.screen.blit(overlay, (0, 0))

            if engine.state == "PIT_TRIVIA":
                warning_txt = engine.big_font.render("PORTAL MALFUNCTION! YOU FELL INTO A PIT!", True, (255, 60, 60))
                engine.screen.blit(warning_txt, (WIDTH // 2 - warning_txt.get_width() // 2, HEIGHT // 3 - 100))
                t_esc = engine.font.render("Failing this challenge will result in Game Over!", True, (255, 120, 120))
            else:
                t_esc = engine.font.render("Press ESC to exit trivia", True, (150, 150, 150))

            if engine.trivia_item_buying in ["Normal Arrow Pack (30)", "Small Arrow Pack (5)"]:
                q_asked = getattr(engine, 'trivia_questions_asked', 0)
                max_str = getattr(engine, 'trivia_max_consecutive_correct', 0)
                t_title = engine.big_font.render(f"ARROW CHALLENGE: Q: {q_asked}/3 | Streak: {max_str}/2", True, (100, 255, 100))
            else:
                t_title = engine.big_font.render(f"TRIVIA CHALLENGE: {engine.trivia_current_streak}/{engine.trivia_target_streak}", True, (255, 100, 100))

            q_text = f"QUESTION: {engine.current_q['q']}"
            words = q_text.split(' ')
            lines = []
            current_line = []
            max_w = WIDTH - 80
            for word in words:
                test_line = ' '.join(current_line + [word])
                w, _ = engine.font.size(test_line)
                if w > max_w:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
                        current_line = []
                else:
                    current_line.append(word)
            if current_line:
                lines.append(' '.join(current_line))

            engine.screen.blit(t_title, (WIDTH // 2 - t_title.get_width() // 2, HEIGHT // 3 - 50))

            y_offset = HEIGHT // 3 + 40
            line_height = engine.font.get_height() + 5
            for line in lines:
                t_line = engine.font.render(line, True, (180, 200, 255))
                engine.screen.blit(t_line, (WIDTH // 2 - t_line.get_width() // 2, y_offset))
                y_offset += line_height

            engine.screen.blit(t_esc, (WIDTH // 2 - t_esc.get_width() // 2, y_offset + 10))
            y_offset += line_height + 25

            # Hint purchase instruction
            hint_instr = engine.font.render("Press H for a hint (Cost: 1 Gold)", True, (200, 180, 100))
            engine.screen.blit(hint_instr, (WIDTH // 2 - hint_instr.get_width() // 2, y_offset))
            y_offset += line_height + 8

            # If a hint was purchased, display it
            if getattr(engine, 'current_hint', None):
                full_hint = engine.current_hint or ''
                # advance reveal tick and increment revealed character count periodically
                prev_index = getattr(engine, 'hint_reveal_index', 0)
                engine.hint_reveal_tick = getattr(engine, 'hint_reveal_tick', 0) + 1
                REVEAL_SPEED = 2  # frames per character
                if engine.hint_reveal_tick % REVEAL_SPEED == 0 and getattr(engine, 'hint_reveal_index', 0) < len(full_hint):
                    engine.hint_reveal_index = getattr(engine, 'hint_reveal_index', 0) + 1

                # Debug: print when reveal index changes or first frame
                try:
                    if prev_index != engine.hint_reveal_index:
                        print(f"[DEBUG] hint reveal updated: index={engine.hint_reveal_index} / {len(full_hint)} visible='{full_hint[:engine.hint_reveal_index]}'")
                    elif prev_index == 0 and engine.hint_reveal_index == 0:
                        print(f"[DEBUG] hint present but not yet revealed: full_hint='{full_hint}'")
                except Exception:
                    pass

                visible_text = full_hint[:getattr(engine, 'hint_reveal_index', 0)]
                hint_lines = self.wrap_text(visible_text, engine.font, WIDTH - 240)
                for hline in hint_lines:
                    hint_surf = engine.font.render(hline, True, (200, 220, 180))
                    engine.screen.blit(hint_surf, (WIDTH // 2 - hint_surf.get_width() // 2, y_offset))
                    y_offset += engine.font.get_height() + 4
                y_offset += 6

            for i, opt in enumerate(engine.current_q['opts']):
                opt_str = f"[{i+1}] {opt}"
                o_words = opt_str.split(' ')
                o_lines = []
                o_current = []
                max_opt_w = WIDTH - 240
                for o_word in o_words:
                    test_opt = ' '.join(o_current + [o_word])
                    w, _ = engine.font.size(test_opt)
                    if w > max_opt_w:
                        if o_current:
                            o_lines.append(' '.join(o_current))
                            o_current = [o_word]
                        else:
                            o_lines.append(o_word)
                            o_current = []
                    else:
                        o_current.append(o_word)
                if o_current:
                    o_lines.append(' '.join(o_current))

                for o_line in o_lines:
                    o_txt = engine.font.render(o_line, True, (220, 220, 220))
                    engine.screen.blit(o_txt, (120, y_offset))
                    y_offset += line_height
                y_offset += 5

        if engine.state == "WUMPUS_PROMPT":
            self.apply_background_blur()
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((30, 0, 0))
            engine.screen.blit(overlay, (0, 0))
            p_title = engine.big_font.render("WUMPUS ENCOUNTERED!", True, (255, 50, 50))
            p_sub = engine.font.render("[1] Retreat (Requires 5 Gold & Trivia)   |   [2] Stay and fight (Wakes up in 3s)", True, (200, 200, 200))
            engine.screen.blit(p_title, (WIDTH // 2 - p_title.get_width() // 2, HEIGHT // 2 - 50))
            engine.screen.blit(p_sub, (WIDTH // 2 - p_sub.get_width() // 2, HEIGHT // 2 + 20))

        if engine.state in ["GAMEOVER", "VICTORY"]:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(235)
            overlay.fill((10, 8, 15))
            engine.screen.blit(overlay, (0, 0))

            end_color = (255, 60, 60) if engine.state == "GAMEOVER" else (100, 255, 100)
            end_title = "DEFEAT - YOU DIED" if engine.state == "GAMEOVER" else "VICTORY - WUMPUS SLAIN!"
            end_txt = engine.big_font.render(end_title, True, end_color)
            engine.screen.blit(end_txt, (WIDTH // 2 - end_txt.get_width() // 2, 30))

            if engine.state == "GAMEOVER" and getattr(engine, 'death_reason', ''):
                reason_txt = engine.font.render(engine.death_reason, True, (255, 150, 150))
                engine.screen.blit(reason_txt, (WIDTH // 2 - reason_txt.get_width() // 2, 65))

            if not getattr(engine, 'score_saved', False):
                n_turns = engine.turns
                g_coins = engine.coins
                a_arrows = engine.arrows + engine.explosive_arrows
                w_bonus = 50 if engine.state == "VICTORY" else 0
                final_score = 100 - n_turns + g_coins + 5 * a_arrows + w_bonus

                card_rect = pygame.Rect(WIDTH // 2 - 250, 90, 500, 420)
                pygame.draw.rect(engine.screen, (20, 15, 30), card_rect)
                pygame.draw.rect(engine.screen, (150, 80, 255), card_rect, 2)

                breakdown_title = engine.font.render("--- GAME OVERALL SCORE ---", True, (255, 200, 50))
                engine.screen.blit(breakdown_title, (WIDTH // 2 - breakdown_title.get_width() // 2, 105))

                # Use external template for score breakdown
                if self.score_breakdown_template:
                    # Format the template with actual values
                    try:
                        stats_text = self.score_breakdown_template.format(
                            turns=n_turns,
                            gold=g_coins,
                            arrows=a_arrows,
                            arrows_value=5 * a_arrows,
                            wumpus_bonus=w_bonus,
                            final_score=final_score
                        )
                        stats = [line.rstrip() for line in stats_text.split('\n')]
                    except KeyError:
                        # Fallback if template formatting fails
                        stats = [
                            f"• Turns Taken (N)       :  {n_turns}  (-{n_turns} pts)",
                            f"• Gold Coins Left (G)   :  {g_coins}  (+{g_coins} pts)",
                            f"• Arrows Left (A)       :  {a_arrows}  (+{5 * a_arrows} pts)",
                            f"• Wumpus Killed (W)     :  {w_bonus} pts",
                            "",
                            "Equation: 100 - N + G + (5 * A) + W",
                            f"FINAL SCORE             :  {final_score} PTS"
                        ]
                else:
                    # Fallback if template not found
                    stats = [
                        f"• Turns Taken (N)       :  {n_turns}  (-{n_turns} pts)",
                        f"• Gold Coins Left (G)   :  {g_coins}  (+{g_coins} pts)",
                        f"• Arrows Left (A)       :  {a_arrows}  (+{5 * a_arrows} pts)",
                        f"• Wumpus Killed (W)     :  {w_bonus} pts",
                        "",
                        "Equation: 100 - N + G + (5 * A) + W",
                        f"FINAL SCORE             :  {final_score} PTS"
                    ]

                y_offset = 140
                for i, st in enumerate(stats):
                    if not st:  # Skip empty lines
                        y_offset += 5
                        continue
                    color = (100, 255, 100) if "FINAL SCORE" in st else ((200, 200, 220) if st else (150, 150, 150))
                    bold_font = engine.big_font if "FINAL SCORE" in st else engine.font
                    st_surf = bold_font.render(st, True, color)
                    engine.screen.blit(st_surf, (WIDTH // 2 - st_surf.get_width() // 2, y_offset))
                    y_offset += 24

                pygame.draw.line(engine.screen, (100, 80, 150), (WIDTH // 2 - 200, 325), (WIDTH // 2 + 200, 325), 1)

                prompt_txt = engine.font.render("ENTER YOUR NAME FOR LEADERBOARD:", True, (200, 180, 255))
                engine.screen.blit(prompt_txt, (WIDTH // 2 - prompt_txt.get_width() // 2, 345))

                input_rect = pygame.Rect(WIDTH // 2 - 160, 375, 320, 36)
                pygame.draw.rect(engine.screen, (30, 25, 45), input_rect)
                pygame.draw.rect(engine.screen, (150, 100, 255), input_rect, 2)

                cursor = "_" if (pygame.time.get_ticks() // 400) % 2 == 0 else ""
                typed_name = engine.player_name_input + cursor
                name_surf = engine.font.render(typed_name, True, (255, 255, 255))
                engine.screen.blit(name_surf, (input_rect.centerx - name_surf.get_width() // 2, input_rect.centery - name_surf.get_height() // 2))

                sub_txt = engine.font.render("Press ENTER to submit and view high scores", True, (150, 150, 150))
                engine.screen.blit(sub_txt, (WIDTH // 2 - sub_txt.get_width() // 2, 430))
            else:
                lb_title = engine.big_font.render("--- TOP 10 LEADERBOARD ---", True, (255, 215, 0))
                engine.screen.blit(lb_title, (WIDTH // 2 - lb_title.get_width() // 2, 75))

                box_rect = pygame.Rect(50, 115, WIDTH - 100, 360)
                pygame.draw.rect(engine.screen, (25, 20, 35), box_rect)
                pygame.draw.rect(engine.screen, (255, 215, 0), box_rect, 2)

                headers = ["Rank", "Player Name", "Score", "Turns (N)", "Gold (G)", "Arrows (A)", "Wumpus (W)", "Cave"]
                x_positions = [70, 130, 270, 360, 450, 530, 610, 680]

                for h, x in zip(headers, x_positions):
                    h_surf = engine.font.render(h, True, (255, 180, 100))
                    engine.screen.blit(h_surf, (x, 125))

                pygame.draw.line(engine.screen, (150, 120, 255), (60, 150), (WIDTH - 60, 150), 2)

                hs_list = getattr(engine, 'high_scores', [])
                for i in range(10):
                    y_pos = 160 + i * 26
                    if i % 2 == 0:
                        row_bg = pygame.Surface((WIDTH - 120, 22))
                        row_bg.set_alpha(30)
                        row_bg.fill((150, 100, 255))
                        engine.screen.blit(row_bg, (60, y_pos - 2))

                    if i < len(hs_list):
                        item = hs_list[i]
                        row_data = [
                            f"#{i+1}",
                            str(item["name"]),
                            str(item["score"]),
                            str(item["turns"]),
                            str(item["gold"]),
                            str(item["arrows"]),
                            str(item["wumpus_killed"]),
                            str(item["cave"])
                        ]
                    else:
                        row_data = [f"#{i+1}", "---", "---", "---", "---", "---", "---", "---"]

                    for val, x in zip(row_data, x_positions):
                        color = (100, 255, 100) if i == 0 and len(hs_list) > 0 else (240, 240, 240)
                        val_surf = engine.font.render(val, True, color)
                        engine.screen.blit(val_surf, (x, y_pos))

                rst_txt = engine.big_font.render("Press 'R' to Return to Menu", True, (255, 255, 255))
                engine.screen.blit(rst_txt, (WIDTH // 2 - rst_txt.get_width() // 2, 500))

        if engine.state == "TELEPORT_SELECT":
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 50))
            engine.screen.blit(overlay, (0, 0))
            prompt_txt = engine.big_font.render("CLICK A CAVE ON MINIMAP TO TELEPORT!", True, (100, 255, 100))
            engine.screen.blit(prompt_txt, (WIDTH // 2 - prompt_txt.get_width() // 2, HEIGHT // 3))

        if engine.state == "INFO":
            self.apply_background_blur()
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(240)
            overlay.fill((15, 10, 25))
            engine.screen.blit(overlay, (0, 0))

            title_txt = engine.big_font.render("--- ADVENTURER'S HANDBOOK ---", True, (240, 200, 100))
            engine.screen.blit(title_txt, (WIDTH // 2 - title_txt.get_width() // 2, 40))

            tab1_rect = pygame.Rect(60, 110, 210, 40)
            tab2_rect = pygame.Rect(295, 110, 210, 40)
            tab3_rect = pygame.Rect(530, 110, 210, 40)

            t1_bg = (50, 40, 80) if engine.info_tab == "INSTRUCTIONS" else (30, 25, 45)
            t1_border = (180, 100, 255) if engine.info_tab == "INSTRUCTIONS" else (100, 80, 130)
            t1_text_color = (255, 255, 255) if engine.info_tab == "INSTRUCTIONS" else (180, 180, 180)

            t2_bg = (50, 40, 80) if engine.info_tab == "STATS" else (30, 25, 45)
            t2_border = (180, 100, 255) if engine.info_tab == "STATS" else (100, 80, 130)
            t2_text_color = (255, 255, 255) if engine.info_tab == "STATS" else (180, 180, 180)

            t3_bg = (50, 40, 80) if engine.info_tab == "KEYBINDS" else (30, 25, 45)
            t3_border = (180, 100, 255) if engine.info_tab == "KEYBINDS" else (100, 80, 130)
            t3_text_color = (255, 255, 255) if engine.info_tab == "KEYBINDS" else (180, 180, 180)

            pygame.draw.rect(engine.screen, t1_bg, tab1_rect)
            pygame.draw.rect(engine.screen, t1_border, tab1_rect, 2)
            t1_txt = engine.font.render("[1] GAMEPLAY RULES", True, t1_text_color)
            engine.screen.blit(t1_txt, (tab1_rect.centerx - t1_txt.get_width() // 2, tab1_rect.centery - t1_txt.get_height() // 2))

            pygame.draw.rect(engine.screen, t2_bg, tab2_rect)
            pygame.draw.rect(engine.screen, t2_border, tab2_rect, 2)
            t2_txt = engine.font.render("[2] STATS & SPECS", True, t2_text_color)
            engine.screen.blit(t2_txt, (tab2_rect.centerx - t2_txt.get_width() // 2, tab2_rect.centery - t2_txt.get_height() // 2))

            pygame.draw.rect(engine.screen, t3_bg, tab3_rect)
            pygame.draw.rect(engine.screen, t3_border, tab3_rect, 2)
            t3_txt = engine.font.render("[3] KEYBINDS & HELP", True, t3_text_color)
            engine.screen.blit(t3_txt, (tab3_rect.centerx - t3_txt.get_width() // 2, tab3_rect.centery - t3_txt.get_height() // 2))

            content_rect = pygame.Rect(60, 170, WIDTH - 120, HEIGHT - 280)
            pygame.draw.rect(engine.screen, (25, 20, 35), content_rect)
            pygame.draw.rect(engine.screen, (120, 50, 180), content_rect, 2)

            # Use external text files for handbook content
            if engine.info_tab == "INSTRUCTIONS":
                lines = self.handbook_instructions if self.handbook_instructions else [
                    "Welcome to Hunt the Wumpus! Your mission is to locate and defeat the beast.",
                    "",
                    "• Sleeping Beast: Wumpus starts asleep. Entering its room prompts Retreat/Stay.",
                    "  - Retreat: Costs 5 Gold & Trivia. Safely sends you back to your previous room!",
                    "  - Stay/Fail: Wumpus wakes up. You are locked in, and the Wumpus hunts you down!",
                    "",
                    "• Dynamic Pits: Pitch black pits are scattered throughout the cave system.",
                    "  - Pit Chance: 5% on Easy | 8% on Medium | 11% on Hard.",
                    "  - Falling in: Malfunctions portal, consumes 5 Gold & triggers a Trivia Escape.",
                    "  - Safe Start: The first 3 rooms you visit are guaranteed to be 100% pit-free!",
                    "",
                    "• Cave Collapse: 40s after Wumpus wakes up, outer rooms collapse sequentially.",
                    "  - Yellow Arrows: Show collapsing rooms on the minimap. Get out in time!",
                    "",
                    "• Weapons Dealer: Open the shop [E] in safe rooms to buy weapons and upgrades.",
                    "  - Secrets Upgrade: Reveals proximity arrows showing if Wumpus/Bat/Pit is 1 room away.",
                    "",
                    "• Wumpus Secrets: Purchasing a Wumpus hint reveals its grid proximity.",
                    "  - Map Arrows: A purple arrow appears on the top/left margins of your minimap.",
                    "  - Interpretation: The Wumpus lies within 3 columns (for top arrows) or 3 rows",
                    "    (for left arrows) of the indicated line. Multiple hints narrow down its exact room!",
                    "  - Redundancy Block: If you already know the Wumpus's exact room (e.g. from retreat),",
                    "    the shop will block you from buying secrets so you do not waste gold!"
                ]
            elif engine.info_tab == "STATS":
                lines = self.handbook_stats if self.handbook_stats else [
                    "Dungeon Entity Stats, Weapon Specs, & Game Mechanics:",
                    "",
                    "• Wumpus: 30 HP (Easy) | 50 HP (Medium) | 75 HP (Hard). Deals 8 touch damage.",
                    "  - Spawns gold drops every 6s, and spawns new swarms of enemies every 10s.",
                    "",
                    "• Super Bats: 2 majestic golden bats reside in the cave. Smoothly chase you.",
                    "  - Has 5 HP. Defeating it awards 15 pts and permanently clears the hazard.",
                    "  - If it touches you, it picks you up and teleports you to a random safe room.",
                    "",
                    "• Dungeon Spiders: Small spiders (1 HP, 1 touch dmg) | Big spiders (2 HP, 2 touch dmg).",
                    "",
                    "• Arsenal & Damage Specs:",
                    "  - Normal Arrow: Deals 2 DMG to Wumpus, 1 DMG to Spiders/Bats. Direct shot.",
                    "  - Explosive Arrow: 60px radius. Kills 4 big / 6 small spiders. Deals 3 DMG to Wumpus.",
                    "  - TNT: 150px radius. Kills up to 15 spiders in room. Deals 8 DMG to Wumpus.",
                    "",
                    "• Scoring Formula: Score = 100 - Turns + Gold + 5 * Arrows + Wumpus Killed Bonus (50 pts)",
                    "  - Speed Bonus: Complete under 2/5/10 min to get a multiplier on your final score!"
                ]
            else:
                lines = self.handbook_keybinds if self.handbook_keybinds else [
                    "Master the keys to survive the cave hazards:",
                    "",
                    "• W, A, S, D / Arrow Keys  : Move Player around the room",
                    "",
                    "• SHIFT + [W/A/S/D]         : Shoot Normal Arrow (deals 2 damage to Wumpus)",
                    "",
                    "• CTRL + [W/A/S/D]          : Shoot Explosive Arrow (requires Explosive Arrow ammo)",
                    "",
                    "• Q + [W/A/S/D]             : Throw TNT (large explosion, requires TNT ammo)",
                    "",
                    "• E                         : Open Weapons Dealer Shop in safe rooms",
                    "",
                    "• I                         : Open / Close this Adventurer's Handbook",
                    "",
                    "• 1, 2, 3, 4                : Select Trivia Answers in Trivia/Pit prompts",
                    "",
                    "• Click Minimap Cell        : Teleport to selected cave (when Teleport active)",
                    "",
                    "• ESC                       : Exit menus or close prompts",
                    "",
                    "• R                         : Restart game (on GameOver / Victory screens)"
                ]

            wrapped_lines_data = []
            for line in lines:
                sub_lines = self.wrap_text(line, engine.handbook_font, WIDTH - 160)
                for sub in sub_lines:
                    wrapped_lines_data.append((sub, line))

            for idx, (sub_line, orig_line) in enumerate(wrapped_lines_data):
                bullet_color = (240, 240, 245) if "•" in orig_line or "  -" in orig_line else (200, 200, 210)
                if orig_line.startswith("•") or orig_line.startswith("  -"):
                    x_pos = 100 if sub_line != orig_line and not sub_line.startswith("  -") else 80
                    line_surf = engine.handbook_font.render(sub_line, True, (220, 200, 255))
                elif orig_line.startswith("Welcome") or orig_line.startswith("Master") or orig_line.startswith("Dungeon"):
                    x_pos = 80
                    line_surf = engine.handbook_font.render(sub_line, True, (100, 255, 100))
                else:
                    x_pos = 80
                    line_surf = engine.handbook_font.render(sub_line, True, bullet_color)

                line_spacing = 26 if engine.info_tab in ["STATS", "KEYBINDS"] else 20
                y_pos = 190 + idx * line_spacing
                if y_pos < HEIGHT - 120:
                    engine.screen.blit(line_surf, (x_pos, y_pos))

            footer_txt = engine.font.render("Press 'I', ESC, or click outside to return to the game", True, (150, 150, 150))
            engine.screen.blit(footer_txt, (WIDTH // 2 - footer_txt.get_width() // 2, HEIGHT - 85))

        if engine.state == "PAUSED":
            self.apply_background_blur()
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((10, 10, 15))
            engine.screen.blit(overlay, (0, 0))

            title_text = engine.big_font.render("GAME PAUSED", True, C_GOLD)
            engine.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3 - 50))

            options = [
                "[1] Resume Game (or P / ESC)",
                "[2] Return to Main Menu",
                "[3] Restart Level"
            ]

            panel_width = 400
            panel_height = 50
            start_y = HEIGHT // 3 + 30
            spacing = 70

            mx, my = pygame.mouse.get_pos()

            for i, opt in enumerate(options):
                x = WIDTH // 2 - panel_width // 2
                y = start_y + i * spacing
                btn_rect = pygame.Rect(x, y, panel_width, panel_height)

                is_hovered = btn_rect.collidepoint(mx, my)
                bg_color = (25, 25, 35) if is_hovered else (20, 20, 25)
                border_color = (62, 203, 114) if is_hovered else (141, 74, 212)

                pygame.draw.rect(engine.screen, bg_color, btn_rect, border_radius=8)
                pygame.draw.rect(engine.screen, border_color, btn_rect, width=2, border_radius=8)

                text_color = (255, 255, 255) if is_hovered else (200, 200, 210)
                text_surf = engine.font.render(opt, True, text_color)
                engine.screen.blit(text_surf, (btn_rect.centerx - text_surf.get_width() // 2, btn_rect.centery - text_surf.get_height() // 2))

        pygame.display.flip()