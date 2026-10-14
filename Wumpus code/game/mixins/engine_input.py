import pygame
import math

from config import *


class InputMixin:
    def handle_input(self):
        if self.state == "MENU":
            return
        if self.state in ["GAMEOVER", "VICTORY", "TRIVIA", "SHOP", "PIT_TRIVIA", "INFO", "WUMPUS_PROMPT", "PAUSED", "TELEPORT_SELECT"]:
            return

        keys = pygame.key.get_pressed()
        if self.combat_manager.handle_shooting_input(keys):
            return

        dx, dy = self.player.handle_movement(keys)

        if (dx != 0 or dy != 0) and self.footstep_cooldown <= 0:
            self.sound_manager.play_footstep()
            self.footstep_cooldown = 20

        self.player.rect.x += dx
        if self.check_collisions(dx, 0):
            return
        self.player.rect.y += dy
        if self.check_collisions(0, dy):
            return

        room = self.cave[self.current_room_id]
        for drop in room.gold_drops:
            if not drop['collected']:
                dist = math.hypot(drop['rect'].centerx - self.player.rect.centerx, drop['rect'].centery - self.player.rect.centery)
                if dist < self.light_radius and self.player.rect.colliderect(drop['rect']):
                    drop['collected'] = True
                    self.coins += drop['amount']
                    self.sound_manager.play("coin collect")
                    self.player.particles.emit_sparkle(self.player.rect.centerx, self.player.rect.centery)
                    self.spawn_floating_text(f"+{drop['amount']} Gold", self.player.rect.centerx, drop['rect'].top, (255, 215, 0))
                    self.log(f"Collected {drop['amount']} gold!")

    def check_collisions(self, dx, dy):
        room = self.cave[self.current_room_id]
        for y in range(ROWS):
            for x in range(COLS):
                tile_val = room.grid[y][x]
                if tile_val == 0:
                    continue

                tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if self.player.rect.colliderect(tile_rect):
                    if tile_val == 1 or (tile_val == 2 and self.lockdown_timer > 0):
                        if dx > 0:
                            self.player.rect.right = tile_rect.left
                        if dx < 0:
                            self.player.rect.left = tile_rect.right
                        if dy > 0:
                            self.player.rect.bottom = tile_rect.top
                        if dy < 0:
                            self.player.rect.top = tile_rect.bottom
                    elif tile_val == 2 and self.lockdown_timer <= 0:
                        self.transition_room(x, y, room)
                        return True
        return False

    def transition_room(self, door_x, door_y, current_room):
        direction = None
        if door_y == 0:
            direction = 'N'
        elif door_y == ROWS - 1:
            direction = 'S'
        elif door_x == 0:
            direction = 'W'
        elif door_x == COLS - 1:
            direction = 'E'

        if direction and direction in current_room.doors:
            target_room = current_room.doors[direction]
            source_room_id = self.current_room_id
            self.last_safe_room = source_room_id
            self.turns += 1
            self.current_room_id = target_room

            if direction == 'N':
                self.player.rect.centerx = (COLS // 2) * TILE_SIZE + TILE_SIZE // 2
                self.player.rect.y = (ROWS - 2) * TILE_SIZE
            elif direction == 'S':
                self.player.rect.centerx = (COLS // 2) * TILE_SIZE + TILE_SIZE // 2
                self.player.rect.y = 1 * TILE_SIZE
            elif direction == 'W':
                self.player.rect.x = (COLS - 2) * TILE_SIZE
                self.player.rect.centery = (ROWS // 2) * TILE_SIZE + TILE_SIZE // 2
            elif direction == 'E':
                self.player.rect.x = 1 * TILE_SIZE
                self.player.rect.centery = (ROWS // 2) * TILE_SIZE + TILE_SIZE // 2

            self.transition.start()
            self.sound_manager.play("portal woosh")

            if target_room != self.wumpus_grid_pos:
                if len(self.visited_rooms) >= 3 and target_room in self.pit_rooms and target_room != (0, 0):
                    if self.coins >= 5:
                        self.coins -= 5
                        self.log("A portal malfunctioned! 5 Gold was consumed to activate the Pit Trivia!")
                    else:
                        self.trigger_game_over("You fell into a pit and couldn't pay the 5 Gold toll!")
                        self.log("You fell into a pit and couldn't pay the 5 Gold toll!")
                        return

                    self.intended_room_id = target_room
                    self.intended_direction = direction
                    self.current_room_id = source_room_id
                    self.player.rect.center = (WIDTH // 2, HEIGHT // 2)

                    self.state = "PIT_TRIVIA"
                    self.trivia_current_streak = 0
                    self.trivia_target_streak = 2
                    self.trivia_item_buying = "PIT_SURVIVE"
                    self.next_question()
                    self.resolve_room_entry()
                    return

            self.resolve_room_entry()
