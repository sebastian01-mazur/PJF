# engine/game_manager.py
import pygame
import random
import os
import time
from settings import *
from engine.card import Card, CARD_DB, CardType, CardTag
from engine.player import Player
from engine.board import Location
from typing import Dict, List, Optional, Tuple


class GameManager:
    def __init__(self, app):
        self.app = app
        self.start_time = time.time()

        self.btn_menu: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.bg_original: Optional[pygame.Surface] = None
        self.bg_image: Optional[pygame.Surface] = None

        self.images_db: Dict[str, Optional[pygame.Surface]] = {}
        self.res_icons: Dict[str, Optional[pygame.Surface]] = {}
        self.images_res: Dict[str, Optional[pygame.Surface]] = {}
        self.card_images: Dict[str, Optional[pygame.Surface]] = {}

        self.locations: List[Location] = []
        self.LOC_W, self.LOC_H, self.LOC_GAP = 110, 160, 20

        try:
            self.bg_original = pygame.image.load("assets/bg.PNG")
        except FileNotFoundError:
            pass

        # Ładowanie grafik
        for k, f in {"brzeg": "brzeg.png", "las": "las.png", "zywica": "zywica.png", "kamyki": "kamyki.png",
                     "krzaki": "krzaki.png", "polana": "polana.png"}.items():
            path = os.path.join("assets", f)
            self.images_db[k] = pygame.transform.smoothscale(pygame.image.load(path),
                                                             (self.LOC_W, self.LOC_H)) if os.path.exists(path) else None

        for k, f in {"twig": "twigs.png", "resin": "resin.png", "pebble": "stones.png", "berry": "berries.png"}.items():
            path = os.path.join("assets", f)
            self.images_res[k] = pygame.transform.smoothscale(pygame.image.load(path), (30, 30)) if os.path.exists(
                path) else None

        cards_files = {"Farma": "farm.png", "Sklep": "shop.png", "Zamek": "castle.png", "Król": "king.png",
                       "Mąż": "mar.png", "Żona": "mar.png", "Sędzia": "judge.png", "Historyk": "history.png",
                       "Karczmarz": "innkeeper.png", "Kupiec": "shopkeeper.png", "Rezydencja": "res.png"}
        for name, f in cards_files.items():
            path = os.path.join("assets", f)
            self.card_images[name] = pygame.transform.smoothscale(pygame.image.load(path),
                                                                  (100, 140)) if os.path.exists(path) else None

        #List Comprehension]
        source = CARD_DB * 4
        random.shuffle(source)
        self.deck = [Card(d) for d in source]

        self.players = [Player("Gracz 1", P1_COLOR), Player("Gracz 2", P2_COLOR)]
        self.turn_idx: int = 0

        # Start z 3 kartami
        for p in self.players:
            for _ in range(3):
                if self.deck: p.hand.append(self.deck.pop())

        self.meadow: List[Card] = []
        self.refill_meadow()
        self.info_msg: str = "Zaczyna Gracz 1 (ZIMA)."
        self.update_layout()

    def update_layout(self) -> None:
        w, h = self.app.width, self.app.height
        if self.bg_original:
            self.bg_image = pygame.transform.scale(self.bg_original, (w, h))
        self.btn_menu = pygame.Rect(w - 120, 10, 110, 40)

        loc_defs = [
            ("Brzeg (2 Gałązki)", {"twig": 2}, True, "brzeg"),
            ("Las (3 Gałązki)", {"twig": 3}, True, "las"),
            ("Żywica (2 Żywice)", {"resin": 2}, True, "zywica"),
            ("Kamyki (1 Kamyk)", {"pebble": 1}, True, "kamyki"),
            ("Krzaki (1 Jagoda)", {"berry": 1}, True, "krzaki"),
            ("Polana (2 Karty)", {"cards": 2}, False, "polana")
        ]

        if not self.locations:
            #Funkcja enumerate]
            start_x, y = (w - ((6 * 110) + (5 * 20))) // 2, 60
            for i, (name, gain, excl, img_key) in enumerate(loc_defs):
                rect = pygame.Rect(start_x + (i * 130), y, 110, 160)
                self.locations.append(Location(name, rect.x, rect.y, gain, excl, image=self.images_db.get(img_key)))
        else:
            start_x = (w - ((6 * 110) + (5 * 20))) // 2
            for i, loc in enumerate(self.locations):
                loc.rect.x = start_x + (i * 130)

    @property
    def current_player(self) -> Player:
        return self.players[self.turn_idx]

    def refill_meadow(self) -> None:
        while len(self.meadow) < 8 and self.deck:
            self.meadow.append(self.deck.pop())

    def next_turn(self) -> None:
        if all(p.finished for p in self.players):  # [Wykład: Funkcja all]
            self.calc_winner()
            return

        self.turn_idx = (self.turn_idx + 1) % 2
        if self.current_player.finished:
            self.turn_idx = (self.turn_idx + 1) % 2
            if self.current_player.finished:
                self.calc_winner()
                return

        p = self.current_player
        self.info_msg = f"Tura: {p.name} ({p.season})"

    def calc_winner(self) -> None:
        p1, p2 = self.players
        duration = time.time() - self.start_time

        #Wyrażenie warunkowe]
        winner = f"WYGRAŁ: {p1.name}!" if p1.score > p2.score else (
            f"WYGRAŁ: {p2.name}!" if p2.score > p1.score else "REMIS!")
        self.app.game_over_scene.set_results(winner, duration)
        self.app.change_state("GAME_OVER")

    def prepare_season(self) -> None:
        p = self.current_player
        for loc in self.locations:
            if loc.occupant == p: loc.occupant = None

        #Pattern Matching - match/case]
        match p.season:
            case "ZIMA":
                p.season = "WIOSNA";
                p.workers_total += 1
                if p.activate_production(): self.info_msg = "Wiosna: Produkcja aktywna!"
            case "WIOSNA":
                p.season = "LATO";
                p.workers_total += 1
                for _ in range(2):
                    if self.deck: p.hand.append(self.deck.pop())
            case "LATO":
                p.season = "JESIEŃ";
                p.workers_total += 2
                if p.activate_production(): self.info_msg = "Jesień: Produkcja aktywna!"
            case "JESIEŃ":
                p.finished = True;
                p.workers_total = 0;
                self.info_msg = f"{p.name} zakończył grę."
                self.next_turn();
                return

        p.workers_available = p.workers_total
        self.next_turn()

    def handle_click(self, pos: Tuple[int, int]) -> None:
        if self.btn_menu.collidepoint(pos):
            self.app.change_state("MENU");
            return
        if "KONIEC" in self.info_msg: return

        p = self.current_player

        # Zmiana sezonu
        if pygame.Rect(self.app.width - 220, self.app.height - 60, 200, 40).collidepoint(pos):
            if p.workers_available == 0:
                self.prepare_season()
            else:
                self.info_msg = "Masz jeszcze robotników!"
            return

        # Lokacje
        if p.workers_available > 0:
            for loc in self.locations:
                if loc.rect.collidepoint(pos):
                    if loc.exclusive and loc.occupant: self.info_msg = "Zajęte!"; return

                    if "cards" in loc.gain:
                        for _ in range(loc.gain["cards"]):
                            if self.deck and len(p.hand) < 8: p.hand.append(self.deck.pop())
                    else:
                        p.gain_resources(loc.gain)

                    if loc.exclusive: loc.occupant = p
                    p.workers_available -= 1;
                    self.next_turn();
                    return

        # Rynek (Kupno do ręki)
        for i, card in enumerate(self.meadow):
            if card.rect and card.rect.collidepoint(pos):
                self.action_buy_from_market(p, card, i);
                return

        # Ręka (Zagranie do miasta)
        start_x, hand_y = 20, self.app.height - 170
        for i, card in enumerate(p.hand):
            if pygame.Rect(start_x + (i * 110), hand_y, 100, 140).collidepoint(pos):
                self.action_play_from_hand(p, card, i);
                return

    def action_buy_from_market(self, p: Player, card: Card, index: int) -> None:
        if len(p.hand) >= 6: self.info_msg = "Pełna ręka!"; return
        if p.can_afford(card):
            is_free = p.pay(card)
            p.hand.append(card)
            self.meadow.pop(index);
            self.refill_meadow()
            self.info_msg = f"Kupiono {card.name}." + (" (FREE)" if is_free else "")
            self.next_turn()
        else:
            self.info_msg = "Nie stać Cię!"

    def action_play_from_hand(self, p: Player, card: Card, index: int) -> None:
        if len(p.city) >= 15: self.info_msg = "Miasto pełne!"; return

        trigger_msgs = p.check_triggers(card) if hasattr(p, 'check_triggers') else []
        for msg in trigger_msgs:
            if "DRAW_CARD" in msg:
                try:
                    for _ in range(int(msg.split(":")[1])):
                        if self.deck and len(p.hand) < 6: p.hand.append(self.deck.pop())
                except:
                    pass

        p.city.append(card);
        p.hand.pop(index)
        p.stats["cards_played"] += 1
        if card.type == CardType.PROD: p.gain_resources(card.benefit)

        self.info_msg = f"Zagrałeś {card.name}."
        self.next_turn()

    def get_cards_by_link_id(self, link_id: str, mode: str) -> List[str]:
        # [Wykład: Funkcja filter + map (zbiór nazw)]
        if mode == 'PROVIDER':
            return [d["name"] for d in CARD_DB if d.get("link") == link_id]
        elif mode == 'RECEIVER':
            return [d["name"] for d in CARD_DB if d.get("link_req") == link_id]
        return []

    def draw_hover_tooltip(self, screen: pygame.Surface, card: Card, mouse_pos: Tuple[int, int]) -> None:
        font_b, font_r = pygame.font.SysFont("Arial", 14, bold=True), pygame.font.SysFont("Arial", 14)
        res_map = {"twig": "Drewno", "resin": "Żywica", "pebble": "Kamyk", "berry": "Jagoda"}

        lines = [(card.name, (255, 215, 0)), (f"Typ: {card.tag} / {card.type}", (200, 200, 200))]
        cost_txt = ", ".join([f"{v} {res_map.get(k, k)}" for k, v in card.cost.items()])
        lines.append((f"Cena: {cost_txt}", (255, 150, 150)))
        lines.append(("Efekt:", (150, 255, 150)));
        lines.append((card.desc, (255, 255, 255)))

        if card.link:
            lines.append(
                (f"Umożliwia darmowe: {', '.join(self.get_cards_by_link_id(card.link, 'RECEIVER'))}", (100, 200, 255)))
        if card.link_req:
            prov = self.get_cards_by_link_id(card.link_req, 'PROVIDER')
            name = prov[0] if prov else "?"
            col = (0, 255, 0) if self.current_player.check_free_build(card) else (255, 200, 100)
            lines.append((f"DARMOWA jeśli masz: {name}", col))

        box_w, box_h = 300, 20 + (len(lines) * 20)
        x, y = mouse_pos[0] + 15, mouse_pos[1] + 15
        if x + box_w > self.app.width: x -= box_w + 30
        if y + box_h > self.app.height: y -= box_h + 30

        s = pygame.Surface((box_w, box_h));
        s.set_alpha(230);
        s.fill((20, 20, 30))
        screen.blit(s, (x, y));
        pygame.draw.rect(screen, (100, 100, 100), (x, y, box_w, box_h), 2)

        for i, (txt, col) in enumerate(lines):
            screen.blit(font_b.render(txt, True, col) if i == 0 else font_r.render(txt, True, col),
                        (x + 10, y + 10 + (i * 20)))

    def draw(self) -> None:
        screen = self.app.screen
        screen.blit(self.bg_image, (0, 0)) if self.bg_image else screen.fill(BG_COLOR)

        # UI Menu
        pygame.draw.rect(screen, (150, 50, 50), self.btn_menu, border_radius=5)
        screen.blit(self.app.font.render("MENU", True, WHITE), (self.btn_menu.x + 35, self.btn_menu.y + 10))

        for loc in self.locations: loc.draw(screen, self.app.font)

        p = self.current_player
        mx, my = pygame.mouse.get_pos()
        hovered = None

        # Łąka (Rynek)
        start_mx = (self.app.width - (8 * 110)) // 2
        for i, card in enumerate(self.meadow):
            bonus = p.check_bonus_potential(card.tag) if hasattr(p, 'check_bonus_potential') else None
            card.draw_visual(screen, start_mx + (i * 110), 250, self.app.font, bonus_source=bonus,
                             image=self.card_images.get(card.name))
            if card.rect.collidepoint((mx, my)): hovered = card

        # Panel UI
        py = self.app.height - 200
        pygame.draw.rect(screen, UI_PANEL_COLOR, (0, py, self.app.width, 200))
        screen.blit(self.app.title_font.render(self.info_msg, True, WHITE), (20, py + 10))

        # Surowce
        rx = 20
        for k in ["twig", "resin", "pebble", "berry"]:
            if self.images_res.get(k): screen.blit(self.images_res[k], (rx, py + 35))
            screen.blit(self.app.font.render(str(p.resources[k]), True, WHITE), (rx + 35, py + 40));
            rx += 80

        screen.blit(self.app.font.render(f"Robotnicy: {p.workers_available}/{p.workers_total}", True, WHITE),
                    (rx + 20, py + 40))
        screen.blit(self.app.font.render(f"PUNKTY: {p.score}", True, (255, 215, 0)), (rx + 150, py + 40))

        # Miasto
        screen.blit(self.app.font.render(f"MIASTO ({len(p.city)}/15):", True, (255, 255, 200)), (20, 125))
        for i, c in enumerate(p.city):
            col = (150, 255, 150) if c.type == CardType.PROD else (
                (150, 150, 255) if c.type == CardType.PASSIVE else (200, 200, 200))
            screen.blit(self.app.font.render(f"- {c.name}", True, col), (20, 150 + (i * 20)))

        # Ręka
        hx, hy = 20, py + 80
        screen.blit(self.app.font.render(f"RĘKA {len(p.hand)}/6", True, (200, 200, 200)), (hx, hy - 20))
        for i, card in enumerate(p.hand):
            card.draw_visual(screen, hx + (i * 110), hy, self.app.font, image=self.card_images.get(card.name))
            if card.rect.collidepoint((mx, my)): hovered = card

        if hovered: self.draw_hover_tooltip(screen, hovered, (mx, my))

        bs = pygame.Rect(self.app.width - 220, self.app.height - 60, 200, 40)
        pygame.draw.rect(screen, (50, 150, 50) if p.workers_available == 0 else (100, 100, 100), bs, border_radius=8)
        screen.blit(self.app.font.render("NASTĘPNA PORA", True, WHITE), (bs.x + 30, bs.y + 10))