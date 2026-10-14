import pygame
from config import *

class Arrow:
    def __init__(self, room_id, x, y, direction):
        self.room_id = room_id
        self.rect = pygame.Rect(x, y, 18, 18)
        self.direction = direction
        self.speed = 8
        self.active = True

    def update(self):
        if self.direction == "N":
            self.rect.y -= self.speed
        elif self.direction == "S":
            self.rect.y += self.speed
        elif self.direction == "W":
            self.rect.x -= self.speed
        elif self.direction == "E":
            self.rect.x += self.speed

        # destroy if leaves room bounds
        if (self.rect.x < 0 or self.rect.x > WIDTH or
            self.rect.y < 0 or self.rect.y > HEIGHT):
            self.active = False

    def draw(self, screen, img=None):
        if img is not None:
            screen.blit(img, self.rect)
        else:
            # Fallback: Draws a bright yellow square so you can see it without the asset
            pygame.draw.rect(screen, (255, 255, 0), self.rect)
