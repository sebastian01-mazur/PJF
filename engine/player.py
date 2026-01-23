# engine/player.py
from settings import *
from typing import List, Dict, Optional, Any
from engine.card import Card, CardType


class Player:
    def __init__(self, name: str, color: tuple[int, int, int]):
        self.name: str = name
        self.color: tuple[int, int, int] = color
        self.resources: Dict[str, int] = {"twig": 0, "resin": 0, "pebble": 0, "berry": 0}
        self.hand: List[Card] = []
        self.city: List[Card] = []

        self.season: str = "ZIMA"
        self.workers_total: int = 2
        self.workers_available: int = 2
        self.finished: bool = False

    @property
    def score(self) -> int:
        return sum(c.points for c in self.city)

    def check_free_build(self, card: Card) -> bool:
        if card.link_req:
            return any(built_card.link == card.link_req for built_card in self.city)
        return False

    def can_afford(self, card: Card) -> bool:
        # Sprawdzamy, czy karta jest darmowa dzięki Combo
        if self.check_free_build(card):
            return True

        # Jeśli nie, sprawdzamy surowce
        for res, amt in card.cost.items():
            if self.resources.get(res, 0) < amt:
                return False
        return True

    def pay(self, card: Card) -> bool:
        """Zwraca True jeśli zapłacono za darmo (Combo), False jeśli surowcami"""
        if self.check_free_build(card):
            return True

        for res, amt in card.cost.items():
            self.resources[res] -= amt
        return False

    def activate_production(self) -> bool:
        produced = False
        for card in self.city:
            if card.type == CardType.PROD:
                for res, amt in card.benefit.items():
                    self.resources[res] += amt
                produced = True
        return produced

    def check_triggers(self, played_card: Card) -> List[str]:
        bonuses: List[str] = []
        for city_card in self.city:
            if city_card.type == CardType.PASSIVE and city_card.trigger:
                trig = city_card.trigger
                if trig.get("on_play_tag") == played_card.tag:
                    if "gain_res" in trig:
                        for r, a in trig["gain_res"].items():
                            self.resources[r] += a
                            bonuses.append(f"+{a} {r} ({city_card.name})")
                    if "gain_card" in trig:
                        bonuses.append(f"DRAW_CARD:{trig['gain_card']}")
        return bonuses

    def check_bonus_potential(self, card_tag: str) -> Optional[str]:
        for city_card in self.city:
            if city_card.type == CardType.PASSIVE and city_card.trigger:
                if city_card.trigger.get("on_play_tag") == card_tag:
                    return city_card.name
        return None