# engine/player.py
from settings import *


class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.resources = {"twig": 0, "resin": 0, "pebble": 0, "berry": 0}
        self.hand = []
        self.city = []

        self.season = "ZIMA"
        self.workers_total = 2
        self.workers_available = 2
        self.finished = False

    def check_free_build(self, card):
        """Sprawdza, czy gracz może zbudować tę kartę za darmo dzięki Synergii"""
        if card.link_req:  # Jeśli karta czegoś wymaga (np. Mąż wymaga Farmera)
            for built_card in self.city:
                # Sprawdzamy czy mamy budynek z odpowiednim symbolem
                if built_card.link == card.link_req:
                    return True
        return False

    def can_afford(self, card):
        # 1. Sprawdź czy jest darmowa (Synergia)
        if self.check_free_build(card):
            return True

        # 2. Jeśli nie darmowa, sprawdź surowce
        for res, amt in card.cost.items():
            if self.resources.get(res, 0) < amt:
                return False
        return True

    def pay(self, card):
        # 1. Jeśli darmowa, nie płać nic!
        if self.check_free_build(card):
            return True  # Zwracamy True, że zapłacono "za darmo"

        # 2. Płać surowcami
        for res, amt in card.cost.items():
            self.resources[res] -= amt
        return False  # Zwracamy False (nie było darmowe)

    def activate_production(self):
        produced = False
        for card in self.city:
            if card.type == "PROD":
                for res, amt in card.benefit.items():
                    self.resources[res] += amt
                produced = True
        return produced

    # --- NOWE METODY (BONUSY) ---

    def check_triggers(self, played_card):
        """Sprawdza karty w mieście i zwraca listę nagród po zagraniu nowej karty"""
        bonuses = []

        for city_card in self.city:
            # Szukamy kart PASYWNYCH (Niebieskich) z triggerami
            if city_card.type == "PASSIVE" and city_card.trigger:
                trig = city_card.trigger

                # Sprawdzamy warunek: Czy typ zagranej karty pasuje?
                # (np. Historyk czeka na CRITTER)
                if trig.get("on_play_tag") == played_card.tag:

                    # Bonus: Surowce
                    if "gain_res" in trig:
                        for r, a in trig["gain_res"].items():
                            self.resources[r] += a
                            bonuses.append(f"+{a} {r} ({city_card.name})")

                    # Bonus: Karty
                    if "gain_card" in trig:
                        # Zwracamy info, że trzeba dobrać (GameManager to obsłuży)
                        bonuses.append(f"DRAW_CARD:{trig['gain_card']}")

        return bonuses

    def check_bonus_potential(self, card_tag):
        """
        Sprawdza (na potrzeby UI), czy zagranie karty o danym tagu
        uruchomiłoby jakiś bonus w mieście.
        Zwraca nazwę karty dającej bonus lub None.
        """
        for city_card in self.city:
            if city_card.type == "PASSIVE" and city_card.trigger:
                if city_card.trigger.get("on_play_tag") == card_tag:
                    return city_card.name  # Np. zwróci "Historyk"
        return None