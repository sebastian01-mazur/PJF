# engine/game_over.py
import pygame
from settings import *
from typing import Tuple  #Typehinting]


class GameOverScene:
    def __init__(self, app):
        self.app = app
        self.winner_text: str = ""
        self.game_duration: str = "00:00"
        self.btn_back = pygame.Rect(0, 0, 200, 50)
        self.update_layout()

    def update_layout(self) -> None:
        self.btn_back.center = (self.app.width // 2, self.app.height - 80)

    def set_results(self, winner_txt: str, duration_sec: float) -> None:
        self.winner_text = winner_txt
        # [Wykład: Formatowanie napisów f-string]
        self.game_duration = f"{int(duration_sec // 60)} min {int(duration_sec % 60)} s"

    def handle_click(self, pos: Tuple[int, int]) -> None:
        if self.btn_back.collidepoint(pos):
            self.app.sound.play_click()
            self.app.game = self.app.reset_game_manager()
            self.app.change_state("MENU")

    def draw(self) -> None:
        screen = self.app.screen
        w, h = self.app.width, self.app.height
        screen.fill((30, 35, 40))

        font_big = pygame.font.SysFont("Arial", 60, bold=True)
        t = font_big.render("GAME OVER", True, (255, 100, 100))
        screen.blit(t, t.get_rect(center=(w // 2, 80)))

        font_mid = pygame.font.SysFont("Arial", 30, bold=True)
        w_surf = font_mid.render(self.winner_text, True, (255, 215, 0))
        screen.blit(w_surf, w_surf.get_rect(center=(w // 2, 150)))

        self.draw_table(screen, w // 2, 220)

        pygame.draw.rect(screen, (100, 100, 100), self.btn_back, border_radius=5)
        txt = self.app.font.render("WRÓĆ DO MENU", True, WHITE)
        screen.blit(txt, txt.get_rect(center=self.btn_back.center))

    def draw_table(self, screen, cx, start_y):
        font = pygame.font.SysFont("Arial", 18)
        p1, p2 = self.app.game.players

        #Krotki i listy]
        rows = [
            ("Punkty Zwycięstwa", str(p1.score), str(p2.score)),
            ("Zagrane Karty", str(p1.stats["cards_played"]), str(p2.stats["cards_played"])),
            ("Drewno (Suma)", str(p1.stats["total_res"]["twig"]), str(p2.stats["total_res"]["twig"])),
            ("Jagody (Suma)", str(p1.stats["total_res"]["berry"]), str(p2.stats["total_res"]["berry"])),
        ]

        screen.blit(font.render(f"Czas gry: {self.game_duration}", True, (200, 200, 200)), (cx - 300, start_y - 40))

        col_w, x = 200, cx - 300
        for i, h in enumerate(["STATYSTYKA", "GRACZ 1", "GRACZ 2"]):
            screen.blit(pygame.font.SysFont("Arial", 18, bold=True).render(h, True, (255, 200, 100)),
                        (x + (i * col_w), start_y))

        y = start_y + 40
        pygame.draw.line(screen, (100, 100, 100), (x, y - 10), (x + 600, y - 10), 2)

        for row in rows:
            for i, val in enumerate(row):
                screen.blit(font.render(val, True, (200, 200, 200) if i == 0 else WHITE), (x + (i * col_w), y))
            y += 30