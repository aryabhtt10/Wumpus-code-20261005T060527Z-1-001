import math
import pygame

from config import *
from core.weapon import NormalArrow, ExplosiveArrow, TNTWeapon
from core.enemy import Enemy, SuperBat


class CombatManager:
    def __init__(self, engine):
        self.engine = engine
        self.active_weapons = []

    def clear(self):
        self.active_weapons.clear()

    def spawn_weapon(self, direction, w_type):
        w_class = None
        if w_type == "NORMAL":
            if self.engine.arrows <= 0:
                self.engine.log("No Normal Arrows left!")
                return False
            self.engine.arrows -= 1
            self.engine.sound_manager.play("arrow whoosh")
            w_class = NormalArrow
        elif w_type == "EXPLOSIVE":
            if self.engine.explosive_arrows <= 0:
                self.engine.log("No Explosive Arrows left!")
                return False
            self.engine.explosive_arrows -= 1
            self.engine.sound_manager.play("arrow whoosh")
            w_class = ExplosiveArrow
        elif w_type == "TNT":
            if self.engine.tnt <= 0:
                self.engine.log("No TNT left!")
                return False
            self.engine.tnt -= 1
            w_class = TNTWeapon

        if w_class:
            self.active_weapons.append(
                w_class(
                    self.engine.current_room_id,
                    self.engine.player.rect.centerx,
                    self.engine.player.rect.centery,
                    direction,
                )
            )
            return True

        return False

    def handle_shooting_input(self, keys):
        if self.engine.shoot_cooldown > 0:
            self.engine.shoot_cooldown -= 1

        if self.engine.shoot_cooldown != 0:
            return False

        shoot_dir = None
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            shoot_dir = 'N'
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            shoot_dir = 'S'
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            shoot_dir = 'W'
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            shoot_dir = 'E'

        if not shoot_dir:
            return False

        fired = False
        if keys[pygame.K_q]:
            fired = self.spawn_weapon(shoot_dir, "TNT")
            if fired:
                self.engine.shoot_cooldown = 40
        elif keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            fired = self.spawn_weapon(shoot_dir, "EXPLOSIVE")
            if fired:
                self.engine.shoot_cooldown = 30
        elif keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            fired = self.spawn_weapon(shoot_dir, "NORMAL")
            if fired:
                self.engine.shoot_cooldown = 20

        return fired

    def damage_wumpus(self, amount, msg=None):
        engine = self.engine
        if engine.state in ("GAMEOVER", "VICTORY"):
            return

        engine.wumpus.hp -= amount
        engine.add_score(3)
        engine.spawn_floating_text(
            f"-{amount}",
            engine.wumpus.rect.centerx,
            engine.wumpus.rect.top,
            (255, 100, 100),
        )
        if msg:
            engine.log(msg)
        else:
            engine.log(f"Wumpus hit! HP left: {engine.wumpus.hp}")

        if engine.wumpus.hp <= 0:
            engine.wumpus.hp = 0
            engine.state = "VICTORY"
            engine.wumpus.awake = False
            engine.add_score(25)
            engine.log("You defeated the Wumpus!")

    def update_weapons(self):
        for w in self.active_weapons[:]:
            w.update()
            if not w.active:
                self.active_weapons.remove(w)
                continue
            if w.exploding:
                self.apply_explosion(w)
                continue

            hit = False
            if self.engine.wumpus.awake and w.rect.colliderect(self.engine.wumpus.rect):
                hit = True
                if w.is_explosive:
                    w.trigger_explosion()
                    self.apply_explosion(w)
                    dmg = DMG_TNT_WUMPUS if w.is_tnt else DMG_EXPLOSIVE_WUMPUS
                    self.damage_wumpus(dmg)
                else:
                    self.damage_wumpus(DMG_NORMAL_ARROW)
                    w.active = False

            if not hit:
                for enemy in self.engine.enemies:
                    if isinstance(enemy, Enemy) and w.rect.colliderect(enemy.rect):
                        hit = True
                        if w.is_explosive:
                            w.trigger_explosion()
                            self.apply_explosion(w)
                        else:
                            enemy.hp -= 1
                            if enemy.hp <= 0:
                                if enemy in self.engine.enemies:
                                    self.engine.enemies.remove(enemy)
                                if isinstance(enemy, SuperBat):
                                    if self.engine.current_room_id in self.engine.super_bat_rooms:
                                        self.engine.super_bat_rooms.remove(self.engine.current_room_id)
                                    self.engine.log("You defeated the majestic Super Bat!")
                                    self.engine.add_score(15)
                                else:
                                    self.engine.add_score(
                                        2 if getattr(enemy, 'is_big', False) else 1
                                    )
                            w.active = False
                        break

            if not hit and w.is_explosive:
                room = self.engine.cave[self.engine.current_room_id]
                for y in range(ROWS):
                    for x in range(COLS):
                        if room.grid[y][x] == 1:
                            wall_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                            if w.rect.colliderect(wall_rect):
                                w.trigger_explosion()
                                self.apply_explosion(w)
                                hit = True
                                break
                    if hit:
                        break

    def apply_explosion(self, weapon):
        engine = self.engine
        if not getattr(weapon, 'explosion_sound_played', False):
            engine.sound_manager.play("explosion")
            weapon.explosion_sound_played = True
        if not hasattr(weapon, 'kills_made'):
            weapon.kills_made = 0
        if not hasattr(weapon, 'hit_wumpus'):
            weapon.hit_wumpus = False

        radius = TNT_RADIUS if getattr(weapon, 'is_tnt', False) else EXPLOSIVE_RADIUS

        for enemy in engine.enemies[:]:
            dist = math.hypot(
                enemy.rect.centerx - weapon.rect.centerx,
                enemy.rect.centery - weapon.rect.centery,
            )
            if dist <= radius:
                if enemy in engine.enemies:
                    engine.enemies.remove(enemy)
                    if isinstance(enemy, SuperBat):
                        if engine.current_room_id in engine.super_bat_rooms:
                            engine.super_bat_rooms.remove(engine.current_room_id)
                        engine.log("You defeated the majestic Super Bat with an explosion!")
                        engine.add_score(15)
                    else:
                        engine.add_score(2 if getattr(enemy, 'is_big', False) else 1)
                    weapon.kills_made += 1

        if engine.wumpus.awake and not weapon.hit_wumpus:
            dist = math.hypot(
                engine.wumpus.rect.centerx - weapon.rect.centerx,
                engine.wumpus.rect.centery - weapon.rect.centery,
            )
            if dist <= radius:
                dmg = 8 if weapon.is_tnt else 3
                self.damage_wumpus(
                    dmg,
                    msg=f"Wumpus caught in explosion! Takes {dmg} damage!",
                )
                weapon.hit_wumpus = True
