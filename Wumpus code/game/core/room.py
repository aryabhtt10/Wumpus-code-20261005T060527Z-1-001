import pygame
import random
from config import WIDTH, HEIGHT, ROWS, COLS, TILE_SIZE, MAP_COLS, MAP_ROWS

class Room:
    def __init__(self, gx, gy):
        self.grid_pos = (gx, gy)
        self.doors = {} 
        
        if gy > 0: self.doors['N'] = (gx, gy - 1)
        if gy < MAP_ROWS - 1: self.doors['S'] = (gx, gy + 1)
        if gx < MAP_COLS - 1: self.doors['E'] = (gx + 1, gy)
        if gx > 0: self.doors['W'] = (gx - 1, gy)
        
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.portal_angle = 0
        
        self.gold_drops = []
        num_spawns = random.choices([1, 2], weights=[0.7, 0.3])[0]
        for _ in range(num_spawns):
            r = random.random()
            if r < 0.60:
                amt = random.choice([1, 3])
            elif r < 0.90:
                amt = random.choice([4, 6])
            else:
                amt = random.choice([8, 10])
            self.gold_drops.append({'rect': self._make_coin_rect(), 'amount': amt, 'collected': False})

        self.build_physical_room()

    def _make_coin_rect(self):
        cx = random.randint(100, WIDTH - 100)
        cy = random.randint(100, (ROWS * TILE_SIZE) - 100)
        return pygame.Rect(cx, cy, 20, 20)

    def build_physical_room(self):
        for y in range(ROWS):
            for x in range(COLS):
                if x == 0 or x == COLS - 1 or y == 0 or y == ROWS - 1:
                    self.grid[y][x] = 1
                else:
                    self.grid[y][x] = 0

    def add_doors_to_grid(self):
        mid_x, mid_y = COLS // 2, ROWS // 2
        if 'N' in self.doors:
            self.grid[0][mid_x] = 2
        if 'S' in self.doors:
            self.grid[ROWS - 1][mid_x] = 2
        if 'E' in self.doors:
            self.grid[mid_y][COLS - 1] = 2
        if 'W' in self.doors:
            self.grid[mid_y][0] = 2