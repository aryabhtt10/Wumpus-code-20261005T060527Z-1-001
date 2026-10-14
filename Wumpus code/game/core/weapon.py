import pygame
import math
from config import *

class BaseWeapon:
    def __init__(self, room_id, x, y, direction, speed=8):
        self.room_id = room_id
        self.rect = pygame.Rect(x, y, 18, 18)
        self.direction = direction
        self.speed = speed
        self.active = True
        
        self.is_explosive = False
        self.is_tnt = False
        self.explosion_timer = 0
        self.exploding = False

    def update(self):
        if self.exploding:
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                self.active = False
            return

        if self.direction == "N":
            self.rect.y -= self.speed
        elif self.direction == "S":
            self.rect.y += self.speed
        elif self.direction == "W":
            self.rect.x -= self.speed
        elif self.direction == "E":
            self.rect.x += self.speed

        if (self.rect.x < 0 or self.rect.x > WIDTH or self.rect.y < 0 or self.rect.y > HEIGHT):
            self.active = False

    def draw(self, screen, img=None):
        if self.exploding:
            # Draw blinking explosion
            if (self.explosion_timer // 4) % 2 == 0:
                radius = TNT_RADIUS if self.is_tnt else EXPLOSIVE_RADIUS
                pygame.draw.circle(screen, C_EXPLOSION, self.rect.center, radius)
            return

        if img is not None:
            # Dynamically rotate arrow sprite to match flight direction (facing East by default)
            angle = 0
            if self.direction == "N":
                angle = 90
            elif self.direction == "S":
                angle = 270
            elif self.direction == "W":
                angle = 180
            elif self.direction == "E":
                angle = 0
            
            rotated_img = pygame.transform.rotate(img, angle)
            new_rect = rotated_img.get_rect(center=self.rect.center)
            screen.blit(rotated_img, new_rect)
        else:
            color = (255, 100, 100) if self.is_tnt else (255, 255, 0)
            pygame.draw.rect(screen, color, self.rect)

    def trigger_explosion(self):
        self.exploding = True
        self.explosion_timer = 60 # 1 second explosion
        self.speed = 0

class NormalArrow(BaseWeapon):
    def __init__(self, room_id, x, y, direction):
        super().__init__(room_id, x, y, direction)

class ExplosiveArrow(BaseWeapon):
    def __init__(self, room_id, x, y, direction):
        super().__init__(room_id, x, y, direction, speed=6)
        self.is_explosive = True

class TNTWeapon(BaseWeapon):
    def __init__(self, room_id, x, y, direction):
        super().__init__(room_id, x, y, direction, speed=4)
        self.is_tnt = True
        self.is_explosive = True
