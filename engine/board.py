# engine/board.py
import pygame


class Location:
    def __init__(self, name, x, y, gain, exclusive=True, image=None):
        self.name = name
        self.rect = pygame.Rect(x, y, 110, 160)  # Domyślne wymiary pionowe
        self.gain = gain
        self.exclusive = exclusive
        self.occupant = None
        self.image = image  # Przechowujemy grafikę tła dla lokacji

    def draw(self, surface, font):
        # 1. RYSOWANIE OBRAZKA (jeśli istnieje)
        if self.image:
            surface.blit(self.image, (self.rect.x, self.rect.y))

            # --- USUNIĘTO PRZYCIEMNIENIE ---
            # Poniższe linie tworzyły ciemny prostokąt na górze karty.
            # s = pygame.Surface((self.rect.width, self.rect.height))
            # s.set_alpha(50)
            # s.fill((0,0,0))
            # surface.blit(s, (self.rect.x, self.rect.y))
            # -------------------------------

        else:
            # Fallback (kolor), jeśli grafika się nie załaduje
            color = (80, 90, 80)
            if self.occupant: color = self.occupant.color
            pygame.draw.rect(surface, color, self.rect, border_radius=10)

        # 2. Ramka
        border_col = (200, 200, 200)
        if self.occupant:
            border_col = self.occupant.color  # Ramka w kolorze gracza
            pygame.draw.rect(surface, border_col, self.rect, 4, border_radius=10)
        else:
            pygame.draw.rect(surface, border_col, self.rect, 2, border_radius=10)

        # 3. Tekst (z cieniem dla czytelności na obrazku)
        # Rysujemy cień (czarny) lekko przesunięty
        shadow_surf = font.render(self.name, True, (0, 0, 0))
        surface.blit(shadow_surf, (self.rect.x + 7, self.rect.y + 7))

        # Rysujemy właściwy tekst (biały)
        text_surf = font.render(self.name, True, (255, 255, 255))
        surface.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))

        # 4. Pionek (jeśli zajęte)
        if self.occupant:
            # Rysujemy kółko na środku karty
            pygame.draw.circle(surface, (255, 255, 255), self.rect.center, 12)
            pygame.draw.circle(surface, self.occupant.color, self.rect.center, 10)