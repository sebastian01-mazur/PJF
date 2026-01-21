# engine/card.py
import pygame

CARD_DB = [
    # --- PRODUKCJA (ZIELONE) ---
    {"name": "Farma", "type": "PROD", "tag": "CONSTRUCT", "cost": {"twig": 2, "resin": 1}, "points": 1,
     "benefit": {"berry": 1}, "link": "FARMER", "desc": "Produkcja: 1 Jagoda."},
    {"name": "Sklep", "type": "PROD", "tag": "CONSTRUCT", "cost": {"resin": 2, "twig": 1}, "points": 2,
     "benefit": {"resin": 1}, "link": "SHOPKEEPER", "desc": "Produkcja: 1 Żywica."},

    # --- NIEBIESKIE (PASYWNE BONUSY) ---
    # Historyk: Kiedy zagrasz STWORZENIE -> Dobierz 1 kartę
    {"name": "Historyk", "type": "PASSIVE", "tag": "CRITTER", "cost": {"berry": 2}, "points": 1, "benefit": {},
     "trigger": {"on_play_tag": "CRITTER", "gain_card": 1},
     "desc": "Dobierz kartę, gdy zagrasz Stworzenie."},

    # Sędzia: Kiedy zagrasz BUDYNEK (CONSTRUCT) -> Zyskaj 1 Jagodę
    {"name": "Sędzia", "type": "PASSIVE", "tag": "CRITTER", "cost": {"berry": 3}, "points": 2, "benefit": {},
     "trigger": {"on_play_tag": "CONSTRUCT", "gain_res": {"berry": 1}},
     "desc": "Zyskaj 1 Jagodę, gdy zagrasz Budynek."},

    # Karczmarz: Kiedy zagrasz STWORZENIE -> Zyskaj 1 Jagodę
    {"name": "Karczmarz", "type": "PASSIVE", "tag": "CRITTER", "cost": {"berry": 2}, "points": 1, "benefit": {},
     "trigger": {"on_play_tag": "CRITTER", "gain_res": {"berry": 1}},
     "desc": "Zyskaj 1 Jagodę za Stworzenia."},

    # --- PUNKTY (SZARE) ---
    {"name": "Zamek", "type": "VP", "tag": "CONSTRUCT", "cost": {"twig": 3, "pebble": 3}, "points": 5, "benefit": {},
     "link": "KING", "desc": "Siedziba Króla."},
    {"name": "Król", "type": "VP", "tag": "CRITTER", "cost": {"berry": 5}, "points": 6, "benefit": {},
     "link_req": "KING", "desc": "Władca."},
    {"name": "Mąż", "type": "VP", "tag": "CRITTER", "cost": {"berry": 3}, "points": 2, "benefit": {},
     "link_req": "FARMER", "desc": "Mąż."},
    {"name": "Żona", "type": "VP", "tag": "CRITTER", "cost": {"berry": 3}, "points": 2, "benefit": {},
     "link_req": "FARMER", "desc": "Żona."},
    {"name": "Kupiec", "type": "VP", "tag": "CRITTER", "cost": {"berry": 2}, "points": 3, "benefit": {},
     "link_req": "SHOPKEEPER", "desc": "Kupiec."}
]


class Card:
    def __init__(self, data):
        self.name = data['name']
        self.type = data['type']  # PROD / VP / PASSIVE
        self.tag = data.get('tag', 'OTHER')  # CONSTRUCT / CRITTER
        self.cost = data['cost']
        self.points = data['points']
        self.benefit = data['benefit']
        self.trigger = data.get('trigger', None)  # Logika bonusu
        self.desc = data['desc']

        self.link = data.get('link', None)
        self.link_req = data.get('link_req', None)

        self.rect = None

    # TUTAJ JEST KLUCZOWA ZMIANA - dodano bonus_source=None
    def draw_visual(self, surface, x, y, font, bonus_source=None):
        # Kolory tła
        if self.type == "PROD":
            bg_col = (60, 100, 60)  # Zielony
        elif self.type == "PASSIVE":
            bg_col = (60, 80, 140)  # Niebieski
        else:
            bg_col = (100, 100, 110)  # Szary

        # Ramka
        border_col = (200, 200, 200)
        if self.tag == "CONSTRUCT": border_col = (139, 69, 19)
        if self.tag == "CRITTER": border_col = (200, 180, 150)

        # JEŚLI JEST BONUS (COMBO), ZMIENIAMY RAMKĘ NA ZŁOTĄ
        if bonus_source:
            border_col = (255, 215, 0)  # Złoty

        self.rect = pygame.Rect(x, y, 100, 140)
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=8)

        # Grubsza ramka przy bonusie
        thickness = 5 if bonus_source else 3
        pygame.draw.rect(surface, border_col, self.rect, thickness, border_radius=8)

        # Nazwa
        name_surf = font.render(self.name, True, (255, 255, 255))
        surface.blit(name_surf, (x + 5, y + 5))

        # Punkty
        pts_surf = font.render(f"{self.points} VP", True, (255, 215, 0))
        surface.blit(pts_surf, (x + 60, y + 5))

        # WYŚWIETLANIE NAZWY BONUSU (COMBO)
        if bonus_source:
            combo_font = pygame.font.SysFont("Arial", 11, bold=True)
            txt = combo_font.render(f"COMBO: {bonus_source}", True, (255, 255, 0))
            bg_rect = txt.get_rect(topleft=(x + 5, y + 25))
            pygame.draw.rect(surface, (0, 0, 0), bg_rect)
            surface.blit(txt, bg_rect)

        # Opis
        desc_words = self.desc.split()
        l1 = " ".join(desc_words[:3])
        l2 = " ".join(desc_words[3:])
        d1_surf = pygame.font.SysFont("Arial", 10).render(l1, True, (200, 200, 200))
        d2_surf = pygame.font.SysFont("Arial", 10).render(l2, True, (200, 200, 200))

        # Przesuwamy tekst nieco w dół, żeby zrobić miejsce na napis COMBO
        surface.blit(d1_surf, (x + 5, y + 45))
        surface.blit(d2_surf, (x + 5, y + 57))

        # Linki
        if self.link:
            link_txt = pygame.font.SysFont("Arial", 10).render(f"Link: {self.link}", True, (150, 255, 150))
            surface.blit(link_txt, (x + 5, y + 75))
        if self.link_req:
            req_txt = pygame.font.SysFont("Arial", 10).render(f"Wymaga: {self.link_req}", True, (255, 150, 150))
            surface.blit(req_txt, (x + 5, y + 75))

        # Koszt
        cost_txt = ""
        for r, a in self.cost.items():
            short = r[0].upper()
            cost_txt += f"{a}{short} "
        c_surf = pygame.font.SysFont("Arial", 12).render(cost_txt, True, (220, 220, 220))
        surface.blit(c_surf, (x + 5, y + 120))