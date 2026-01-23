# engine/player.py
from settings import *
from typing import List, Dict, Optional
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

        self.stats = {
            "cards_played": 0,
            "total_res": {"twig": 0, "resin": 0, "pebble": 0, "berry": 0}
        }

    @property  # [Wykład: Dekorator @property]
    def score(self) -> int:
        #Programowanie funkcyjne - Wyrażenie generatorowe]
        return sum(c.points for c in self.city)

    def gain_resources(self, res_dict: Dict[str, int]) -> None:
        for r, amount in res_dict.items():
            self.resources[r] += amount
            self.stats["total_res"][r] += amount

    def check_free_build(self, card: Card) -> bool:
        if card.link_req:
            #Funkcja any() z generatorem]
            return any(built_card.link == card.link_req for built_card in self.city)
        return False

    def can_afford(self, card: Card) -> bool:
        if self.check_free_build(card):
            return True
        #Iteracja po słowniku .items()]
        for res, amt in card.cost.items():
            if self.resources.get(res, 0) < amt:
                return False
        return True

    def pay(self, card: Card) -> bool:
        if self.check_free_build(card):
            return True
        for res, amt in card.cost.items():
            self.resources[res] -= amt
        return False

    def activate_production(self) -> bool:
        #List comprehension z filtrowaniem]
        prod_cards = [c for c in self.city if c.type == CardType.PROD]
        if not prod_cards:
            return False

        for card in prod_cards:
            self.gain_resources(card.benefit)
        return True

    def check_triggers(self, played_card: Card) -> List[str]:
        bonuses: List[str] = []
        # Filtrujemy tylko karty pasywne z triggerem (Styl funkcyjny)
        passive_cards = filter(lambda c: c.type == CardType.PASSIVE and c.trigger, self.city)

        for city_card in passive_cards:
            trig = city_card.trigger
            if trig.get("on_play_tag") == played_card.tag:
                if "gain_res" in trig:
                    self.gain_resources(trig["gain_res"])
                    for r, a in trig["gain_res"].items():
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