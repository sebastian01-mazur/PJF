# engine/card.py
import pygame

# Baza danych kart (Tu dodajesz nowe!)
CARD_DB = [
    # --- PRODUKCJA (ZIELONE) ---
    {"name": "Farma", "type": "PROD", "cost": {"twig": 2, "resin": 1}, "points": 1, "benefit": {"berry": 1},
     "desc": "Produkuje 1 Jagodę"},
    {"name": "Tartak", "type": "PROD", "cost": {"twig": 1, "pebble": 1}, "points": 2, "benefit": {"twig": 1},
     "desc": "Produkuje 1 Gałązkę"},
    {"name": "Sklep", "type": "PROD", "cost": {"resin": 2}, "points": 1, "benefit": {"resin": 1},
     "desc": "Produkuje 1 Żywicę"},

    # --- PUNKTY (SZARE) ---
    {"name": "Zamek", "type": "VP", "cost": {"twig": 2, "resin": 3, "pebble": 3}, "points": 5, "benefit": {},
     "desc": "Epicka budowla"},
    {"name": "Szkoła", "type": "VP", "cost": {"twig": 2, "resin": 2}, "points": 3, "benefit": {},
     "desc": "Miejsce nauki"},
    {"name": "Pałac", "type": "VP", "cost": {"twig": 3, "resin": 3, "pebble": 3}, "points": 7, "benefit": {},
     "desc": "Siedziba Króla"},
]


class Card:
    def __init__(self, data):
        self.name = data['name']
        self.type = data['type']  #  "VP"
        self.cost = data['cost']  # np. {'twig': 2}
        self.points = data['points']
        self.benefit = data['benefit']  # Co daje przy produkcji
        self.desc = data['desc']
        self.rect = None  # Do klikania (ustawiane przy rysowaniu)

    def draw_visual(self, surface, x, y, font):
        # Rysowanie karty (Miniaturka)
        bg_col = (60, 100, 60) if self.type == "PROD" else (100, 100, 110)
        self.rect = pygame.Rect(x, y, 100, 140)

        pygame.draw.rect(surface, bg_col, self.rect, border_radius=8)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 1, border_radius=8)

        # Nazwa
        name_surf = font.render(self.name, True, (255, 255, 255))
        surface.blit(name_surf, (x + 5, y + 5))

        # Punkty
        pts_surf = font.render(f"{self.points} VP", True, (255, 215, 0))
        surface.blit(pts_surf, (x + 60, y + 5))

        # Koszt (Tekstowo na dole)
        cost_txt = ""
        for r, a in self.cost.items():
            cost_txt += f"{a}{r[0].upper()} "

        c_surf = pygame.font.SysFont("Arial", 12).render(cost_txt, True, (200, 200, 200))
        surface.blit(c_surf, (x + 5, y + 120))