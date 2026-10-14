"""
Enemy Module

Contains all enemy classes including Spiders, Bats, and Super Bats.
Uses lazy loading for images to optimize performance.
"""

import pygame
import random
import math
import logging
from config import SPIDER_BIG_HP
from systems.asset_loader import load_image

logger = logging.getLogger(__name__)


class Enemy:
    """Base class for all enemies."""
    
    def __init__(self, x, y, size, hp, speed, color):
        self.rect = pygame.Rect(x, y, size, size)
        self.hp = hp
        self.speed = speed
        self.color = color
        self.active = True
        self.is_big = False
        self.image = None  # Child classes will populate this

    def update(self, player_rect):
        """Update enemy position and state. To be overridden by child classes."""
        pass

    def draw(self, screen):
        """Draw the enemy on the screen."""
        if self.active:
            if self.image:
                screen.blit(self.image, self.rect)
            else:
                # Fallback to simple rectangle drawing if image loading failed
                pygame.draw.rect(screen, self.color, self.rect)


class Spider(Enemy):
    """Spider enemy that chases the player."""
    
    # Class-level image cache to avoid reloading
    _img_big = None

    def __init__(self, x, y, is_big=False):
        # Force all spiders to be big spiders
        is_big = True
        size = 35
        hp = SPIDER_BIG_HP
        base_speed = 0.5
        speed = base_speed + random.uniform(-0.15, 0.15)
        color = (50, 40, 40)
        
        super().__init__(x, y, size, hp, speed, color)
        self.is_big = True
        self.fx = float(x)
        self.fy = float(y)

        # Lazy load the spider image
        if Spider._img_big is None:
            Spider._img_big = self._load_enemy_image("spider_big.png", size, size)
        self.image = Spider._img_big

    @staticmethod
    def _load_enemy_image(filename, width, height):
        """Load enemy image with fallback."""
        image = load_image(filename, (width, height))
        if image is None:
            logger.warning(f"Could not load spider image: {filename}")
        return image

    def update(self, player_rect):
        """Move towards the player."""
        if not self.active:
            return
            
        # Move horizontally towards player
        if self.rect.centerx < player_rect.centerx:
            self.fx += self.speed
        elif self.rect.centerx > player_rect.centerx:
            self.fx -= self.speed
        
        # Move vertically towards player    
        if self.rect.centery < player_rect.centery:
            self.fy += self.speed
        elif self.rect.centery > player_rect.centery:
            self.fy -= self.speed
        
        # Update actual position
        self.rect.x = int(self.fx)
        self.rect.y = int(self.fy)


class Bat(Enemy):
    """Bat enemy that charges at the player then flees after stealing gold."""
    
    _img_bat = None

    def __init__(self, x, y):
        super().__init__(x, y, 24, 1, 5.0, (80, 80, 100))
        self.fleeing = False
        self.flee_dir_x = 0
        self.flee_dir_y = 0
        self.fx = float(x)
        self.fy = float(y)
        self.charge_timer = random.randint(30, 90)
        self.vx = 0
        self.vy = 0

        # Lazy load bat image
        if Bat._img_bat is None:
            Bat._img_bat = self._load_enemy_image("bat.png", self.rect.width, self.rect.height)
        self.image = Bat._img_bat

    @staticmethod
    def _load_enemy_image(filename, width, height):
        """Load enemy image with fallback."""
        image = load_image(filename, (width, height))
        if image is None:
            logger.warning(f"Could not load bat image: {filename}")
        return image

    def update(self, player_rect):
        """Update bat behavior: charge then flee."""
        if not self.active:
            return
        
        # Handle fleeing state
        if self.fleeing:
            self.fx += self.flee_dir_x * self.speed
            self.fy += self.flee_dir_y * self.speed
            self.rect.x = int(self.fx)
            self.rect.y = int(self.fy)
            return

        # Charging state
        if self.charge_timer > 0:
            self.charge_timer -= 1
            if self.charge_timer == 0:
                dx = player_rect.centerx - self.rect.centerx
                dy = player_rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist != 0:
                    self.vx = (dx / dist) * (self.speed * 2.0)
                    self.vy = (dy / dist) * (self.speed * 2.0)
        else:
            self.fx += self.vx
            self.fy += self.vy
        
        self.rect.x = int(self.fx)
        self.rect.y = int(self.fy)

    def steal(self):
        """Make the bat flee after stealing gold."""
        self.fleeing = True
        self.flee_dir_x = random.choice([-1, 1])
        self.flee_dir_y = random.choice([-1, 1])

    def draw(self, screen):
        """Draw the bat with custom circle fallback."""
        if not self.active:
            return
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            cx, cy = self.rect.center
            pygame.draw.circle(screen, self.color, (cx, cy), 10)


class SuperBat(Enemy):
    """Super Bat boss enemy that teleports the player when touched."""
    
    _img_super_bat = None

    def __init__(self, x, y):
        # Super Bats are larger with custom dimensions
        size_w = 75
        size_h = 50
        super().__init__(x, y, 48, 5, 6.5, (255, 215, 0))
        self.rect = pygame.Rect(x, y, size_w, size_h)
        self.fx = float(x)
        self.fy = float(y)

        # Lazy load super bat image
        if SuperBat._img_super_bat is None:
            SuperBat._img_super_bat = self._load_enemy_image("super_bat.png", size_w, size_h)
        self.image = SuperBat._img_super_bat

    @staticmethod
    def _load_enemy_image(filename, width, height):
        """Load enemy image with fallback."""
        image = load_image(filename, (width, height))
        if image is None:
            logger.warning(f"Could not load super bat image: {filename}")
        return image

    def update(self, player_rect):
        """Smooth pursuit of the player."""
        if not self.active:
            return
        
        # Move towards player's center with smooth pursuit
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        
        if dist != 0:
            self.fx += (dx / dist) * self.speed
            self.fy += (dy / dist) * self.speed
        
        self.rect.x = int(self.fx)
        self.rect.y = int(self.fy)

    def draw(self, screen):
        """Draw the super bat with custom circle fallback."""
        if not self.active:
            return
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            cx, cy = self.rect.center
            pygame.draw.circle(screen, self.color, (cx, cy), 20)