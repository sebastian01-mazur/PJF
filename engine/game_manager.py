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
        self.images_db = {}  # Lokacje
        self.res_icons = {}  # UI
        self.images_res = {}  # Surowce
        self.card_images = {}  # Karty

        self.locations = []

        # Wymiary
        self.LOC_W = 110
        self.LOC_H = 160
        self.LOC_GAP = 20

        # 1. Ładowanie Tła
        try:
            self.bg_original = pygame.image.load("assets/bg.PNG")
        except FileNotFoundError:
            pass

            # 2. Ładowanie Obrazków Lokalizacji
        files_map = {
            "brzeg": "brzeg.png",
            "las": "las.png",
            "zywica": "zywica.png",
            "kamyki": "kamyki.png",
            "krzaki": "krzaki.png",
            "polana": "polana.png"
        }
        for key, filename in files_map.items():
            path = os.path.join("assets", filename)
            if os.path.exists(path):
                raw_img = pygame.image.load(path)
                self.images_db[key] = pygame.transform.smoothscale(raw_img, (self.LOC_W, self.LOC_H))
            else:
                self.images_db[key] = None

        # 3. Ładowanie Ikon Surowców
        files_res = {
            "twig": "twigs.png",
            "resin": "resin.png",
            "pebble": "stones.png",
            "berry": "berries.png"
        }
        for key, filename in files_res.items():
            path = os.path.join("assets", filename)
            if os.path.exists(path):
                raw_img = pygame.image.load(path)
                self.images_res[key] = pygame.transform.smoothscale(raw_img, (30, 30))
            else:
                self.images_res[key] = None

        # 4. ŁADOWANIE GRAFIK KART
        cards_files = {
            "Farma": "farm.png",
            "Sklep": "shop.png",
            "Zamek": "castle.png",
            "Król": "king.png",
            "Mąż": "mar.png",
            "Żona": "mar.png",
            "Sędzia": "judge.png",
            "Historyk": "history.png",
            "Karczmarz": "innkeeper.png",
            "Kupiec": "shopkeeper.png",
            "Rezydencja": "res.png"
        }

        CARD_W, CARD_H = 100, 140

        for name, filename in cards_files.items():
            path = os.path.join("assets", filename)
            if os.path.exists(path):
                img = pygame.image.load(path)
                self.card_images[name] = pygame.transform.smoothscale(img, (CARD_W, CARD_H))
            else:
                self.card_images[name] = None

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

        self.btn_menu = pygame.Rect(w - 120, 10, 110, 40)

        total_width = (6 * self.LOC_W) + (5 * self.LOC_GAP)
        start_x = (w - total_width) // 2
        y = 60

        loc_defs = [
            ("Brzeg (2 Gałązki)", {"twig": 2}, True, "brzeg"),
            ("Las (3 Gałązki)", {"twig": 3}, True, "las"),
            ("Żywica (2 Żywice)", {"resin": 2}, True, "zywica"),
            ("Kamyki (1 Kamyk)", {"pebble": 1}, True, "kamyki"),
            ("Krzaki (1 Jagoda)", {"berry": 1}, True, "krzaki"),
            ("Polana (2 Karty)", {"cards": 2}, False, "polana")
        ]

        if not self.locations:
            for i, (name, gain, excl, img_key) in enumerate(loc_defs):
                current_x = start_x + (i * (self.LOC_W + self.LOC_GAP))
                rect = pygame.Rect(current_x, y, self.LOC_W, self.LOC_H)
                img = self.images_db.get(img_key)
                self.locations.append(Location(name, rect.x, rect.y, gain, excl, image=img))
                self.locations[-1].rect.width = self.LOC_W
                self.locations[-1].rect.height = self.LOC_H
        else:
            for i, loc in enumerate(self.locations):
                current_x = start_x + (i * (self.LOC_W + self.LOC_GAP))
                loc.rect.x = current_x
                loc.rect.y = y
                loc.rect.width = self.LOC_W
                loc.rect.height = self.LOC_H

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
            if p.activate_production():
                self.info_msg = "Wiosna: Produkcja aktywna!"
        elif p.season == "WIOSNA":
            p.season = "LATO";
            p.workers_total += 1
            if self.deck: p.hand.append(self.deck.pop())
            if self.deck: p.hand.append(self.deck.pop())
        elif p.season == "LATO":
            p.season = "JESIEŃ";
            p.workers_total += 2
            if p.activate_production():
                self.info_msg = "Jesień: Produkcja aktywna!"
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

        btn_season = pygame.Rect(w - 220, h - 60, 200, 40)
        if btn_season.collidepoint(pos):
            if p.workers_available == 0:
                self.prepare_season()
            else:
                self.info_msg = "Masz jeszcze robotników!"
            return

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
            is_free = p.pay(card)

            trigger_msgs = []
            if hasattr(p, 'check_triggers'):
                trigger_msgs = p.check_triggers(card)

            for msg in trigger_msgs:
                if "DRAW_CARD" in msg:
                    try:
                        count = int(msg.split(":")[1])
                        for _ in range(count):
                            if self.deck: p.hand.append(self.deck.pop())
                    except:
                        pass

            p.city.append(card)

            if card.type == "PROD":
                for r, a in card.benefit.items(): p.resources[r] += a

            if source == "MEADOW":
                self.meadow.pop(index);
                self.refill_meadow()
            else:
                p.hand.pop(index)

            bonus_txt = " +Bonus!" if trigger_msgs else ""
            if is_free:
                self.info_msg = f"Zbudowano {card.name} (DARMO){bonus_txt}"
            else:
                self.info_msg = f"Zbudowano {card.name}{bonus_txt}"

            self.next_turn()
        else:
            self.info_msg = "Brak surowców lub budynku do pary!"

    # --- NOWA FUNKCJA DO RYSOWANIA TOOLTIPA ---
    def draw_hover_tooltip(self, screen, card, mouse_pos):
        font_bold = pygame.font.SysFont("Arial", 14, bold=True)
        font_reg = pygame.font.SysFont("Arial", 14)

        # Tłumaczenie kodów surowców na język polski (dla estetyki)
        res_trans = {"twig": "Drewno", "resin": "Żywica", "pebble": "Kamyk", "berry": "Jagoda"}

        # 1. Przygotowanie treści
        lines = []
        lines.append((card.name, (255, 215, 0)))  # Nazwa na złoto
        lines.append((f"Typ: {card.tag} / {card.type}", (200, 200, 200)))

        # Koszt
        cost_str = []
        for r, a in card.cost.items():
            name_pl = res_trans.get(r, r)
            cost_str.append(f"{a} {name_pl}")
        lines.append((f"Koszt: {', '.join(cost_str)}", (255, 150, 150)))

        # Opis działania
        lines.append(("Efekt:", (150, 255, 150)))
        lines.append((card.desc, (255, 255, 255)))

        # Combo / Linki
        if card.link:
            lines.append((f"Symbol: {card.link}", (100, 200, 255)))
        if card.link_req:
            lines.append((f"Wymaga: {card.link_req} (do pary)", (255, 100, 255)))

        # 2. Obliczenie wymiarów okienka
        box_w = 260
        box_h = 20 + (len(lines) * 20)

        x, y = mouse_pos
        x += 15  # Przesunięcie żeby myszka nie zasłaniała
        y += 15

        # Zabezpieczenie przed wyjściem za ekran
        if x + box_w > self.app.width: x -= box_w + 30
        if y + box_h > self.app.height: y -= box_h + 30

        # 3. Rysowanie
        # Tło półprzezroczyste
        s = pygame.Surface((box_w, box_h))
        s.set_alpha(230)
        s.fill((20, 20, 30))
        screen.blit(s, (x, y))

        # Ramka
        pygame.draw.rect(screen, (100, 100, 100), (x, y, box_w, box_h), 2)

        # Tekst
        curr_y = y + 10
        for text, color in lines:
            surf = font_bold.render(text, True, color) if text == card.name else font_reg.render(text, True, color)
            screen.blit(surf, (x + 10, curr_y))
            curr_y += 20

    def draw(self):
        screen = self.app.screen
        w, h = self.app.width, self.app.height
        mouse_pos = pygame.mouse.get_pos()

        if self.bg_image:
            screen.blit(self.bg_image, (0, 0))
        else:
            screen.fill(BG_COLOR)
        font = self.app.font

        # MENU
        pygame.draw.rect(screen, (150, 50, 50), self.btn_menu, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.btn_menu, 2, border_radius=5)
        txt = font.render("MENU", True, WHITE)
        screen.blit(txt, txt.get_rect(center=self.btn_menu.center))

        for loc in self.locations: loc.draw(screen, font)

        p = self.current_player

        # Zmienna do przechowywania karty pod myszką
        hovered_card = None

        # Łąka
        meadow_y = 240
        start_mx = (w - (8 * 110)) // 2

        for i, card in enumerate(self.meadow):
            bonus_name = None
            if hasattr(p, 'check_bonus_potential'):
                bonus_name = p.check_bonus_potential(card.tag)

            img = self.card_images.get(card.name)
            card.draw_visual(screen, start_mx + (i * 110), meadow_y + 10, font, bonus_source=bonus_name, image=img)

            # Sprawdzenie hovera
            if card.rect and card.rect.collidepoint(mouse_pos):
                hovered_card = card

        # Panel UI
        py = h - 200
        pygame.draw.rect(screen, UI_PANEL_COLOR, (0, py, w, 200))
        pygame.draw.line(screen, p.color, (0, py), (w, py), 5)
        screen.blit(self.app.title_font.render(self.info_msg, True, WHITE), (20, py + 10))

        # SUROWCE
        rx = 20;
        ry = py + 50
        res_types = ["twig", "resin", "pebble", "berry"]
        for res_key in res_types:
            icon = self.images_res.get(res_key)
            if icon:
                screen.blit(icon, (rx, ry - 15))
            else:
                col = RES_COLORS.get(res_key, (255, 255, 255))
                pygame.draw.circle(screen, col, (rx + 15, ry), 10)

            screen.blit(font.render(str(p.resources[res_key]), True, WHITE), (rx + 35, ry - 10))
            rx += 80

        screen.blit(font.render(f"Robotnicy: {p.workers_available}/{p.workers_total}", True, WHITE), (rx + 20, ry - 10))
        score_text = font.render(f"PUNKTY: {p.score}", True, (255, 215, 0))
        screen.blit(score_text, (rx + 150, ry - 10))

        # WIDOK MIASTA
        city_start_y = 150
        city_x = 20
        title_city = font.render(f"TWOJE MIASTO ({len(p.city)}/15):", True, (255, 255, 200))
        screen.blit(title_city, (city_x, city_start_y - 25))

        for i, built_card in enumerate(p.city):
            c_col = (200, 200, 200)
            if built_card.type == "PROD":
                c_col = (150, 255, 150)
            elif built_card.type == "PASSIVE":
                c_col = (150, 150, 255)
            card_name = font.render(f"- {built_card.name}", True, c_col)
            screen.blit(card_name, (city_x, city_start_y + (i * 20)))

        # RĘKA
        hx = 20;
        hy = py + 80
        for i, card in enumerate(p.hand):
            bonus_name = None
            if hasattr(p, 'check_bonus_potential'):
                bonus_name = p.check_bonus_potential(card.tag)

            img = self.card_images.get(card.name)
            card.draw_visual(screen, hx + (i * 110), hy, font, bonus_source=bonus_name, image=img)

            # Sprawdzenie hovera
            if card.rect and card.rect.collidepoint(mouse_pos):
                hovered_card = card

        # NA SAMYM KOŃCU: JEŚLI JEST HOVER, RYSUJ OKIENKO
        if hovered_card:
            self.draw_hover_tooltip(screen, hovered_card, mouse_pos)

        bs_rect = pygame.Rect(w - 220, h - 60, 200, 40)
        col = (100, 100, 100)
        if p.workers_available == 0 and not p.finished: col = (50, 150, 50)
        pygame.draw.rect(screen, col, bs_rect, border_radius=8)
        screen.blit(font.render("NASTĘPNA PORA", True, WHITE), (bs_rect.x + 30, bs_rect.y + 10))