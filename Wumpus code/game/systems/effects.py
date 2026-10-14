import pygame
import random

from config import WIDTH, HEIGHT, UI_HEIGHT


class FloatingText:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.life = 60
        self.font = pygame.font.SysFont("Arial", 20, bold=True)

    def update(self):
        self.y -= 1
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            alpha = min(255, self.life * 5)
            txt = self.font.render(self.text, True, self.color)
            txt.set_alpha(alpha)
            surface.blit(txt, (self.x, self.y))


class ScoreFloater:
    def __init__(self, amount, x, y):
        self.amount = amount
        self.x = x
        self.y = y
        self.alpha = 255

    def update(self):
        self.y -= 1
        self.alpha -= 5

    def draw(self, surface, font):
        txt = font.render(f"+{self.amount}", True, (50, 255, 50))
        txt.set_alpha(self.alpha)
        surface.blit(txt, (self.x, self.y))


class FloatingTextManager:
    def __init__(self):
        self.floaters = []
        self.score_floaters = []

    def clear(self):
        self.floaters.clear()
        self.score_floaters.clear()

    def spawn_text(self, text, x, y, color):
        self.floaters.append(FloatingText(text, x, y, color))

    def spawn_score(self, amount):
        fx = 420 + random.randint(-20, 20)
        fy = (HEIGHT - UI_HEIGHT + 15) + random.randint(-10, 10)
        self.score_floaters.append(ScoreFloater(amount, fx, fy))

    def update(self):
        for ft in self.floaters[:]:
            ft.update()
            if ft.life <= 0:
                self.floaters.remove(ft)

        for sf in self.score_floaters[:]:
            sf.update()
            if sf.alpha <= 0:
                self.score_floaters.remove(sf)

    def draw(self, surface, font):
        for ft in self.floaters:
            ft.draw(surface)
        for sf in self.score_floaters:
            sf.draw(surface, font)
