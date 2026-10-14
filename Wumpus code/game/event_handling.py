import pygame

from config import FPS, WIDTH, HEIGHT, UI_HEIGHT, MAP_COLS, MAP_ROWS
from systems.trivia import handle_input as handle_trivia_input


def handle_state_event(event, engine):
    if engine.state == "MENU":
        handle_menu_event(event, engine)
    elif engine.state in ["GAMEOVER", "VICTORY"]:
        handle_endgame_event(event, engine)
    elif engine.state == "PLAYING":
        handle_playing_event(event, engine)
    elif engine.state == "INFO":
        handle_info_event(event, engine)
    elif engine.state == "PAUSED":
        handle_paused_event(event, engine)
    elif engine.state == "TELEPORT_SELECT":
        handle_teleport_event(event, engine)
    elif engine.state == "SHOP":
        engine.shop.handle_input(event, engine)
    elif engine.state == "WUMPUS_PROMPT":
        handle_wumpus_prompt_event(event, engine)
    elif engine.state in ["TRIVIA", "PIT_TRIVIA"]:
        handle_trivia_input(event, engine)


def handle_menu_event(event, engine):
    if event.type != pygame.KEYDOWN:
        return

    if event.key in [pygame.K_1, pygame.K_KP1]:
        engine.sound_manager.play("menu select")
        engine.difficulty = "EASY"
        engine.setup_game()
    elif event.key in [pygame.K_2, pygame.K_KP2]:
        engine.sound_manager.play("menu select")
        engine.difficulty = "MEDIUM"
        engine.setup_game()
    elif event.key in [pygame.K_3, pygame.K_KP3]:
        engine.sound_manager.play("menu select")
        engine.difficulty = "HARD"
        engine.setup_game()


def handle_endgame_event(event, engine):
    if not getattr(engine, 'score_saved', False):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_RETURN:
            name_to_save = engine.player_name_input.strip()
            if not name_to_save:
                name_to_save = "Player"
            engine.save_score(name_to_save)
        elif event.key == pygame.K_BACKSPACE:
            engine.player_name_input = engine.player_name_input[:-1]
        else:
            if event.unicode and event.unicode.isprintable() and len(engine.player_name_input) < 15:
                if event.unicode != ",":
                    engine.player_name_input += event.unicode
    else:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            engine.state = "MENU"


def handle_playing_event(event, engine):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_e:
            engine.sound_manager.play("menu change")
            engine.state = "SHOP"
        elif event.key == pygame.K_i:
            engine.sound_manager.play("menu change")
            engine.state = "INFO"
            engine.info_tab = "INSTRUCTIONS"
        elif event.key in [pygame.K_p, pygame.K_ESCAPE]:
            engine.sound_manager.play("menu change")
            engine.state = "PAUSED"
    elif event.type == pygame.MOUSEBUTTONDOWN:
        mx, my = event.pos
        ui_top_y = HEIGHT - UI_HEIGHT
        btn_rect = pygame.Rect(WIDTH - 350, ui_top_y + 45, 120, 30)
        if btn_rect.collidepoint(mx, my):
            engine.sound_manager.play("menu change")
            engine.state = "INFO"
            engine.info_tab = "INSTRUCTIONS"


def handle_info_event(event, engine):
    if event.type == pygame.KEYDOWN:
        if event.key in [pygame.K_i, pygame.K_ESCAPE]:
            engine.sound_manager.play("menu select")
            engine.state = "PLAYING"
        elif event.key == pygame.K_1:
            engine.sound_manager.play("menu move cursor")
            engine.info_tab = "INSTRUCTIONS"
        elif event.key == pygame.K_2:
            engine.sound_manager.play("menu move cursor")
            engine.info_tab = "STATS"
        elif event.key == pygame.K_3:
            engine.sound_manager.play("menu move cursor")
            engine.info_tab = "KEYBINDS"
    elif event.type == pygame.MOUSEBUTTONDOWN:
        mx, my = event.pos
        tab1_rect = pygame.Rect(60, 110, 210, 40)
        tab2_rect = pygame.Rect(295, 110, 210, 40)
        tab3_rect = pygame.Rect(530, 110, 210, 40)
        if tab1_rect.collidepoint(mx, my):
            engine.sound_manager.play("menu move cursor")
            engine.info_tab = "INSTRUCTIONS"
        elif tab2_rect.collidepoint(mx, my):
            engine.sound_manager.play("menu move cursor")
            engine.info_tab = "STATS"
        elif tab3_rect.collidepoint(mx, my):
            engine.sound_manager.play("menu move cursor")
            engine.info_tab = "KEYBINDS"
        else:
            content_rect = pygame.Rect(60, 170, WIDTH - 120, HEIGHT - 280)
            if not content_rect.collidepoint(mx, my):
                engine.sound_manager.play("menu select")
                engine.state = "PLAYING"


