# engine/game_manager.py
import pygame
import random
import os
from settings import *
from engine.card import Card, CARD_DB, CardType, CardTag
from engine.player import Player
from engine.board import Location
from typing import Dict, List, Optional, Tuple, Any


class GameManager:
    def __init__(self, app):
        self.app = app

        self.btn_menu: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.bg_original: Optional[pygame.Surface] = None
        self.bg_image: Optional[pygame.Surface] = None

        self.images_db: Dict[str, Optional[pygame.Surface]] = {}
        self.res_icons: Dict[str, Optional[pygame.Surface]] = {}
        self.images_res: Dict[str, Optional[pygame.Surface]] = {}
        self.card_images: Dict[str, Optional[pygame.Surface]] = {}

        self.locations: List[Location] = []

        self.LOC_W: int = 110
        self.LOC_H: int = 160
        self.LOC_GAP: int = 20

        try:
            self.bg_original = pygame.image.load("assets/bg.PNG")
        except FileNotFoundError:
            pass

        files_map = {
            "brzeg": "brzeg.png", "las": "las.png", "zywica": "zywica.png",
            "kamyki": "kamyki.png", "krzaki": "krzaki.png", "polana": "polana.png"
        }
        for key, filename in files_map.items():
            path = os.path.join("assets", filename)
            if os.path.exists(path):
                raw_img = pygame.image.load(path)
                self.images_db[key] = pygame.transform.smoothscale(raw_img, (self.LOC_W, self.LOC_H))
            else:
                self.images_db[key] = None

        files_res = {
            "twig": "twigs.png", "resin": "resin.png",
            "pebble": "stones.png", "berry": "berries.png"
        }
        for key, filename in files_res.items():
            path = os.path.join("assets", filename)
            if os.path.exists(path):
                raw_img = pygame.image.load(path)
                self.images_res[key] = pygame.transform.smoothscale(raw_img, (30, 30))
            else:
                self.images_res[key] = None

        cards_files = {
            "Farma": "farm.png", "Sklep": "shop.png", "Zamek": "castle.png",
            "Król": "king.png", "Mąż": "mar.png", "Żona": "mar.png",
            "Sędzia": "judge.png", "Historyk": "history.png",
            "Karczmarz": "innkeeper.png", "Kupiec": "shopkeeper.png",
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

        source = CARD_DB * 4
        random.shuffle(source)
        self.deck = [Card(d) for d in source]

        self.players = [Player("Gracz 1", P1_COLOR), Player("Gracz 2", P2_COLOR)]
        self.turn_idx: int = 0

        # [ZMIANA] Rozdajemy tylko 3 karty na start
        for p in self.players:
            for _ in range(3):
                if self.deck: p.hand.append(self.deck.pop())

        self.meadow: List[Card] = []
        self.refill_meadow()

        self.info_msg: str = "Zaczyna Gracz 1 (ZIMA)."

        self.update_layout()

    def update_layout(self) -> None:
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
    def current_player(self) -> Player:
        return self.players[self.turn_idx]

    def refill_meadow(self) -> None:
        while len(self.meadow) < 8 and self.deck:
            self.meadow.append(self.deck.pop())

    def next_turn(self) -> None:
        # Sprawdzamy, czy gra się skończyła (obaj gracze Finished)
        if self.players[0].finished and self.players[1].finished:
            self.calc_winner()
            return

        # Przełącz gracza
        self.turn_idx = (self.turn_idx + 1) % 2

        # Jeśli następny gracz już skończył grę, wróć do poprzedniego
        if self.current_player.finished:
            self.turn_idx = (self.turn_idx + 1) % 2
            # Jeśli i on skończył, to znaczy że obaj skończyli
            if self.current_player.finished:
                self.calc_winner()
                return

        p = self.current_player
        self.info_msg = f"Tura: {p.name} ({p.season})"

    def calc_winner(self) -> None:
        p1 = self.players[0]
        p2 = self.players[1]

        msg = f"KONIEC! {p1.name}: {p1.score} VP vs {p2.name}: {p2.score} VP. "
        if p1.score > p2.score:
            msg += f"Wygrywa {p1.name}!"
        elif p2.score > p1.score:
            msg += f"Wygrywa {p2.name}!"
        else:
            msg += "REMIS!"

        self.info_msg = msg

    def prepare_season(self) -> None:
        p = self.current_player

        # Ściągamy robotników z planszy
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
            # Lato: dobierz 2 karty
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
            self.info_msg = f"{p.name} zakończył grę."
            self.next_turn()
            return

        p.workers_available = p.workers_total
        self.info_msg = f"{p.name}: Sezon {p.season} rozpoczęty!"
        # Uwaga: Nie wywołujemy next_turn(), bo przygotowanie sezonu to akcja gracza,
        # po której (zazwyczaj) ma on jeszcze ruch lub kończy turę, ale tutaj
        # przyjęliśmy, że zmiana pory roku zużywa turę.
        self.next_turn()

    def handle_click(self, pos: Tuple[int, int]) -> None:
        if self.btn_menu.collidepoint(pos):
            self.app.change_state("MENU")
            return

        if "KONIEC" in self.info_msg: return
        p = self.current_player
        w, h = self.app.width, self.app.height

        # Przycisk zmiany sezonu
        btn_season = pygame.Rect(w - 220, h - 60, 200, 40)
        if btn_season.collidepoint(pos):
            if p.workers_available == 0:
                self.prepare_season()
            else:
                self.info_msg = "Masz jeszcze robotników!"
            return

        # 1. Obsługa LOKACJI (Robotnicy)
        if p.workers_available > 0:
            for loc in self.locations:
                if loc.rect.collidepoint(pos):
                    if loc.exclusive and loc.occupant:
                        self.info_msg = "Zajęte!"
                        return
                    if "cards" in loc.gain:
                        for _ in range(loc.gain["cards"]):
                            if self.deck and len(p.hand) < 8:  # Limit ręki przy dobieraniu
                                p.hand.append(self.deck.pop())
                    else:
                        for r, a in loc.gain.items(): p.resources[r] += a

                    if loc.exclusive: loc.occupant = p
                    p.workers_available -= 1
                    self.next_turn()
                    return

        # 2. Obsługa RYNKU (Kupowanie do Ręki)
        for i, card in enumerate(self.meadow):
            if card.rect and card.rect.collidepoint(pos):
                self.action_buy_from_market(p, card, i)
                return

        # 3. Obsługa RĘKI (Zagrywanie do Miasta)
        start_x = 20;
        hand_y = h - 170
        for i, card in enumerate(p.hand):
            rect = pygame.Rect(start_x + (i * 110), hand_y, 100, 140)
            if rect.collidepoint(pos):
                self.action_play_from_hand(p, card, i)
                return

    # [NOWA LOGIKA] Kupno z Rynku -> Ręka
    def action_buy_from_market(self, p: Player, card: Card, index: int) -> None:
        # Sprawdź limit ręki (np. 6 kart)
        if len(p.hand) >= 6:
            self.info_msg = "Masz pełną rękę (max 6)!"
            return

        # Sprawdź czy stać (surowce LUB combo)
        if p.can_afford(card):
            is_free = p.pay(card)  # Pobiera surowce

            # Przenieś z Łąki do Ręki
            p.hand.append(card)
            self.meadow.pop(index)
            self.refill_meadow()

            txt = " (DARMOWE KUPNO)" if is_free else ""
            self.info_msg = f"Kupiono {card.name} do ręki{txt}."
            self.next_turn()
        else:
            self.info_msg = "Nie stać Cię na kupno tej karty!"

    # [NOWA LOGIKA] Zagranie z Ręki -> Miasto
    def action_play_from_hand(self, p: Player, card: Card, index: int) -> None:
        # Sprawdź limit miasta
        if len(p.city) >= 15:
            self.info_msg = "Miasto pełne (max 15)!"
            return

        # Zgodnie z życzeniem: zagranie z ręki jest DARMOWE (koszt 0)
        # Ale zużywa turę.

        # Sprawdzamy triggery (bonusy z niebieskich kart w mieście)
        trigger_msgs = []
        if hasattr(p, 'check_triggers'):
            trigger_msgs = p.check_triggers(card)

        # Obsługa bonusów (dobieranie kart)
        for msg in trigger_msgs:
            if "DRAW_CARD" in msg:
                try:
                    count = int(msg.split(":")[1])
                    for _ in range(count):
                        if self.deck and len(p.hand) < 6:
                            p.hand.append(self.deck.pop())
                except:
                    pass

        # Przenieś z Ręki do Miasta
        p.city.append(card)
        p.hand.pop(index)

        # Efekt natychmiastowy (zielone karty)
        if card.type == CardType.PROD:
            for r, a in card.benefit.items(): p.resources[r] += a

        bonus_txt = " +Bonus!" if trigger_msgs else ""
        self.info_msg = f"Zagrałeś {card.name} do miasta{bonus_txt}."

        self.next_turn()

    def get_cards_by_link_id(self, link_id: str, search_mode: str) -> List[str]:
        names = set()
        for data in CARD_DB:
            if search_mode == 'PROVIDER':
                if data.get("link") == link_id:
                    names.add(data["name"])
            elif search_mode == 'RECEIVER':
                if data.get("link_req") == link_id:
                    names.add(data["name"])
        return list(names)

    def draw_hover_tooltip(self, screen: pygame.Surface, card: Card, mouse_pos: Tuple[int, int]) -> None:
        font_bold = pygame.font.SysFont("Arial", 14, bold=True)
        font_reg = pygame.font.SysFont("Arial", 14)

        res_trans = {"twig": "Drewno", "resin": "Żywica", "pebble": "Kamyk", "berry": "Jagoda"}

        lines = []
        lines.append((card.name, (255, 215, 0)))
        lines.append((f"Typ: {card.tag} / {card.type}", (200, 200, 200)))

        # Wyświetlamy koszt (dotyczy kupna z Rynku)
        cost_str = []
        for r, a in card.cost.items():
            name_pl = res_trans.get(r, r)
            cost_str.append(f"{a} {name_pl}")
        lines.append((f"Cena (Rynek): {', '.join(cost_str)}", (255, 150, 150)))

        lines.append(("Efekt:", (150, 255, 150)))
        lines.append((card.desc, (255, 255, 255)))

        if card.link:
            receivers = self.get_cards_by_link_id(card.link, 'RECEIVER')
            if receivers:
                names_str = ", ".join(receivers)
                lines.append((f"Umożliwia darmowe kupno: {names_str}", (100, 200, 255)))

        if card.link_req:
            providers = self.get_cards_by_link_id(card.link_req, 'PROVIDER')
            if providers:
                req_name = providers[0]
                is_free = self.current_player.check_free_build(card)
                if is_free:
                    lines.append((f"KUP ZA DARMO! (Masz {req_name})", (0, 255, 0)))
                else:
                    lines.append((f"Darmowe kupno jeśli masz: {req_name}", (255, 200, 100)))

        box_w = 300
        box_h = 20 + (len(lines) * 20)

        x, y = mouse_pos
        x += 15
        y += 15

        if x + box_w > self.app.width: x -= box_w + 30
        if y + box_h > self.app.height: y -= box_h + 30

        s = pygame.Surface((box_w, box_h))
        s.set_alpha(230)
        s.fill((20, 20, 30))
        screen.blit(s, (x, y))

        pygame.draw.rect(screen, (100, 100, 100), (x, y, box_w, box_h), 2)

        curr_y = y + 10
        for text, color in lines:
            surf = font_bold.render(text, True, color) if text == card.name else font_reg.render(text, True, color)
            screen.blit(surf, (x + 10, curr_y))
            curr_y += 20

    def draw(self) -> None:
        screen = self.app.screen
        w, h = self.app.width, self.app.height
        mouse_pos = pygame.mouse.get_pos()

        if self.bg_image:
            screen.blit(self.bg_image, (0, 0))
        else:
            screen.fill(BG_COLOR)
        font = self.app.font

        pygame.draw.rect(screen, (150, 50, 50), self.btn_menu, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.btn_menu, 2, border_radius=5)
        txt = font.render("MENU", True, WHITE)
        screen.blit(txt, txt.get_rect(center=self.btn_menu.center))

        for loc in self.locations: loc.draw(screen, font)

        p = self.current_player

        hovered_card: Optional[Card] = None

        meadow_y = 240
        start_mx = (w - (8 * 110)) // 2

        # Rysowanie Rynku (Łąki)
        for i, card in enumerate(self.meadow):
            # Sprawdzamy combo TYLKO dla rynku (bo tylko tu płacimy)
            bonus_name = None
            if hasattr(p, 'check_bonus_potential'):
                bonus_name = p.check_bonus_potential(card.tag)

            img = self.card_images.get(card.name)
            card.draw_visual(screen, start_mx + (i * 110), meadow_y + 10, font, bonus_source=bonus_name, image=img)

            if card.rect and card.rect.collidepoint(mouse_pos):
                hovered_card = card

        py = h - 200
        pygame.draw.rect(screen, UI_PANEL_COLOR, (0, py, w, 200))
        pygame.draw.line(screen, p.color, (0, py), (w, py), 5)
        screen.blit(self.app.title_font.render(self.info_msg, True, WHITE), (20, py + 10))

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

        city_start_y = 150
        city_x = 20
        title_city = font.render(f"TWOJE MIASTO ({len(p.city)}/15):", True, (255, 255, 200))
        screen.blit(title_city, (city_x, city_start_y - 25))

        for i, built_card in enumerate(p.city):
            c_col = (200, 200, 200)
            if built_card.type == CardType.PROD:
                c_col = (150, 255, 150)
            elif built_card.type == CardType.PASSIVE:
                c_col = (150, 150, 255)
            card_name = font.render(f"- {built_card.name}", True, c_col)
            screen.blit(card_name, (city_x, city_start_y + (i * 20)))

        # Rysowanie Ręki
        hx = 20;
        hy = py + 80
        # Nagłówek dla Ręki
        hand_title = font.render(f"RĘKA (Ekwipunek) {len(p.hand)}/6", True, (200, 200, 200))
        screen.blit(hand_title, (hx, hy - 25))

        for i, card in enumerate(p.hand):
            # Na ręce NIE pokazujemy combo, bo zagranie i tak jest darmowe
            img = self.card_images.get(card.name)
            card.draw_visual(screen, hx + (i * 110), hy, font, bonus_source=None, image=img)

            if card.rect and card.rect.collidepoint(mouse_pos):
                hovered_card = card

        if hovered_card:
            self.draw_hover_tooltip(screen, hovered_card, mouse_pos)

        bs_rect = pygame.Rect(w - 220, h - 60, 200, 40)
        col = (100, 100, 100)
        if p.workers_available == 0 and not p.finished: col = (50, 150, 50)
        pygame.draw.rect(screen, col, bs_rect, border_radius=8)
        screen.blit(font.render("NASTĘPNA PORA", True, WHITE), (bs_rect.x + 30, bs_rect.y + 10))