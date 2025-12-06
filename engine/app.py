# engine/app.py
import pygame
from settings import *
from engine.menu import Menu
from engine.game_manager import GameManager
from engine.sound import SoundManager


class App:
    def __init__(self):
        pygame.init()

        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.fullscreen = False

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Forest Valley - Final Version")
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = pygame.font.SysFont("Arial", 16)
        self.title_font = pygame.font.SysFont("Arial", 30, bold=True)

        self.sound = SoundManager()
        self.sound.play_music()

        self.menu = Menu(self)
        self.game = GameManager(self)

        self.state = "MENU"

    def change_state(self, new_state):
        self.sound.play_click()
        self.state = new_state
        if new_state == "GAME":
            self.game.update_layout()

    def set_resolution(self, w, h):
        self.width = w
        self.height = h
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((w, h), flags)
        self.menu.update_layout()
        self.game.update_layout()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        self.menu.update_layout()
        self.game.update_layout()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # --- OBSŁUGA KLAWIATURY (ESC) ---
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "GAME":
                            self.change_state("MENU")
                        elif self.state == "MENU":
                            # Opcjonalnie: ESC w menu wyłącza grę
                            # self.running = False
                            pass

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "MENU":
                        self.menu.handle_click(event.pos)
                    elif self.state == "GAME":
                        self.game.handle_click(event.pos)

                elif event.type == pygame.MOUSEMOTION:
                    if self.state == "MENU":
                        self.menu.handle_drag(event.pos, event.buttons)

            if self.state == "MENU":
                self.menu.draw()
            elif self.state == "GAME":
                self.game.draw()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()