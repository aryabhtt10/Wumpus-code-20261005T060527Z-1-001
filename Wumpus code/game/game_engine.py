import pygame

from config import *
from systems.asset_loader import load_image
from core.player import Player
from core.wumpus import Wumpus
from systems.shop import Shop
from core.particle import TransitionEffect
from systems.sound_manager import SoundManager
from systems.effects import FloatingTextManager
from ui.renderer import GameRenderer
from systems.combat import CombatManager
from mixins.engine_setup import EngineSetupMixin
from mixins.engine_input import InputMixin
from mixins.engine_logic import LogicMixin
from mixins.engine_run import RunMixin


class GameEngine(EngineSetupMixin, InputMixin, LogicMixin, RunMixin):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Hunt The Wumpus - Overhaul")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.warning_font = pygame.font.SysFont("Arial", 20, bold=True)
        self.big_font = pygame.font.SysFont("Arial", 32, bold=True)
        self.sub_font = pygame.font.SysFont("Arial", 15, bold=False)
        self.handbook_font = pygame.font.SysFont("Arial", 18, bold=False)

        self.state = "MENU"
        self.difficulty = "MEDIUM"
        self.message_log = ["Welcome to the Cave system!\nWatch your step."]
        self.warning_messages = []
        self.warning_timer = 0
        self.warning_duration = FPS*3

        self.player = Player()
        self.player_invincible_timer = 0
        self.wumpus = Wumpus()
        self.wumpus.hp = 100

        self.enemies = []
        self.lockdown_timer = 0
        self.transition = TransitionEffect()
        self.wumpus_gold_timer = 0

        self.visited_rooms = set()
        self.wumpus_seen_room = None
        self.wumpus_grid_pos = None
        self.wumpus_chase_timer = 0
        self.wumpus_grace_timer = 0

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
        self.last_safe_room = (0, 0)

        self.room_cleared = {}

        self.shop = Shop()
        self.trivia_target_streak = 0
        self.trivia_current_streak = 0
        self.trivia_item_buying = None
        self.trivia_item_cost = 0
        self.current_q = None
        self.current_hint = None
        self.hint_reveal_index = 0
        self.hint_reveal_tick = 0
        self.teleports_bought = 0
        self.secrets_bought = 0
        self.secrets = []
        self.info_tab = "INSTRUCTIONS"
        self.asked_trivia = set()

        self.super_bat_rooms = set()
        self.pit_rooms = set()
        self.player_name_input = ""
        self.score_saved = False
        self.death_reason = ""

        self.bg_image = load_image("cave.png", (WIDTH, HEIGHT))
        self.player_img = load_image("player.png", (64, 64))
        self.wumpus_img = load_image("wumpus.png", (100, 100))
        self.arrow_img = load_image("arrow.png", (54, 54))

        self.aura_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        self.sound_manager = SoundManager()
        self.score = 0
        self.floating_text_manager = FloatingTextManager()
        self.combat_manager = CombatManager(self)
        self.renderer = GameRenderer(self)

    def draw(self):
        self.renderer.draw()
