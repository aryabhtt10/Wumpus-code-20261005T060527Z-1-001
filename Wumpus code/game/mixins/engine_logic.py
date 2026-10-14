import random
import math

from config import *
from core.enemy import Spider, Bat, SuperBat


class LogicMixin:
    def resolve_trivia_answer(self, is_correct):
        if self.trivia_item_buying in ["Normal Arrow Pack (30)", "Small Arrow Pack (5)"]:
            self.trivia_questions_asked += 1
            if is_correct:
                self.sound_manager.play("correct answer")
                self.trivia_current_streak += 1
                self.trivia_max_consecutive_correct = max(self.trivia_max_consecutive_correct, self.trivia_current_streak)
                self.log(f"Correct! Current streak: {self.trivia_current_streak}")
            else:
                self.sound_manager.play("wrong answer")
                self.log("Incorrect answer!")
                self.trivia_current_streak = 0

            if self.trivia_max_consecutive_correct >= 2:
                self.log("Trivia challenge passed!")
                self.coins -= self.trivia_item_cost
                self.grant_item(self.trivia_item_buying)
                self.state = "SHOP"
            elif self.trivia_questions_asked >= 3:
                self.log("Challenge failed! Starting over...")
                self.trivia_questions_asked = 0
                self.trivia_current_streak = 0
                self.trivia_max_consecutive_correct = 0
                self.next_question()
            else:
                self.next_question()
            return

        if is_correct:
            self.sound_manager.play("correct answer")
            self.trivia_current_streak += 1
            if self.trivia_current_streak >= self.trivia_target_streak:
                if self.trivia_item_buying == "PIT_SURVIVE":
                    self.log("You correctly answered and escaped the pit!")
                    self.current_room_id = getattr(self, 'intended_room_id', (0, 0))
                    self.state = "PLAYING"
                    self.transition.start()

                    direction = getattr(self, 'intended_direction', 'N')
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

                    self.resolve_room_entry()
                elif self.trivia_item_buying == "WUMPUS_RETREAT":
                    wx, wy = self.current_room_id
                    sx, sy = self.last_safe_room
                    self.current_room_id = self.last_safe_room

                    if wx > sx:
                        self.player.rect.centerx = WIDTH - 100
                    elif wx < sx:
                        self.player.rect.centerx = 100
                    elif wy > sy:
                        self.player.rect.centery = (ROWS * TILE_SIZE) - 100
                    elif wy < sy:
                        self.player.rect.centery = 100

                    self.state = "PLAYING"
                    self.resolve_room_entry()
                    self.log("You successfully retreated!")
                else:
                    self.log("Trivia challenge passed!")
                    self.coins -= self.trivia_item_cost
                    self.grant_item(self.trivia_item_buying)
                    self.state = "SHOP"
            else:
                self.log(f"Correct! Streak: {self.trivia_current_streak}/{self.trivia_target_streak}")
                self.next_question()
        else:
            self.sound_manager.play("wrong answer")
            if self.trivia_item_buying == "PIT_SURVIVE":
                self.log("Wrong answer! You fell into the pit!")
                self.trigger_game_over("Wrong answer! You fell into the pit!")
            elif self.trivia_item_buying == "WUMPUS_RETREAT":
                self.log("Wrong answer! You panicked and couldn't escape! You are locked inside with the awake Wumpus!")
                self.state = "PLAYING"
                self.wumpus.awake = True
                self.wumpus_grace_timer = FPS * 3
                self.wumpus_chase_timer = FPS * 4
                self.wumpus.reset_position()
                self.lockdown_timer = FPS * 30
                self.wumpus_gold_timer = FPS * 6
                self.resolve_room_entry()
            else:
                self.log("Incorrect! Streak reset to 0.")
                self.trivia_current_streak = 0
                self.next_question()

    def trigger_collapse(self):
        collapsing_rooms = []
        if self.collapse_stage < 4:
            target_y = self.collapse_stage
            for x in range(MAP_COLS):
                collapsing_rooms.append((x, target_y))
        else:
            target_x = self.collapse_stage - 4
            target_y = 4
            collapsing_rooms.append((target_x, target_y))

        for room_id in collapsing_rooms:
            if room_id in self.cave:
                del self.cave[room_id]

            for rx in range(MAP_COLS):
                for ry in range(MAP_ROWS):
                    adj = (rx, ry)
                    if adj in self.cave:
                        room = self.cave[adj]
                        doors_to_remove = [d for d, target in room.doors.items() if target == room_id]
                        for d in doors_to_remove:
                            del room.doors[d]

        if self.current_room_id in collapsing_rooms:
            self.trigger_game_over("You were crushed by the collapsing cave!")
            self.log("You were crushed by the collapsing cave!")

        if getattr(self, 'wumpus_grid_pos', None) in collapsing_rooms:
            safe_rooms = list(self.cave.keys())
            if safe_rooms:
                wx, wy = self.wumpus_grid_pos
                closest = min(safe_rooms, key=lambda p: abs(p[0] - wx) + abs(p[1] - wy))
                self.wumpus_grid_pos = closest
                self.wumpus_seen_room = closest
                self.log("The Wumpus fled the collapsing cave!")

    def trigger_super_bat(self):
        possible_rooms = [r for r in self.cave.keys() if r != self.current_room_id]
        if possible_rooms:
            new_room_id = random.choice(possible_rooms)
            possible_bat_rooms = [r for r in self.cave.keys() if r != new_room_id]
            if possible_bat_rooms:
                self.super_bat_rooms.remove(self.current_room_id)
                new_bat_room = random.choice(possible_bat_rooms)
                self.super_bat_rooms.add(new_bat_room)

            self.current_room_id = new_room_id
            self.player.rect.center = (WIDTH // 2, HEIGHT // 2)
            self.log("A Super Bat grabbed you and carried you away!")
            self.sound_manager.play_bat_sound()
            self.resolve_room_entry()

    def resolve_room_entry(self):
        room = self.cave[self.current_room_id]
        self.enemies.clear()
        self.combat_manager.clear()

        self.visited_rooms.add(self.current_room_id)

        if self.current_room_id == (0, 0):
            if not room.gold_drops:
                for _ in range(random.randint(3, 5)):
                    amt = random.choice([5, 8, 10, 12, 15])
                    room.gold_drops.append({'rect': room._make_coin_rect(), 'amount': amt, 'collected': False})
            return

        if self.current_room_id in self.super_bat_rooms:
            def get_furthest_corner(player_pos):
                corners = [
                    (150, 150),
                    (WIDTH - 150, 150),
                    (150, (ROWS * TILE_SIZE) - 150),
                    (WIDTH - 150, (ROWS * TILE_SIZE) - 150)
                ]
                px, py = player_pos
                return max(corners, key=lambda c: math.hypot(c[0] - px, c[1] - py))

            cx, cy = get_furthest_corner(self.player.rect.center)
            self.enemies.append(SuperBat(cx, cy))
            self.log(">>> A majestic Super Bat is hovering here!")

        adjacent_rooms = list(room.doors.values())
        has_wumpus = False
        has_bat = False
        has_pit = False

        for adj in adjacent_rooms:
            if adj == self.wumpus_grid_pos:
                has_wumpus = True
            if adj in self.super_bat_rooms:
                has_bat = True
            if adj in self.pit_rooms:
                has_pit = True

        if has_wumpus:
            self.log(">>> I smell a Wumpus!")
        if has_bat:
            self.log(">>> Super Bat nearby, watch out for golden wings!")
        if has_pit:
            self.log(">>> I feel a draft")

        if self.current_room_id == self.wumpus_grid_pos:
            self.wumpus_seen_room = self.current_room_id
            if not self.wumpus.awake:
                self.state = "WUMPUS_PROMPT"
                self.log("You entered the room with the Wumpus! Retreat or Stay?")
                return
            else:
                self.lockdown_timer = FPS * 30
                self.wumpus_gold_timer = FPS * 6
                self.wumpus_spawn_timer = FPS * 10
        else:
            self.lockdown_timer = 0

        if self.difficulty == "EASY":
            num_small = random.randint(0, 5)
            num_big = random.randint(0, 2)
            num_bats = random.randint(0, 2)
        elif self.difficulty == "MEDIUM":
            num_small = random.randint(2, 7)
            num_big = random.randint(1, 3)
            num_bats = random.randint(1, 3)
        elif self.difficulty == "HARD":
            num_small = random.randint(4, 14)
            num_big = random.randint(2, 10)
            num_bats = random.randint(2, 6)

        if self.current_room_id == getattr(self, 'wumpus_grid_pos', None) or self.current_room_id in self.super_bat_rooms:
            num_small = 0
            num_big = 0
            num_bats = 0

        def get_corner_spawn():
            for _ in range(50):
                corner = random.choice([
                    (150, 150),
                    (WIDTH - 150, 150),
                    (150, (ROWS * TILE_SIZE) - 150),
                    (WIDTH - 150, (ROWS * TILE_SIZE) - 150)
                ])
                cx = corner[0] + random.randint(-50, 50)
                cy = corner[1] + random.randint(-50, 50)
                if math.hypot(cx - self.player.rect.centerx, cy - self.player.rect.centery) > 350:
                    return cx, cy
            return random.randint(100, WIDTH - 100), random.randint(100, (ROWS * TILE_SIZE) - 100)

        for _ in range(num_small):
            cx, cy = get_corner_spawn()
            self.enemies.append(Spider(cx, cy, is_big=False))
            self.sound_manager.play("spawn")
        for _ in range(num_big):
            cx, cy = get_corner_spawn()
            self.enemies.append(Spider(cx, cy, is_big=True))
            self.sound_manager.play("spawn")
        for _ in range(num_bats):
            cx, cy = get_corner_spawn()
            self.enemies.append(Bat(cx, cy))

        room.gold_drops = []
        num_spawns = random.choices([1, 2], weights=[0.7, 0.3])[0]
        for _ in range(num_spawns):
            r = random.random()
            if r < 0.60:
                amt = random.choice([1, 3])
            elif r < 0.90:
                amt = random.choice([4, 6])
            else:
                amt = random.choice([8, 10])
            room.gold_drops.append({'rect': room._make_coin_rect(), 'amount': amt, 'collected': False})

    def update_entities(self):
        self.transition.update()

        if getattr(self, 'warning_timer', 0) > 0:
            self.warning_timer -= 1
            if self.warning_timer <= 0:
                self.warning_timer = 0
                self.warning_messages = []

        if self.state != "PLAYING":
            return

        if hasattr(self, 'game_timer'):
            self.game_timer += 1 / FPS

        if self.wumpus.awake:
            if self.collapse_stage < 9:
                self.collapse_timer -= 1
                if self.collapse_timer <= 0:
                    self.trigger_collapse()
                    self.collapse_stage += 1
                    if self.collapse_stage < 9:
                        self.collapse_timer = FPS * 40

            if getattr(self, 'wumpus_grace_timer', 0) > 0:
                self.wumpus_grace_timer -= 1
            elif self.current_room_id != self.wumpus_grid_pos:
                self.wumpus_chase_timer -= 1
                if self.wumpus_chase_timer <= 0:
                    wx, wy = self.wumpus_grid_pos
                    px, py = self.current_room_id
                    from_dir = None
                    if wx < px:
                        wx += 1
                        from_dir = 'W'
                    elif wx > px:
                        wx -= 1
                        from_dir = 'E'
                    elif wy < py:
                        wy += 1
                        from_dir = 'N'
                    elif wy > py:
                        wy -= 1
                        from_dir = 'S'
                    self.wumpus_grid_pos = (wx, wy)
                    self.wumpus_seen_room = self.wumpus_grid_pos

                    game_mins = getattr(self, 'game_timer', 0) / 60.0
                    if self.difficulty == "HARD":
                        base_delay = 4.5
                        gain_rate = 0.5
                        min_delay = 2.0
                    elif self.difficulty == "MEDIUM":
                        base_delay = 6.0
                        gain_rate = 0.4
                        min_delay = 2.5
                    else:
                        base_delay = 7.5
                        gain_rate = 0.2
                        min_delay = 3.5

                    chase_delay = max(min_delay, base_delay - (game_mins * gain_rate))
                    self.wumpus_chase_timer = int(FPS * chase_delay)

                    if not getattr(self, 'last_wumpus_speed_alert', None) or (self.last_wumpus_speed_alert - chase_delay) >= 0.5:
                        self.log(f"ALERT: The Wumpus is getting faster! (Speed: {chase_delay:.1f}s)")
                        self.last_wumpus_speed_alert = chase_delay

                    if self.wumpus_grid_pos == self.current_room_id:
                        self.log("The Wumpus has tracked you down!")
                        self.wumpus.spawn_at_portal(from_dir)
                        self.lockdown_timer = FPS * 30
                        self.wumpus_gold_timer = FPS * 6
                        self.wumpus_spawn_timer = FPS * 10

        if self.player_invincible_timer > 0:
            self.player_invincible_timer -= 1

        if self.footstep_cooldown > 0:
            self.footstep_cooldown -= 1

        if self.bat_sound_timer > 0:
            self.bat_sound_timer -= 1

        if self.spider_sound_timer > 0:
            self.spider_sound_timer -= 1
        elif self.state == "PLAYING":
            has_spiders = any(isinstance(enemy, Spider) for enemy in self.enemies)
            if has_spiders:
                self.sound_manager.play_spider_sound()
                self.spider_sound_timer = random.randint(FPS * 4, FPS * 6)

        self.floating_text_manager.update()

        if self.lockdown_timer > 0:
            self.lockdown_timer -= 1
            if self.lockdown_timer == 0:
                self.log("Lockdown lifted! Portals opened.")

        if self.wumpus.awake:
            self.wumpus.update(self.player.rect, self.enemies)

            if self.wumpus_gold_timer > 0:
                self.wumpus_gold_timer -= 1
                if self.wumpus_gold_timer <= 0:
                    room = self.cave[self.current_room_id]
                    r = random.random()
                    if r < 0.60:
                        amt = random.choice([1, 3])
                    elif r < 0.90:
                        amt = random.choice([4, 6])
                    else:
                        amt = random.choice([8, 10])
                    new_drop = {'rect': room._make_coin_rect(), 'amount': amt, 'collected': False}
                    room.gold_drops.append(new_drop)
                    self.wumpus_gold_timer = FPS * 6
                    self.spawn_floating_text("Gold spawned!", new_drop['rect'].centerx, new_drop['rect'].top, (255, 215, 0))

            if hasattr(self, 'wumpus_spawn_timer'):
                self.wumpus_spawn_timer -= 1
                if self.wumpus_spawn_timer <= 0:
                    if self.difficulty == "EASY":
                        s_min, s_max = 0, 5
                        b_min, b_max = 0, 2
                        bat_min, bat_max = 0, 2
                    elif self.difficulty == "MEDIUM":
                        s_min, s_max = 2, 7
                        b_min, b_max = 1, 3
                        bat_min, bat_max = 1, 3
                    else:
                        s_min, s_max = 3, 6
                        b_min, b_max = 2, 4
                        bat_min, bat_max = 1, 3

                    num_small = random.randint(s_min, s_max)
                    num_big = random.randint(b_min, b_max)
                    num_bats = random.randint(bat_min, bat_max)

                    def get_corner_spawn():
                        for _ in range(50):
                            corner = random.choice([
                                (150, 150),
                                (WIDTH - 150, 150),
                                (150, (ROWS * TILE_SIZE) - 150),
                                (WIDTH - 150, (ROWS * TILE_SIZE) - 150)
                            ])
                            cx = corner[0] + random.randint(-50, 50)
                            cy = corner[1] + random.randint(-50, 50)
                            if math.hypot(cx - self.player.rect.centerx, cy - self.player.rect.centery) > 350:
                                return cx, cy
                        return random.randint(100, WIDTH - 100), random.randint(100, (ROWS * TILE_SIZE) - 100)

                    for _ in range(num_small):
                        cx, cy = get_corner_spawn()
                        self.enemies.append(Spider(cx, cy, is_big=False))
                        self.sound_manager.play("spawn")
                    for _ in range(num_big):
                        cx, cy = get_corner_spawn()
                        self.enemies.append(Spider(cx, cy, is_big=True))
                        self.sound_manager.play("spawn")
                    for _ in range(num_bats):
                        cx, cy = get_corner_spawn()
                        self.enemies.append(Bat(cx, cy))

                    self.wumpus_spawn_timer = FPS * 10
                    self.log("More enemies spawned!")

            if self.player.rect.colliderect(self.wumpus.rect):
                if self.player_invincible_timer <= 0:
                    self.player.health -= DMG_WUMPUS_TOUCH
                    self.player_invincible_timer = 60
                    self.sound_manager.play("hurt")
                    self.spawn_floating_text("-8", self.player.rect.centerx, self.player.rect.top, (255, 50, 50))
                    self.log("Wumpus crushed you!")
                    if self.player.health <= 0:
                        self.sound_manager.play("death")
                        self.trigger_game_over("Crushed by the terrifying Wumpus!")

        for enemy in self.enemies[:]:
            enemy.update(self.player.rect)

            if enemy.rect.colliderect(self.player.rect):
                if isinstance(enemy, Spider):
                    if self.player_invincible_timer <= 0:
                        dmg = 2 if enemy.is_big else 1
                        self.player.health -= dmg
                        self.player_invincible_timer = 30
                        self.sound_manager.play("hurt")
                        self.spawn_floating_text(f"-{dmg}", self.player.rect.centerx, self.player.rect.top, (255, 80, 80))
                        self.log("A spider bit you!")
                elif isinstance(enemy, Bat) and not enemy.fleeing:
                    if self.coins >= 2:
                        self.coins -= 2
                        self.spawn_floating_text("-2 Gold", self.player.rect.centerx, self.player.rect.top, (200, 200, 0))
                        self.log("A Bat stole 2 Gold!")
                        self.sound_manager.play_bat_sound()
                    enemy.fleeing = True
                    enemy.steal()
                elif isinstance(enemy, SuperBat):
                    self.enemies.remove(enemy)
                    self.trigger_super_bat()
                    return

            if enemy.rect.x < -100 or enemy.rect.x > WIDTH + 100 or enemy.rect.y < -100 or enemy.rect.y > HEIGHT + 100:
                if enemy in self.enemies:
                    self.enemies.remove(enemy)

        if self.player.health <= 0:
            self.sound_manager.play("death")
            self.trigger_game_over("Defeated by the dungeon monsters!")
            self.log("You were defeated by the monsters!")

        self.combat_manager.update_weapons()

    def grant_item(self, name):
        if name == "Normal Arrow Pack (30)":
            self.arrows += 30
            self.log("Bought Normal Arrow Pack (30 arrows)!")
        elif name == "Small Arrow Pack (5)":
            self.arrows += 5
            self.log("Bought Small Arrow Pack (5 arrows)!")
        elif name == "Explosive Arrow":
            self.explosive_arrows += 1
            self.log("Bought Explosive Arrow!")
        elif name == "TNT":
            self.tnt += 1
            self.log("Bought TNT!")
        elif name == "Light Upgrade":
            self.light_radius += LIGHT_UPGRADE_AMOUNT
            self.log("Light Radius Upgraded!")
        elif name == "Small Healing Potion":
            self.player.health = min(self.player.max_health, self.player.health + 10)
            self.log("Healed 10 Health!")
        elif name == "Big Healing Potion":
            self.player.health = min(self.player.max_health, self.player.health + 25)
            self.log("Healed 25 Health!")
        elif name == "Secret":
            if not hasattr(self, 'secrets_bought'):
                self.secrets_bought = 0
                self.secrets = []

            self.secrets_bought += 1
            for item in self.shop.items:
                if item.name == "Secret":
                    if self.secrets_bought == 1:
                        item.gold_cost = 20
                    elif self.secrets_bought == 2:
                        item.gold_cost = 40

            wx, wy = getattr(self, 'wumpus_grid_pos', (0, 0))
            is_row = random.choice([True, False])
            if is_row:
                offset = random.choice([-3, -2, -1, 0, 1, 2, 3])
                target_y = min(max(0, wy + offset), MAP_ROWS - 1)
                self.secrets.append({'type': 'row', 'index': target_y})
                self.log(f"Secret bought! Wumpus is near Row {target_y}")
            else:
                offset = random.choice([-3, -2, -1, 0, 1, 2, 3])
                target_x = min(max(0, wx + offset), MAP_COLS - 1)
                self.secrets.append({'type': 'col', 'index': target_x})
                self.log(f"Secret bought! Wumpus is near Column {target_x}")
        elif name == "Teleportation":
            if not hasattr(self, 'teleports_bought'):
                self.teleports_bought = 0
            self.teleports_bought += 1
            self.state = "TELEPORT_SELECT"
            self.log("Click on the minimap to teleport!")
