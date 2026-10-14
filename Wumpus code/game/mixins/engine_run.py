import pygame
import sys

from config import *
from event_handling import handle_state_event


class RunMixin:
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.state == "MENU":
                    if event.type == pygame.KEYDOWN:
                        if event.key in [pygame.K_1, pygame.K_KP1]:
                            self.sound_manager.play("menu select")
                            self.difficulty = "EASY"
                            self.setup_game()
                        elif event.key in [pygame.K_2, pygame.K_KP2]:
                            self.sound_manager.play("menu select")
                            self.difficulty = "MEDIUM"
                            self.setup_game()
                        elif event.key in [pygame.K_3, pygame.K_KP3]:
                            self.sound_manager.play("menu select")
                            self.difficulty = "HARD"
                            self.setup_game()

                elif self.state in ["GAMEOVER", "VICTORY"]:
                    if not getattr(self, 'score_saved', False):
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN:
                                name_to_save = self.player_name_input.strip()
                                if not name_to_save:
                                    name_to_save = "Player"
                                self.save_score(name_to_save)
                            elif event.key == pygame.K_BACKSPACE:
                                self.player_name_input = self.player_name_input[:-1]
                            else:
                                if event.unicode and event.unicode.isprintable() and len(self.player_name_input) < 15:
                                    if event.unicode != ",":
                                        self.player_name_input += event.unicode
                    else:
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                            self.state = "MENU"

                elif self.state == "PLAYING":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_e:
                            self.sound_manager.play("menu change")
                            self.state = "SHOP"
                        elif event.key == pygame.K_i:
                            self.sound_manager.play("menu change")
                            self.state = "INFO"
                            self.info_tab = "INSTRUCTIONS"
                        elif event.key in [pygame.K_p, pygame.K_ESCAPE]:
                            self.sound_manager.play("menu change")
                            self.state = "PAUSED"
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        ui_top_y = HEIGHT - UI_HEIGHT
                        btn_rect = pygame.Rect(WIDTH - 350, ui_top_y + 45, 120, 30)
                        if btn_rect.collidepoint(mx, my):
                            self.sound_manager.play("menu change")
                            self.state = "INFO"
                            self.info_tab = "INSTRUCTIONS"

                elif self.state == "INFO":
                    if event.type == pygame.KEYDOWN:
                        if event.key in [pygame.K_i, pygame.K_ESCAPE]:
                            self.sound_manager.play("menu select")
                            self.state = "PLAYING"
                        elif event.key == pygame.K_1:
                            self.sound_manager.play("menu move cursor")
                            self.info_tab = "INSTRUCTIONS"
                        elif event.key == pygame.K_2:
                            self.sound_manager.play("menu move cursor")
                            self.info_tab = "STATS"
                        elif event.key == pygame.K_3:
                            self.sound_manager.play("menu move cursor")
                            self.info_tab = "KEYBINDS"
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        tab1_rect = pygame.Rect(60, 110, 210, 40)
                        tab2_rect = pygame.Rect(295, 110, 210, 40)
                        tab3_rect = pygame.Rect(530, 110, 210, 40)
                        if tab1_rect.collidepoint(mx, my):
                            self.sound_manager.play("menu move cursor")
                            self.info_tab = "INSTRUCTIONS"
                        elif tab2_rect.collidepoint(mx, my):
                            self.sound_manager.play("menu move cursor")
                            self.info_tab = "STATS"
                        elif tab3_rect.collidepoint(mx, my):
                            self.sound_manager.play("menu move cursor")
                            self.info_tab = "KEYBINDS"
                        else:
                            content_rect = pygame.Rect(60, 170, WIDTH - 120, HEIGHT - 280)
                            if not content_rect.collidepoint(mx, my):
                                self.sound_manager.play("menu select")
                                self.state = "PLAYING"

                elif self.state == "PAUSED":
                    if event.type == pygame.KEYDOWN:
                        if event.key in [pygame.K_1, pygame.K_KP1]:
                            self.sound_manager.play("menu select")
                            self.state = "PLAYING"
                        elif event.key in [pygame.K_2, pygame.K_KP2]:
                            self.sound_manager.play("menu select")
                            self.state = "MENU"
                        elif event.key in [pygame.K_3, pygame.K_KP3]:
                            self.sound_manager.play("menu select")
                            self.setup_game()
                        elif event.key in [pygame.K_p, pygame.K_ESCAPE]:
                            self.sound_manager.play("menu select")
                            self.state = "PLAYING"
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
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
                                    if i == 0:
                                        self.sound_manager.play("menu select")
                                        self.state = "PLAYING"
                                    elif i == 1:
                                        self.sound_manager.play("menu select")
                                        self.state = "MENU"
                                    elif i == 2:
                                        self.sound_manager.play("menu select")
                                        self.setup_game()

                elif self.state == "TELEPORT_SELECT":
                    if event.type == pygame.MOUSEBUTTONDOWN:
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
                                    if hasattr(self, 'cave') and (gx, gy) in self.cave:
                                        self.sound_manager.play("portal woosh")
                                        self.current_room_id = (gx, gy)
                                        self.state = "PLAYING"
                                        self.player.rect.center = (WIDTH // 2, HEIGHT // 2)
                                        self.resolve_room_entry()
                                        self.log(f"Teleported to Cave ({gx}, {gy})!")

                else:
                    handle_state_event(event, self)

            self.handle_input()
            self.update_entities()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
