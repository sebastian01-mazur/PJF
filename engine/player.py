# engine/player.py
from settings import *


class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.resources = {"twig": 0, "resin": 0, "pebble": 0, "berry": 0}
        self.hand = []  # Karty na ręce
        self.city = []  # Zbudowane karty

        # Pory roku
        self.season = "ZIMA"
        self.workers_total = 2
        self.workers_available = 2
        self.finished = False  # Czy zakończył grę

    def can_afford(self, card):
        for res, amt in card.cost.items():
            if self.resources[res] < amt:
                return False
        return True

    def pay(self, card):
        for res, amt in card.cost.items():
            self.resources[res] -= amt

    def activate_production(self):
        """Zbiera surowce z zielonych kart w mieście"""
        produced = False
        for card in self.city:
            if card.type == "PROD":
                for res, amt in card.benefit.items():
                    self.resources[res] += amt
                produced = True
        return produced