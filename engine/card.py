# engine/card.py
import pygame

CARD_DB = [
    # --- PRODUKCJA (ZIELONE) ---
    {"name": "Farma", "type": "PROD", "tag": "CONSTRUCT", "cost": {"twig": 2, "resin": 1}, "points": 1,
     "benefit": {"berry": 1}, "link": "FARMER", "desc": "Produkcja: 1 Jagoda."},
    {"name": "Sklep", "type": "PROD", "tag": "CONSTRUCT", "cost": {"resin": 2, "twig": 1}, "points": 2,
     "benefit": {"resin": 1}, "link": "SHOPKEEPER", "desc": "Produkcja: 1 Żywica."},

    # --- NIEBIESKIE (PASYWNE BONUSY) ---
    {"name": "Historyk", "type": "PASSIVE", "tag": "CRITTER", "cost": {"berry": 2}, "points": 1, "benefit": {},
     "trigger": {"on_play_tag": "CRITTER", "gain_card": 1},
     "desc": "Dobierz kartę, gdy zagrasz Stworzenie."},

    {"name": "Sędzia", "type": "PASSIVE", "tag": "CRITTER", "cost": {"berry": 3}, "points": 2, "benefit": {},
     "trigger": {"on_play_tag": "CONSTRUCT", "gain_res": {"berry": 1}},
     "desc": "Zyskaj 1 Jagodę, gdy zagrasz Budynek."},

    {"name": "Karczmarz", "type": "PASSIVE", "tag": "CRITTER", "cost": {"berry": 2}, "points": 1, "benefit": {},
     "trigger": {"on_play_tag": "CRITTER", "gain_res": {"berry": 1}},
     "desc": "Zyskaj 1 Jagodę za Stworzenia."},

    # --- PUNKTY (SZARE) ---
    {"name": "Zamek", "type": "VP", "tag": "CONSTRUCT", "cost": {"twig": 3, "pebble": 3}, "points": 5, "benefit": {},
     "link": "KING", "desc": "Siedziba Króla."},
    {"name": "Król", "type": "VP", "tag": "CRITTER", "cost": {"berry": 5}, "points": 6, "benefit": {},
     "link_req": "KING", "desc": "Władca."},

    # Mąż i Żona (korzystają z grafiki 'mar')
    {"name": "Mąż", "type": "VP", "tag": "CRITTER", "cost": {"berry": 3}, "points": 2, "benefit": {},
     "link_req": "FARMER", "desc": "Para farmerów."},
    {"name": "Żona", "type": "VP", "tag": "CRITTER", "cost": {"berry": 3}, "points": 2, "benefit": {},
     "link_req": "FARMER", "desc": "Para farmerów."},

    {"name": "Kupiec", "type": "VP", "tag": "CRITTER", "cost": {"berry": 2}, "points": 3, "benefit": {},
     "link_req": "SHOPKEEPER", "desc": "Kupiec."},

    # --- NOWOŚĆ: REZYDENCJA (korzysta z grafiki 'res') ---
    {"name": "Rezydencja", "type": "VP", "tag": "CONSTRUCT", "cost": {"twig": 2, "resin": 2, "pebble": 1}, "points": 3,
     "benefit": {}, "desc": "Luksusowy dom."}
]


class Card:
    def __init__(self, data):
        self.name = data['name']
        self.type = data['type']  # PROD / VP / PASSIVE
        self.tag = data.get('tag', 'OTHER')  # CONSTRUCT / CRITTER
        self.cost = data['cost']
        self.points = data['points']
        self.benefit = data['benefit']
        self.trigger = data.get('trigger', None)
        self.desc = data['desc']

        self.link = data.get('link', None)
        self.link_req = data.get('link_req', None)

        self.rect = None

    def draw_visual(self, surface, x, y, font, bonus_source=None, image=None):
        self.rect = pygame.Rect(x, y, 100, 140)

        # 1. TŁO / OBRAZEK
        if image:
            surface.blit(image, (x, y))
        else:
            # Fallback (gdyby brakowało pliku)
            if self.type == "PROD":
                bg_col = (60, 100, 60)
            elif self.type == "PASSIVE":
                bg_col = (60, 80, 140)
            else:
                bg_col = (100, 100, 110)
            pygame.draw.rect(surface, bg_col, self.rect, border_radius=8)

        # 2. RAMKA
        border_col = (200, 200, 200)
        if self.tag == "CONSTRUCT": border_col = (139, 69, 19)  # Brązowa
        if self.tag == "CRITTER": border_col = (220, 200, 160)  # Beżowa

        if bonus_source:
            border_col = (255, 215, 0)  # Złota dla Combo

        thickness = 4 if bonus_source else 2
        pygame.draw.rect(surface, border_col, self.rect, thickness, border_radius=8)

        # 3. PANELDONIY (Tło pod nazwę)
        header = pygame.Surface((100, 20))
        header.set_alpha(180)
        header.fill((0, 0, 0))
        surface.blit(header, (x, y))

        # Nazwa Karty
        name_surf = pygame.font.SysFont("Arial", 12, bold=True).render(self.name, True, (255, 255, 255))
        surface.blit(name_surf, (x + 5, y + 2))

        # 4. KOSZT (Lewy Dolny Róg)
        cost_y = y + 115
        # Tło pod koszt
        s_cost = pygame.Surface((40, 20))
        s_cost.set_alpha(180);
        s_cost.fill((0, 0, 0))
        surface.blit(s_cost, (x + 2, cost_y))

        cost_txt = ""
        for r, a in self.cost.items():
            short = r[0].upper()
            cost_txt += f"{a}{short} "
        c_surf = pygame.font.SysFont("Arial", 11, bold=True).render(cost_txt, True, (255, 200, 200))
        surface.blit(c_surf, (x + 4, cost_y + 2))

        # 5. PUNKTY I EFEKT (Prawy Górny/Środek)
        # VP w kółku w prawym górnym
        pygame.draw.circle(surface, (0, 0, 0), (x + 88, y + 12), 10)  # Tło
        pygame.draw.circle(surface, (255, 215, 0), (x + 88, y + 12), 9, width=1)  # Ramka
        vp_surf = pygame.font.SysFont("Arial", 12, bold=True).render(str(self.points), True, (255, 215, 0))
        surface.blit(vp_surf, (x + 88 - vp_surf.get_width() // 2, y + 5))

        # COMBO
        if bonus_source:
            combo_font = pygame.font.SysFont("Arial", 11, bold=True)
            txt = combo_font.render(f"COMBO!", True, (255, 255, 0))
            bg_rect = txt.get_rect(center=(x + 50, y + 35))
            pygame.draw.rect(surface, (0, 0, 0), bg_rect)
            surface.blit(txt, bg_rect)