# engine/card.py
import pygame
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import StrEnum


# [Wykład 3.4.4 - Typy wyliczeniowe]
class CardType(StrEnum):
    PROD = "PROD"
    VP = "VP"
    PASSIVE = "PASSIVE"


class CardTag(StrEnum):
    CONSTRUCT = "CONSTRUCT"
    CRITTER = "CRITTER"
    OTHER = "OTHER"


CARD_DB = [
    # --- PRODUKCJA (ZIELONE) ---
    # Tutaj opis mówi co produkujemy
    {
        "name": "Farma",
        "type": CardType.PROD,
        "tag": CardTag.CONSTRUCT,
        "cost": {"twig": 2, "resin": 1},
        "points": 1,
        "benefit": {"berry": 1},
        "link": "FARMER",
        "desc": "Produkcja: Otrzymujesz 1 Jagodę."
    },
    {
        "name": "Sklep",
        "type": CardType.PROD,
        "tag": CardTag.CONSTRUCT,
        "cost": {"resin": 2, "twig": 1},
        "points": 2,
        "benefit": {"resin": 1},
        "link": "SHOPKEEPER",
        "desc": "Produkcja: Otrzymujesz 1 Żywicę."
    },

    # --- NIEBIESKIE (PASYWNE BONUSY) ---
    # Tutaj opis mówi dokładnie jaki jest warunek (trigger)
    {
        "name": "Historyk",
        "type": CardType.PASSIVE,
        "tag": CardTag.CRITTER,
        "cost": {"berry": 2},
        "points": 1,
        "benefit": {},
        "trigger": {"on_play_tag": CardTag.CRITTER, "gain_card": 1},
        "desc": "Dobierz kartę za każdym razem, gdy zagrasz Stworzenie."
    },
    {
        "name": "Sędzia",
        "type": CardType.PASSIVE,
        "tag": CardTag.CRITTER,
        "cost": {"berry": 3},
        "points": 2,
        "benefit": {},
        "trigger": {"on_play_tag": CardTag.CONSTRUCT, "gain_res": {"berry": 1}},
        "desc": "Zyskaj 1 Jagodę za każdym razem, gdy zagrasz Budynek."
    },
    {
        "name": "Karczmarz",
        "type": CardType.PASSIVE,
        "tag": CardTag.CRITTER,
        "cost": {"berry": 2},
        "points": 1,
        "benefit": {},
        "trigger": {"on_play_tag": CardTag.CRITTER, "gain_res": {"berry": 1}},
        "desc": "Zyskaj 1 Jagodę, gdy zagrasz Stworzenie (zwrot kosztu)."
    },

    # --- PUNKTY (SZARE) ---
    # Tutaj opis musi "sprzedać" kartę jako źródło punktów
    {
        "name": "Zamek",
        "type": CardType.VP,
        "tag": CardTag.CONSTRUCT,
        "cost": {"twig": 3, "pebble": 3},
        "points": 5,
        "benefit": {},
        "link": "KING",
        "desc": "Potężna fortyfikacja warta aż 5 punktów zwycięstwa."
    },
    {
        "name": "Król",
        "type": CardType.VP,
        "tag": CardTag.CRITTER,
        "cost": {"berry": 5},
        "points": 6,
        "benefit": {},
        "link_req": "KING",
        "desc": "Najcenniejsza karta w grze. Zapewnia 6 punktów."
    },
    {
        "name": "Mąż",
        "type": CardType.VP,
        "tag": CardTag.CRITTER,
        "cost": {"berry": 3},
        "points": 2,
        "benefit": {},
        "link_req": "FARMER",
        "desc": "Podstawowa jednostka punktowa (2 VP). Tani z Farmą."
    },
    {
        "name": "Żona",
        "type": CardType.VP,
        "tag": CardTag.CRITTER,
        "cost": {"berry": 3},
        "points": 2,
        "benefit": {},
        "link_req": "FARMER",
        "desc": "Podstawowa jednostka punktowa (2 VP). Tania z Farmą."
    },
    {
        "name": "Kupiec",
        "type": CardType.VP,
        "tag": CardTag.CRITTER,
        "cost": {"berry": 2},
        "points": 3,
        "benefit": {},
        "link_req": "SHOPKEEPER",
        "desc": "Zyskujesz 3 punkty zwycięstwa dzięki handlowi."
    },
    {
        "name": "Rezydencja",
        "type": CardType.VP,
        "tag": CardTag.CONSTRUCT,
        "cost": {"twig": 2, "resin": 2, "pebble": 1},
        "points": 3,
        "benefit": {},
        "desc": "Prestiżowy budynek mieszkalny wart 3 punkty."
    }
]


