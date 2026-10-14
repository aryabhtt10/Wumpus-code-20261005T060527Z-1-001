import pygame
import random
import math
from config import WIDTH, HEIGHT

class Particle:
    def __init__(self, x, y, dx, dy, color, decay, size):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.life = 255
        self.decay = decay
        self.size = size

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= self.decay

    def draw(self, surface):
        if self.life > 0:
            s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            s.fill((*self.color, max(0, int(self.life))))
            surface.blit(s, (int(self.x), int(self.y)))

class SparkleParticle(Particle):
    def draw(self, surface):
        if self.life > 0:
            alpha = max(0, int(self.life))
            # Draw a star/sparkle shape
            pygame.draw.circle(surface, (*self.color, alpha), (int(self.x), int(self.y)), int(self.size/2))
            pygame.draw.line(surface, (*self.color, alpha), (int(self.x - self.size), int(self.y)), (int(self.x + self.size), int(self.y)), 2)
            pygame.draw.line(surface, (*self.color, alpha), (int(self.x), int(self.y - self.size)), (int(self.x), int(self.y + self.size)), 2)

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit_dirt(self, x, y, move_dx, move_dy):
        # Dirt tracks - they stay longer and fade slowly, AND DO NOT MOVE (stationary etched tracks)
        color = random.choice([(70, 45, 15), (90, 60, 20), (50, 30, 10)])
        decay = random.uniform(1.5, 3) # Very slow decay
        size = random.randint(4, 7)
        
        # Add random offset near player's feet
        px = x + random.uniform(-6, 6)
        py = y + random.uniform(-6, 6)
        
        self.particles.append(Particle(px, py, 0, 0, color, decay, size))

    def emit_sparkle(self, x, y):
        # Golden sparkles for coins
        for _ in range(8):
            dx = random.uniform(-2, 2)
            dy = random.uniform(-2, 2)
            color = (255, 230, 100)
            decay = random.uniform(5, 15)
            self.particles.append(SparkleParticle(x, y, dx, dy, color, decay, random.randint(4, 8)))

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

class TransitionEffect:
    def __init__(self):
        self.active = False
        self.timer = 0
        self.duration = 40 # frames
        self.lines = []
        
    def start(self):
        self.active = True
        self.timer = self.duration
        self.lines = []
        # Create tunnel lines coming from center
        for _ in range(50):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(10, 30)
            self.lines.append([angle, speed, 0]) # angle, speed, distance from center
            
    def update(self):
        if not self.active:
            return
        self.timer -= 1
        if self.timer <= 0:
            self.active = False
            return
            
        for line in self.lines:
            line[2] += line[1] # increase distance

    def draw(self, surface):
        if not self.active:
            return
            
        # Draw tunnel effect overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        alpha = int((self.timer / self.duration) * 255)
        overlay.fill((20, 10, 40, min(255, alpha)))
        
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        for line in self.lines:
            angle, _, dist = line
            # Draw line extending outward
            x1 = center_x + math.cos(angle) * dist
            y1 = center_y + math.sin(angle) * dist
            x2 = center_x + math.cos(angle) * (dist + 50)
            y2 = center_y + math.sin(angle) * (dist + 50)
            pygame.draw.line(overlay, (150, 100, 255, alpha), (x1, y1), (x2, y2), 3)
            
        surface.blit(overlay, (0, 0))
