# engine/menu.py
import pygame
from settings import *


class Menu:
    def __init__(self, app):
        self.app = app
        self.state = "MAIN"

        #TŁO MENU
        self.bg_original = None
        self.bg_image = None
        try:
            self.bg_original = pygame.image.load("assets/menu_bg.png")
        except FileNotFoundError:
            pass

        # --- GRAFIKI PRZYCISKÓW ---
        self.btn_images = {}

        # KONFIGURACJA WYMIARÓW
        self.BTN_W = 300
        self.BTN_H = 110
        self.GAP = 5

        files = {
            "play": "play.png",
            "setting": "setting.png",
            "quit": "quit.png"
        }

        for key, filename in files.items():
            try:
                img = pygame.image.load(f"assets/{filename}")
                self.btn_images[key] = pygame.transform.smoothscale(img, (self.BTN_W, self.BTN_H))
            except FileNotFoundError:
                print(f"Błąd: Nie znaleziono assets/{filename}")
                self.btn_images[key] = None

        # Wstępne definicje
        self.btn_start = pygame.Rect(0, 0, self.BTN_W, self.BTN_H)
        self.btn_settings = pygame.Rect(0, 0, self.BTN_W, self.BTN_H)
        self.btn_quit = pygame.Rect(0, 0, self.BTN_W, self.BTN_H)

        # USTAWIENIA (UI)
        self.slider_rect = pygame.Rect(0, 0, 200, 10)
        self.slider_knob = pygame.Rect(0, 0, 10, 20)

        # Szukamy aktualnego indeksu rozdzielczości
        self.res_idx = 0
        for i, res in enumerate(RESOLUTIONS):
            if res == (self.app.width, self.app.height):
                self.res_idx = i
                break

        self.btn_res = pygame.Rect(0, 0, 240, 50)
        self.btn_fullscreen = pygame.Rect(0, 0, 240, 50)
        self.btn_back = pygame.Rect(0, 0, 200, 50)

        self.update_layout()

    def update_layout(self):
        #Przelicza pozycje po zmianie rozmiaru okna
        cx = self.app.width // 2
        cy = self.app.height // 2

        if self.bg_original:
            self.bg_image = pygame.transform.scale(self.bg_original, (self.app.width, self.app.height))

        #UKŁADANIE BLOKU PRZYCISKÓW
        step = self.BTN_H + self.GAP
        center_y = cy + 50

        self.btn_settings.centerx = cx
        self.btn_settings.centery = center_y

        self.btn_start.centerx = cx
        self.btn_start.centery = center_y - step

        self.btn_quit.centerx = cx
        self.btn_quit.centery = center_y + step

        #USTAWIENIA (UI)
        self.slider_rect.center = (cx, 250)
        self.btn_res.center = (cx, 330)
        self.btn_fullscreen.center = (cx, 400)
        self.btn_back.center = (cx, 500)

        # Aktualizujemy hitbox gałki (żeby po zmianie rozdzielczości była w dobrym miejscu do kliknięcia)
        self.sync_knob_to_volume()

    def sync_knob_to_volume(self):
        #Pomocnicza funkcja ustawiająca gałkę idealnie wg aktualnej głośności
        current_vol = self.app.sound.volume
        knob_x = self.slider_rect.x + (self.slider_rect.width * current_vol)
        self.slider_knob.center = (int(knob_x), self.slider_rect.centery)

    def handle_click(self, pos):
        if self.state == "MAIN":
            if self.btn_start.collidepoint(pos):
                self.app.change_state("GAME")
            elif self.btn_settings.collidepoint(pos):
                self.app.sound.play_click()
                self.state = "SETTINGS"
            elif self.btn_quit.collidepoint(pos):
                self.app.running = False

        elif self.state == "SETTINGS":
            # Kliknięcie w suwak przesuwa gałkę
            if self.slider_rect.collidepoint(pos) or self.slider_knob.collidepoint(pos):
                self.update_volume(pos[0])

            elif self.btn_res.collidepoint(pos):
                self.app.sound.play_click()
                self.res_idx = (self.res_idx + 1) % len(RESOLUTIONS)
                w, h = RESOLUTIONS[self.res_idx]
                self.app.set_resolution(w, h)

            elif self.btn_fullscreen.collidepoint(pos):
                self.app.sound.play_click()
                self.app.toggle_fullscreen()

            elif self.btn_back.collidepoint(pos):
                self.app.sound.play_click()
                self.state = "MAIN"

    def handle_drag(self, pos, buttons):
        if self.state == "SETTINGS" and buttons[0]:
            # Sprawdzamy czy myszka jest w okolicy suwaka
            if self.slider_rect.collidepoint(pos[0], self.slider_rect.y) or \
                    (pos[0] > self.slider_rect.left - 20 and pos[0] < self.slider_rect.right + 20 and \
                     pos[1] > self.slider_rect.top - 20 and pos[1] < self.slider_rect.bottom + 20):
                self.update_volume(pos[0])

    def update_volume(self, mouse_x):
        """Aktualizuje głośność na podstawie pozycji myszy X"""
        # Ograniczamy X do krawędzi suwaka
        x = max(self.slider_rect.left, min(mouse_x, self.slider_rect.right))

        # Obliczamy procent (0.0 - 1.0)
        pct = (x - self.slider_rect.left) / self.slider_rect.width
        self.app.sound.set_volume(pct)

        # Od razu synchronizujemy gałkę
        self.sync_knob_to_volume()

    def draw(self):
        screen = self.app.screen

        if self.bg_image:
            screen.blit(self.bg_image, (0, 0))
            if self.state == "SETTINGS":
                overlay = pygame.Surface((400, 600))
                overlay.set_alpha(150)
                overlay.fill((0, 0, 0))
                screen.blit(overlay, overlay.get_rect(center=(self.app.width // 2, self.app.height // 2)))
        else:
            screen.fill(BG_COLOR)

        title = self.app.title_font.render("FOREST VALLEY", True, GOLD)
        title_shadow = self.app.title_font.render("FOREST VALLEY", True, BLACK)
        t_pos = (self.app.width // 2 - title.get_width() // 2, 50)
        screen.blit(title_shadow, (t_pos[0] + 2, t_pos[1] + 2))
        screen.blit(title, t_pos)

        if self.state == "MAIN":
            self.draw_img_btn(screen, self.btn_start, "play")
            self.draw_img_btn(screen, self.btn_settings, "setting")
            self.draw_img_btn(screen, self.btn_quit, "quit")

        elif self.state == "SETTINGS":
            self.sync_knob_to_volume()

            lbl_vol = self.app.font.render(f"Głośność: {int(self.app.sound.volume * 100)}%", True, WHITE)
            screen.blit(lbl_vol, (self.slider_rect.x, self.slider_rect.y - 25))

            pygame.draw.rect(screen, (100, 100, 100), self.slider_rect, border_radius=5)
            pygame.draw.circle(screen, GOLD, self.slider_knob.center, 10)

            # Przycisk Rozdzielczości
            w, h = RESOLUTIONS[self.res_idx]
            self.draw_standard_btn(screen, self.btn_res, f"Rozdzielczość: {w}x{h}", (60, 60, 80))

            # Przycisk Fullscreen
            fs_txt = "Pełny Ekran: TAK" if self.app.fullscreen else "Pełny Ekran: NIE"
            col_fs = (50, 150, 50) if self.app.fullscreen else (150, 50, 50)
            self.draw_standard_btn(screen, self.btn_fullscreen, fs_txt, col_fs)

            # Przycisk Powrót
            self.draw_standard_btn(screen, self.btn_back, "WRÓĆ", (100, 100, 100))

    def draw_img_btn(self, screen, rect, img_key):
        img = self.btn_images.get(img_key)
        is_hovered = rect.collidepoint(pygame.mouse.get_pos())

        if img:
            if is_hovered:
                w, h = rect.width + 4, rect.height + 4
                scaled = pygame.transform.smoothscale(img, (w, h))
                new_rect = scaled.get_rect(center=rect.center)
                screen.blit(scaled, new_rect)
            else:
                screen.blit(img, rect)
        else:
            self.draw_standard_btn(screen, rect, img_key.upper(), (100, 100, 100))

    def draw_standard_btn(self, screen, rect, text, color):
        if rect.collidepoint(pygame.mouse.get_pos()):
            color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        s = pygame.Surface((rect.width, rect.height))
        s.set_alpha(230)
        s.fill(color)
        screen.blit(s, (rect.x, rect.y))
        pygame.draw.rect(screen, WHITE, rect, 2)
        txt_surf = self.app.font.render(text, True, WHITE)
        txt_rect = txt_surf.get_rect(center=rect.center)
        screen.blit(txt_surf, txt_rect)