# [Wykład 3.4.11 - @dataclass]
@dataclass
class Card:
    name: str
    type: str
    cost: Dict[str, int]
    points: int
    benefit: Dict[str, int]
    desc: str
    tag: str = CardTag.OTHER
    trigger: Optional[Dict[str, Any]] = None
    link: Optional[str] = None
    link_req: Optional[str] = None
    rect: Optional[pygame.Rect] = field(default=None, init=False)

    def __init__(self, data: Dict[str, Any]):
        self.name = data['name']
        self.type = data['type']
        self.tag = data.get('tag', CardTag.OTHER)
        self.cost = data['cost']
        self.points = data['points']
        self.benefit = data['benefit']
        self.trigger = data.get('trigger', None)
        self.desc = data['desc']
        self.link = data.get('link', None)
        self.link_req = data.get('link_req', None)
        self.rect = None

    def draw_visual(self, surface: pygame.Surface, x: int, y: int, font: pygame.font.Font,
                    bonus_source: Optional[str] = None, image: Optional[pygame.Surface] = None) -> None:
        self.rect = pygame.Rect(x, y, 100, 140)

        # 1. Rysowanie Obrazka
        if image:
            surface.blit(image, (x, y))
        else:
            if self.type == CardType.PROD:
                bg_col = (60, 100, 60)
            elif self.type == CardType.PASSIVE:
                bg_col = (60, 80, 140)
            else:
                bg_col = (100, 100, 110)
            pygame.draw.rect(surface, bg_col, self.rect, border_radius=8)

        # 2. Rysowanie Ramki
        if self.type == CardType.PROD:
            border_col = (50, 200, 50)  # Jasny Zielony
        elif self.type == CardType.PASSIVE:
            border_col = (50, 100, 255)  # Jasny Niebieski
        else:
            border_col = (180, 180, 180)  # Szary

        if bonus_source:
            border_col = (255, 215, 0)  # Złota dla Combo

        thickness = 4 if bonus_source else 3
        pygame.draw.rect(surface, border_col, self.rect, thickness, border_radius=8)

        # 3. Nazwa
        header = pygame.Surface((100, 20))
        header.set_alpha(180)
        header.fill((0, 0, 0))
        surface.blit(header, (x, y))

        name_surf = pygame.font.SysFont("Arial", 12, bold=True).render(self.name, True, (255, 255, 255))
        surface.blit(name_surf, (x + 5, y + 2))

        # 4. Punkty
        pygame.draw.circle(surface, (0, 0, 0), (x + 88, y + 12), 10)
        pygame.draw.circle(surface, (255, 215, 0), (x + 88, y + 12), 9, width=1)
        vp_surf = pygame.font.SysFont("Arial", 12, bold=True).render(str(self.points), True, (255, 215, 0))
        surface.blit(vp_surf, (x + 88 - vp_surf.get_width() // 2, y + 5))

        # 5. Znacznik Combo
        if bonus_source:
            combo_font = pygame.font.SysFont("Arial", 11, bold=True)
            txt = combo_font.render(f"COMBO!", True, (255, 255, 0))
            bg_rect = txt.get_rect(center=(x + 50, y + 125))
            pygame.draw.rect(surface, (0, 0, 0), bg_rect)
            surface.blit(txt, bg_rect)