# engine/app.py
import pygame
from settings import *
from engine.menu import Menu
from engine.game_manager import GameManager
from engine.game_over import GameOverScene
from engine.sound import SoundManager


class App:
    def __init__(self):
        pygame.init()
        self.width, self.height = SCREEN_WIDTH, SCREEN_HEIGHT
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
        self.game_over_scene = GameOverScene(self)
        self.state = "MENU"

    def reset_game_manager(self):
        return GameManager(self)

    def change_state(self, new_state):
        self.sound.play_click()
        self.state = new_state
        #Pattern Matching - match/case (sterowanie stanem)]
        match new_state:
            case "GAME":
                self.game.update_layout()
            case "GAME_OVER":
                self.game_over_scene.update_layout()
            case "MENU":
                self.menu.update_layout()

    def set_resolution(self, w, h):
        self.width, self.height = w, h
        self.screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN if self.fullscreen else 0)
        self.menu.update_layout();
        self.game.update_layout();
        self.game_over_scene.update_layout()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.set_resolution(self.width, self.height)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.state == "GAME": self.change_state("MENU")

                # [Wykład: Pattern Matching w obsłudze zdarzeń]
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    match self.state:
                        case "MENU":
                            self.menu.handle_click(event.pos)
                        case "GAME":
                            self.game.handle_click(event.pos)
                        case "GAME_OVER":
                            self.game_over_scene.handle_click(event.pos)

                elif event.type == pygame.MOUSEMOTION and self.state == "MENU":
                    self.menu.handle_drag(event.pos, event.buttons)

            match self.state:
                case "MENU":
                    self.menu.draw()
                case "GAME":
                    self.game.draw()
                case "GAME_OVER":
                    self.game_over_scene.draw()

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()