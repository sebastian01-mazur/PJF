# engine/game_manager.py
import pygame
import random
import os
from settings import *
from engine.card import Card, CARD_DB
from engine.player import Player
from engine.board import Location


class GameManager:
    def __init__(self, app):
        self.app = app

        # --- UI ---
        self.btn_menu = pygame.Rect(0, 0, 0, 0)

        # Tło
        self.bg_original = None
        self.bg_image = None

        # --- ZASOBY GRAFICZNE ---
        self.res_images = {}  # Do lokacji (duże)
        self.res_icons = {}  # Do UI (małe)

        self.locations = []

        # 1. Ładowanie Tła
        try:
            self.bg_original = pygame.image.load("assets/bg.PNG")
        except FileNotFoundError:
            print("Brak tła assets/bg.PNG")

        # 2. Ładowanie Obrazków Surowców
        # Mapowanie: nazwa w kodzie -> nazwa pliku
        files = {
            "twig": "twigs.png",
            "resin": "resin.png",
            "pebble": "stones.png",
            "berry": "berries.png"
        }

        for res_key, filename in files.items():
            path = os.path.join("assets", filename)
            if os.path.exists(path):
                img = pygame.image.load(path)
                # Skalowanie dla lokacji (140x90)
                self.res_images[res_key] = pygame.transform.smoothscale(img, (140, 90))
                # Skalowanie dla UI (30x30)
                self.res_icons[res_key] = pygame.transform.smoothscale(img, (30, 30))
            else:
                print(f"Brak pliku: {path}")
                self.res_images[res_key] = None
                self.res_icons[res_key] = None

        # Inicjalizacja gry
        source = CARD_DB * 4
        random.shuffle(source)
        self.deck = [Card(d) for d in source]

        self.players = [Player("Gracz 1", P1_COLOR), Player("Gracz 2", P2_COLOR)]
        self.turn_idx = 0

        for p in self.players:
            for _ in range(5):
                if self.deck: p.hand.append(self.deck.pop())

        self.meadow = []
        self.refill_meadow()

        self.info_msg = "Zaczyna Gracz 1 (ZIMA)."

        self.update_layout()

    def update_layout(self):
        w = self.app.width
        h = self.app.height

        if self.bg_original:
            self.bg_image = pygame.transform.scale(self.bg_original, (w, h))

        self.btn_menu = pygame.Rect(w - 110, 10, 100, 40)

        # --- TWORZENIE LOKACJI Z OBRAZKAMI ---
        total_loc_width = 6 * 150
        start_x = (w - total_loc_width) // 2
        y = 100

        # Definicje: (Nazwa, Zysk, CzyEkskluzywne, KluczObrazka)
        loc_defs = [
            ("Brzeg (2 Gałązki)", {"twig": 2}, True, "twig"),
            ("Las (3 Gałązki)", {"twig": 3}, True, "twig"),
            ("Żywica (2 Żywice)", {"resin": 2}, True, "resin"),
            ("Kamyki (1 Kamyk)", {"pebble": 1}, True, "pebble"),
            ("Krzaki (1 Jagoda)", {"berry": 1}, True, "berry"),
            ("Polana (2 Karty)", {"cards": 2}, False, None)  # Brak obrazka dla kart
        ]

        if not self.locations:
            for i, (name, gain, excl, img_key) in enumerate(loc_defs):
                rect = pygame.Rect(start_x + (i * 150), y, 140, 90)
                # Pobierz obrazek jeśli istnieje
                img = self.res_images.get(img_key) if img_key else None
                self.locations.append(Location(name, rect.x, rect.y, gain, excl, image=img))
        else:
            for i, loc in enumerate(self.locations):
                loc.rect.x = start_x + (i * 150)
                loc.rect.y = y

    @property
    def current_player(self):
        return self.players[self.turn_idx]

    def refill_meadow(self):
        while len(self.meadow) < 8 and self.deck:
            self.meadow.append(self.deck.pop())

    def next_turn(self):
        if self.players[0].finished and self.players[1].finished:
            self.calc_winner()
            return

        self.turn_idx = (self.turn_idx + 1) % 2
        if self.current_player.finished:
            self.turn_idx = (self.turn_idx + 1) % 2

        p = self.current_player
        self.info_msg = f"Tura: {p.name} ({p.season})"

    def calc_winner(self):
        res = []
        for p in self.players:
            pts = sum(c.points for c in p.city)
            res.append(f"{p.name}: {pts}")
        self.info_msg = "KONIEC: " + " vs ".join(res)

    def prepare_season(self):
        p = self.current_player
        for loc in self.locations:
            if loc.occupant == p: loc.occupant = None

        if p.season == "ZIMA":
            p.season = "WIOSNA";
            p.workers_total += 1
            p.activate_production()
        elif p.season == "WIOSNA":
            p.season = "LATO";
            p.workers_total += 1
            if self.deck: p.hand.append(self.deck.pop())
            if self.deck: p.hand.append(self.deck.pop())
        elif p.season == "LATO":
            p.season = "JESIEŃ";
            p.workers_total += 2
            p.activate_production()
        elif p.season == "JESIEŃ":
            p.finished = True
            p.workers_total = 0
            self.next_turn()
            return

        p.workers_available = p.workers_total
        self.info_msg = f"{p.name}: Sezon {p.season} rozpoczęty!"
        self.next_turn()

    def handle_click(self, pos):
        if self.btn_menu.collidepoint(pos):
            self.app.change_state("MENU")
            return

        if "KONIEC" in self.info_msg: return
        p = self.current_player
        w, h = self.app.width, self.app.height

        # Sezon
        btn_season = pygame.Rect(w - 220, h - 60, 200, 40)
        if btn_season.collidepoint(pos):
            if p.workers_available == 0:
                self.prepare_season()
            else:
                self.info_msg = "Masz jeszcze robotników!"
            return

        # Lokacje
        if p.workers_available > 0:
            for loc in self.locations:
                if loc.rect.collidepoint(pos):
                    if loc.exclusive and loc.occupant:
                        self.info_msg = "Zajęte!"
                        return
                    if "cards" in loc.gain:
                        for _ in range(loc.gain["cards"]):
                            if self.deck: p.hand.append(self.deck.pop())
                    else:
                        for r, a in loc.gain.items(): p.resources[r] += a

                    if loc.exclusive: loc.occupant = p
                    p.workers_available -= 1
                    self.next_turn()
                    return

        # Karty
        for i, card in enumerate(self.meadow):
            if card.rect and card.rect.collidepoint(pos):
                self.buy_card(p, card, "MEADOW", i)
                return

        start_x = 20;
        hand_y = h - 170
        for i, card in enumerate(p.hand):
            rect = pygame.Rect(start_x + (i * 110), hand_y, 100, 140)
            if rect.collidepoint(pos):
                self.buy_card(p, card, "HAND", i)
                return

    def buy_card(self, p, card, source, index):
        if len(p.city) >= 15:
            self.info_msg = "Miasto pełne!"
            return
        if p.can_afford(card):
            p.pay(card)
            p.city.append(card)
            if card.type == "PROD":
                for r, a in card.benefit.items(): p.resources[r] += a
            if source == "MEADOW":
                self.meadow.pop(index);
                self.refill_meadow()
            else:
                p.hand.pop(index)
            self.info_msg = f"Zbudowano {card.name}"
            self.next_turn()
        else:
            self.info_msg = "Brak surowców!"

    def draw(self):
        screen = self.app.screen
        w, h = self.app.width, self.app.height

        if self.bg_image:
            screen.blit(self.bg_image, (0, 0))
        else:
            screen.fill(BG_COLOR)
        font = self.app.font

        # Menu Btn
        pygame.draw.rect(screen, (150, 50, 50), self.btn_menu, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.btn_menu, 2, border_radius=5)
        txt = font.render("MENU", True, WHITE)
        screen.blit(txt, txt.get_rect(center=self.btn_menu.center))

        for loc in self.locations: loc.draw(screen, font)

        # Łąka
        meadow_y = 220
        start_mx = (w - (8 * 110)) // 2
        s = pygame.Surface((w, 160));
        s.set_alpha(150);
        s.fill((0, 0, 0))
        screen.blit(s, (0, meadow_y))

        for i, card in enumerate(self.meadow):
            card.draw_visual(screen, start_mx + (i * 110), meadow_y + 10, font)

        # Panel UI
        p = self.current_player
        py = h - 200
        pygame.draw.rect(screen, UI_PANEL_COLOR, (0, py, w, 200))
        pygame.draw.line(screen, p.color, (0, py), (w, py), 5)
        screen.blit(self.app.title_font.render(self.info_msg, True, WHITE), (20, py + 10))

        # SUROWCE (Teraz z ikonkami!)
        rx = 20;
        ry = py + 50
        for res_key in ["twig", "resin", "pebble", "berry"]:
            icon = self.res_icons.get(res_key)
            if icon:
                screen.blit(icon, (rx, ry - 15))
            else:
                # Fallback kółko
                pygame.draw.circle(screen, RES_COLORS.get(res_key), (rx + 15, ry), 10)

            screen.blit(font.render(str(p.resources[res_key]), True, WHITE), (rx + 35, ry - 10))
            rx += 80  # Zwiększony odstęp bo ikonki są szersze

        screen.blit(font.render(f"Robotnicy: {p.workers_available}/{p.workers_total}", True, WHITE), (rx + 20, ry - 10))

        hx = 20;
        hy = py + 80
        for i, card in enumerate(p.hand):
            card.draw_visual(screen, hx + (i * 110), hy, font)

        bs_rect = pygame.Rect(w - 220, h - 60, 200, 40)
        col = (100, 100, 100)
        if p.workers_available == 0 and not p.finished: col = (50, 150, 50)
        pygame.draw.rect(screen, col, bs_rect, border_radius=8)
        screen.blit(font.render("NASTĘPNA PORA", True, WHITE), (bs_rect.x + 30, bs_rect.y + 10))