def handle_paused_event(event, engine):
    if event.type == pygame.KEYDOWN:
        if event.key in [pygame.K_1, pygame.K_KP1]:
            engine.sound_manager.play("menu select")
            engine.state = "PLAYING"
        elif event.key in [pygame.K_2, pygame.K_KP2]:
            engine.sound_manager.play("menu select")
            engine.state = "MENU"
        elif event.key in [pygame.K_3, pygame.K_KP3]:
            engine.sound_manager.play("menu select")
            engine.setup_game()
        elif event.key in [pygame.K_p, pygame.K_ESCAPE]:
            engine.sound_manager.play("menu select")
            engine.state = "PLAYING"
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mx, my = event.pos
        panel_width = 400
        panel_height = 50
        start_y = HEIGHT // 3 + 30
        spacing = 70
        for i in range(3):
            x = WIDTH // 2 - panel_width // 2
            y = start_y + i * spacing
            btn_rect = pygame.Rect(x, y, panel_width, panel_height)
            if btn_rect.collidepoint(mx, my):
                engine.sound_manager.play("menu select")
                if i == 0:
                    engine.state = "PLAYING"
                elif i == 1:
                    engine.state = "MENU"
                elif i == 2:
                    engine.setup_game()


def handle_teleport_event(event, engine):
    if event.type != pygame.MOUSEBUTTONDOWN:
        return

    mx, my = event.pos
    mm_x_start = WIDTH - 200
    mm_y_start = HEIGHT - 160
    cell_w, cell_h = 25, 25
    gap = 5
    for gx in range(MAP_COLS):
        for gy in range(MAP_ROWS):
            cx = mm_x_start + gx * (cell_w + gap)
            cy = mm_y_start + gy * (cell_h + gap)
            if cx <= mx <= cx + cell_w and cy <= my <= cy + cell_h:
                if hasattr(engine, 'cave') and (gx, gy) in engine.cave:
                    engine.sound_manager.play("portal woosh")
                    engine.current_room_id = (gx, gy)
                    engine.state = "PLAYING"
                    engine.player.rect.center = (WIDTH // 2, HEIGHT // 2)
                    engine.resolve_room_entry()
                    engine.log(f"Teleported to Cave ({gx}, {gy})!")


def handle_wumpus_prompt_event(event, engine):
    if event.type != pygame.KEYDOWN:
        return

    if event.key == pygame.K_1:
        engine.sound_manager.play("menu select")
        if engine.coins >= 5:
            engine.coins -= 5
            engine.state = "TRIVIA"
            engine.trivia_current_streak = 0
            engine.trivia_target_streak = 2
            engine.trivia_item_buying = "WUMPUS_RETREAT"
            engine.next_question()
        else:
            engine.log("Not enough gold to retreat! You must fight!")
    elif event.key == pygame.K_2:
        engine.sound_manager.play("menu select")
        engine.state = "PLAYING"
        engine.wumpus.awake = True
        engine.wumpus_grace_timer = FPS * 3
        engine.wumpus_chase_timer = FPS * 4
        engine.wumpus.reset_position()
        engine.lockdown_timer = FPS * 30
        engine.wumpus_gold_timer = FPS * 6
        engine.log("The Wumpus is waking up! You have 3 seconds!")
        engine.resolve_room_entry()
