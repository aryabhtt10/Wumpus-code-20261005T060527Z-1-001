import os
import random

from config import *
from core.room import Room
from core.player import Player
from core.wumpus import Wumpus
from systems.shop import Shop
from core.particle import TransitionEffect
from systems.trivia import random_question


class EngineSetupMixin:
    def setup_game(self):
        self.cave = {(x, y): Room(x, y) for x in range(MAP_COLS) for y in range(MAP_ROWS)}
        for room in self.cave.values():
            room.add_doors_to_grid()

        self.current_room_id = (0, 0)
        self.last_safe_room = self.current_room_id
        self.is_first_room = True
        self.message_log = ["Welcome to the Cave system!\nWatch your step."]

        w_x = random.randint(0, MAP_COLS - 1)
        w_y = random.randint(0, MAP_ROWS - 1)
        while (w_x, w_y) == self.current_room_id:
            w_x = random.randint(0, MAP_COLS - 1)
            w_y = random.randint(0, MAP_ROWS - 1)
        self.wumpus_grid_pos = (w_x, w_y)
        self.wumpus.awake = False

        self.player_name_input = ""
        self.score_saved = False
        self.death_reason = ""
        self.asked_trivia = set()

        self.super_bat_rooms = set()
        while len(self.super_bat_rooms) < 2:
            bx = random.randint(0, MAP_COLS - 1)
            by = random.randint(0, MAP_ROWS - 1)
            if (bx, by) != self.current_room_id and (bx, by) != self.wumpus_grid_pos:
                self.super_bat_rooms.add((bx, by))

        if self.difficulty == "EASY":
            pit_chance = 0.05
        elif self.difficulty == "MEDIUM":
            pit_chance = 0.08
        else:
            pit_chance = 0.11

        self.pit_rooms = set()
        for px in range(MAP_COLS):
            for py in range(MAP_ROWS):
                if (px, py) != self.current_room_id and (px, py) != self.wumpus_grid_pos:
                    if random.random() < pit_chance:
                        self.pit_rooms.add((px, py))

        print(f"\n[DEBUG] WUMPUS POSITION  : {self.wumpus_grid_pos}")
        print(f"[DEBUG] SUPER BAT ROOMS  : {self.super_bat_rooms}")
        print(f"[DEBUG] PIT ROOMS        : {self.pit_rooms}\n")

        self.player = Player()
        self.player_invincible_timer = 0
        self.combat_manager.clear()
        self.enemies = []
        self.floating_text_manager.clear()
        self.load_scores()
        self.arrows = 3
        self.explosive_arrows = 0
        self.tnt = 0
        self.coins = 0
        self.light_radius = BASE_LIGHT_RADIUS

        self.turns = 0
        self.shoot_cooldown = 0
        self.footstep_cooldown = 0
        self.bat_sound_timer = 0
        self.spider_sound_timer = 0
        self.lockdown_timer = 0
        self.wumpus_gold_timer = 0
        self.room_cleared = {}

        self.visited_rooms = set()
        self.wumpus_seen_room = None
        self.wumpus_chase_timer = 0
        self.wumpus_grace_timer = 0

        self.game_timer = 0
        self.multiplier_applied = False
        self.collapse_stage = 0
        self.collapse_timer = FPS * 40
        self.teleports_bought = 0
        self.secrets_bought = 0
        self.secrets = []
        self.info_tab = "INSTRUCTIONS"
        for item in self.shop.items:
            if item.name == "Secret":
                item.gold_cost = 10

        self.state = "PLAYING"
        self.wumpus.hp = {"EASY": 30, "MEDIUM": 50, "HARD": 75}[self.difficulty]
        self.resolve_room_entry()

    def trigger_game_over(self, reason):
        self.state = "GAMEOVER"
        self.death_reason = reason

    def log(self, msg):
        if msg.startswith(">>>"):
            warning_text = msg.lstrip('>').strip()
            self.warning_messages.append(warning_text)
            self.warning_timer = getattr(self, 'warning_duration', FPS)
            if len(self.warning_messages) > 4:
                self.warning_messages.pop(0)

        self.message_log.append(msg)
        if len(self.message_log) > 4:
            self.message_log.pop(0)

    def load_scores(self):
        self.high_scores = []
        try:
            if os.path.exists("scores.txt"):
                with open("scores.txt", "r") as f:
                    lines = f.readlines()
                for l in lines:
                    l = l.strip()
                    if not l:
                        continue
                    parts = l.split(",")
                    if len(parts) == 7:
                        try:
                            name = parts[0]
                            score = int(parts[1])
                            turns = int(parts[2])
                            gold = int(parts[3])
                            arrows = int(parts[4])
                            wumpus_killed = int(parts[5])
                            cave = parts[6]
                            self.high_scores.append({
                                "name": name,
                                "score": score,
                                "turns": turns,
                                "gold": gold,
                                "arrows": arrows,
                                "wumpus_killed": wumpus_killed,
                                "cave": cave
                            })
                        except ValueError:
                            pass
                    elif l.isdigit():
                        self.high_scores.append({
                            "name": "Unknown",
                            "score": int(l),
                            "turns": 0,
                            "gold": 0,
                            "arrows": 0,
                            "wumpus_killed": 0,
                            "cave": "MEDIUM"
                        })
                self.high_scores = sorted(self.high_scores, key=lambda x: x["score"], reverse=True)[:10]
        except Exception:
            pass

    def save_score(self, player_name=None):
        if not player_name:
            player_name = "Player"
        player_name = player_name.replace(",", " ").strip()
        if not player_name:
            player_name = "Player"

        n_turns = self.turns
        g_coins = self.coins
        a_arrows = self.arrows + self.explosive_arrows
        w_bonus = 50 if self.state == "VICTORY" else 0
        final_score = 100 - n_turns + g_coins + 5 * a_arrows + w_bonus
        cave = self.difficulty

        try:
            with open("scores.txt", "a") as f:
                f.write(f"{player_name},{final_score},{n_turns},{g_coins},{a_arrows},{w_bonus},{cave}\n")
            self.load_scores()
            self.score_saved = True
        except Exception:
            pass

    def spawn_floating_text(self, text, x, y, color):
        self.floating_text_manager.spawn_text(text, x, y, color)

    def add_score(self, amount):
        self.score += amount
        self.floating_text_manager.spawn_score(amount)

    def start_buying_trivia(self, item_name, streak_required, gold_cost):
        self.state = "TRIVIA"
        self.trivia_target_streak = streak_required
        self.trivia_current_streak = 0
        self.trivia_item_buying = item_name
        self.trivia_item_cost = gold_cost
        if item_name in ["Normal Arrow Pack (30)", "Small Arrow Pack (5)"]:
            self.trivia_questions_asked = 0
            self.trivia_max_consecutive_correct = 0
        self.next_question()

    def next_question(self):
        if not hasattr(self, 'asked_trivia'):
            self.asked_trivia = set()
        self.current_q = random_question(self.difficulty.lower(), self.asked_trivia)
        # reset any previous hint when moving to a new question
        self.current_hint = None
        self.hint_reveal_index = 0
        self.hint_reveal_tick = 0
        # Debug: print the loaded question and hint (if any)
        try:
            qtxt = self.current_q.get('q') if self.current_q else None
            hint = self.current_q.get('hint') if self.current_q else None
            print(f"[DEBUG] next_question loaded q='{qtxt}' hint='{hint}'")
        except Exception:
            print("[DEBUG] next_question: failed to print question/hint")
