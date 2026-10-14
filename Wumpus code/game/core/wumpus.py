import pygame
import random
from config import WIDTH, HEIGHT, ROWS, TILE_SIZE, C_WUMPUS
from core.enemy import Spider, Bat

class Wumpus:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 100, 100)
        self.hp = 100
        self.speed = 1.0
        self.awake = False
        self.spawn_timer = 0

    def reset_position(self):
        self.rect.x = 80
        self.rect.y = 80
        self.spawn_timer = 0

    def spawn_at_portal(self, from_dir):
        if from_dir == 'N':
            self.rect.x = WIDTH // 2 - 50
            self.rect.y = 50
        elif from_dir == 'S':
            self.rect.x = WIDTH // 2 - 50
            self.rect.y = (ROWS * TILE_SIZE) - 100
        elif from_dir == 'E':
            self.rect.x = WIDTH - 100
            self.rect.y = (ROWS * TILE_SIZE) // 2 - 50
        elif from_dir == 'W':
            self.rect.x = 50
            self.rect.y = (ROWS * TILE_SIZE) // 2 - 50
        else:
            self.reset_position()
        self.spawn_timer = 60 # 1 second delay before first spawn

    def update(self, player_rect, enemies_list):
        if not self.awake:
            return

        # Move towards player
        if player_rect.centerx < self.rect.centerx:
            self.rect.x -= self.speed
        if player_rect.centerx > self.rect.centerx:
            self.rect.x += self.speed
        if player_rect.centery < self.rect.centery:
            self.rect.y -= self.speed
        if player_rect.centery > self.rect.centery:
            self.rect.y += self.speed

        # Minion Spawner logic
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            self.spawn_timer = random.randint(120, 240) # Every 2-4 seconds
            num_spawns = random.randint(2, 4)
            for _ in range(num_spawns):
                spawn_x = self.rect.centerx + random.randint(-80, 80)
                spawn_y = self.rect.centery + random.randint(-80, 80)
                if random.random() < 0.3:
                    enemies_list.append(Bat(spawn_x, spawn_y))
                else:
                    is_big = random.random() < 0.2
                    enemies_list.append(Spider(spawn_x, spawn_y, is_big))

    def draw(self, screen, image=None):
        if not self.awake:
            return

        if image is not None:
            screen.blit(image, self.rect)
        else:
            pygame.draw.circle(screen, (120, 80, 160), self.rect.center, self.rect.width // 2)