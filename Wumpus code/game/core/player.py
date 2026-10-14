import pygame
import math
import os
from config import WIDTH, ROWS, TILE_SIZE, C_PLAYER, PLAYER_HEALTH_MAX
from core.particle import ParticleSystem

class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 15, (ROWS * TILE_SIZE) // 2 - 15, 30, 30)
        self.speed = 4
        self.health = PLAYER_HEALTH_MAX
        self.max_health = PLAYER_HEALTH_MAX
        self.particles = ParticleSystem()
        
        self.bob_timer = 0
        self.is_moving = False
        self.fallback_image = None
        path = os.path.join("assets", "player.png")
        try:
            img = pygame.image.load(path).convert_alpha()
            self.fallback_image = pygame.transform.scale(img, (48, 48))
        except (pygame.error, FileNotFoundError):
            pass

    def update(self, dx, dy):
        self.is_moving = dx != 0 or dy != 0
        if self.is_moving:
            self.bob_timer += 0.2
            self.particles.emit_dirt(self.rect.centerx, self.rect.bottom - 5, dx, dy)
        else:
            self.bob_timer = 0
        self.particles.update()

    def get_movement_delta(self, keys):
        dx = 0
        dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.speed
        return dx, dy

    def handle_movement(self, keys):
        dx, dy = self.get_movement_delta(keys)
        self.update(dx, dy)
        return dx, dy

    def draw(self, screen, image=None):
        self.particles.draw(screen)
        bob_offset = 0
        if self.is_moving:
            bob_offset = abs(math.sin(self.bob_timer)) * 5

        draw_rect = self.rect.copy()
        draw_rect.inflate_ip(18, 18)
        draw_rect.y -= bob_offset

        active_img = image if image is not None else self.fallback_image

        if active_img is not None:
            if self.is_moving:
                angle = math.sin(self.bob_timer * 1.5) * 8
                rotated_image = pygame.transform.rotate(active_img, angle)
                new_rect = rotated_image.get_rect(center=draw_rect.center)
                screen.blit(rotated_image, new_rect)
            else:
                screen.blit(active_img, draw_rect)
        else:
            pygame.draw.rect(screen, C_PLAYER, draw_rect)