# engine/sound.py
import pygame
import os


class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        # ZMIANA: 2% głośności na start
        self.volume = 0.02

        # Ścieżki
        self.music_path = "assets/menu_sound.wav"
        self.click_path = "assets/menu_click.wav"

        # Ładowanie SFX
        self.click_sound = None
        try:
            if os.path.exists(self.click_path):
                self.click_sound = pygame.mixer.Sound(self.click_path)
                self.click_sound.set_volume(self.volume)
        except Exception as e:
            print(f"Błąd dźwięku SFX: {e}")

    def play_music(self):
        if os.path.exists(self.music_path):
            try:
                pygame.mixer.music.load(self.music_path)
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Błąd muzyki: {e}")

    def play_click(self):
        if self.click_sound:
            self.click_sound.play()

    def set_volume(self, val):
        self.volume = val
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(val)
        if self.click_sound:
            self.click_sound.set_volume(val)