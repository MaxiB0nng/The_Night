import pygame

class Music:
    def __init__(self):
        self.current = None
        self.volume = 100

        self.track = {
        "home":  "music/ogg_files/Home_theme.ogg",
        "night": "music/ogg_files/The_night_theme.ogg",
        }

    def switch(self, track_key):
        self.current = track_key
        path = self.track.get(track_key)
        if path:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.volume/ 100)
            pygame.mixer.music.play(-1)

    def stop(self):
        pygame.mixer.music.stop()
        self.current = None

    def set_volume(self, v):
        self.volume = max(0, min(100, v))
        pygame.mixer.music.set_volume(self.volume/ 100)

class Soundfx:
    def __init__(self):
        self.current = None
        self.volume = 100
        
        self.track = {
        "down": "sound_fx\ogg_files\down.ogg",
        "up": "sound_fx\ogg_files\up.ogg",
        "press": "sound_fx\ogg_files\press.ogg"
        }
        