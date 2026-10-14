import pygame
from config import WIDTH, HEIGHT

class ShopItem:
    def __init__(self, name, gold_cost, trivia_cost, description):
        self.name = name
        self.gold_cost = gold_cost
        self.trivia_cost = trivia_cost
        self.description = description

class Shop:
    def __init__(self):
        self.items = [
            ShopItem("Small Healing Potion", 5, 0, "Heals 10 Health."),
            ShopItem("Big Healing Potion", 15, 0, "Heals 25 Health."),
            ShopItem("Normal Arrow Pack (30)", 15, 2, "Buy 30 arrows. Get at least 2 correct in a row out of 3 questions."),
            ShopItem("Small Arrow Pack (5)", 3, 2, "Buy 5 arrows. Same trivia rules as the 30 pack."),
            ShopItem("Explosive Arrow", 3, 0, "No trivia required to buy."),
            ShopItem("TNT", 7, 4, "Answer 4 trivia in a row to buy."),
            ShopItem("Light Upgrade", 20, 0, "Increase Light Radius permanently."),
            ShopItem("Secret", 10, 0, "Reveals a hint about the Wumpus's location."),
            ShopItem("Teleportation", 10, 0, "Click the minimap to teleport anywhere.")
        ]
        self.selected_idx = 0
        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 16)

    def selected_item(self):
        return self.items[self.selected_idx]

    def handle_input(self, event, game):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_e or event.key == pygame.K_ESCAPE:
            game.sound_manager.play("menu select")
            game.state = "PLAYING"
        elif event.key in [pygame.K_w, pygame.K_UP]:
            game.sound_manager.play("menu move cursor")
            self.selected_idx = max(0, self.selected_idx - 1)
        elif event.key in [pygame.K_s, pygame.K_DOWN]:
            game.sound_manager.play("menu move cursor")
            self.selected_idx = min(len(self.items) - 1, self.selected_idx + 1)
        elif event.key == pygame.K_RETURN:
            game.sound_manager.play("menu select")
            self.try_buy_selected(game)

    def try_buy_selected(self, game):
        item = self.selected_item()
        if game.coins < item.gold_cost:
            game.log("Not enough gold!")
            return

        if item.name == "Secret":
            if getattr(game, 'wumpus_seen_room', None) is not None:
                game.log("Wumpus location already discovered!")
                return
            if getattr(game, 'wumpus', None) and game.wumpus.awake:
                game.log("Cannot buy secrets while Wumpus is awake!")
                return
            if getattr(game, 'secrets_bought', 0) >= 3:
                game.log("No more secrets available!")
                return

        if item.name == "Teleportation" and getattr(game, 'teleports_bought', 0) >= 3:
            game.log("No more teleports available!")
            return

        if item.trivia_cost > 0:
            game.start_buying_trivia(item.name, item.trivia_cost, item.gold_cost)
        else:
            game.coins -= item.gold_cost
            game.grant_item(item.name)

    def draw(self, screen, game):
        coins = game.coins
        teleports_bought = getattr(game, 'teleports_bought', 0)
        secrets_bought = getattr(game, 'secrets_bought', 0)

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(230)
        overlay.fill((20, 15, 30))
        screen.blit(overlay, (0, 0))

        title = self.font.render("--- THE WEAPONS DEALER ---", True, (240, 200, 100))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        
        gold_txt = self.font.render(f"Your Gold: {coins}", True, (240, 240, 50))
        screen.blit(gold_txt, (WIDTH // 2 - gold_txt.get_width() // 2, 90))

        for i, item in enumerate(self.items):
            color = (255, 255, 255) if i == self.selected_idx else (150, 150, 150)
            prefix = ">> " if i == self.selected_idx else "   "
            
            name_display = item.name
            if item.name == "Teleportation":
                rem = 3 - teleports_bought
                if rem <= 0:
                    name_display = f"{item.name} [SOLD OUT]"
                    color = (100, 100, 100) if i != self.selected_idx else (180, 180, 180)
                else:
                    name_display = f"{item.name} ({rem} left)"
            elif item.name == "Secret":
                rem = 3 - secrets_bought
                if rem <= 0:
                    name_display = f"{item.name} [SOLD OUT]"
                    color = (100, 100, 100) if i != self.selected_idx else (180, 180, 180)
                else:
                    name_display = f"{item.name} ({rem} left)"

            text = f"{prefix}{name_display} - {item.gold_cost} Gold, {item.trivia_cost} Trivia streak required"
            if item.trivia_cost == 0:
                text = f"{prefix}{name_display} - {item.gold_cost} Gold"

            item_render = self.font.render(text, True, color)
            screen.blit(item_render, (100, 150 + i * 60))
            
            desc_render = self.small_font.render(item.description, True, (120, 120, 150))
            screen.blit(desc_render, (130, 175 + i * 60))

        help_txt = self.small_font.render("W/S to navigate | ENTER to buy | E or ESC to exit", True, (100, 100, 100))
        screen.blit(help_txt, (WIDTH // 2 - help_txt.get_width() // 2, HEIGHT - 50))
