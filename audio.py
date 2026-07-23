import pygame

pygame.mixer.init()

class Music:
    def __init__(self):
        self.current = None
        self.volume = 100

        self.track = {
        "night": "all_sound/music/ogg_files/The_night_theme.ogg",
        "home":  "all_sound/music/ogg_files/Home_theme.ogg",
        }

    def switch(self, track_key):
        global current

        self.current = track_key

        path = self.track.get(track_key)
        if path:
            print(f"[audio] loading: {path}")
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.volume/ 100)
            pygame.mixer.music.play(-1)
            print(f"[audio] playing: {pygame.mixer.music.get_busy()}")
            print(self.volume)

    def next(self, next):
    
        key =  list(self.track.keys())
        song_index = key.index(self.current)

        next_song = key[(song_index + next) % len(key)]
        self.switch(next_song)
        
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

        self.paths = {
            "down": "all_sound/sound_fx/ogg_files/down.ogg",
            "up": "all_sound/sound_fx/ogg_files/up.ogg",
            "press": "all_sound/sound_fx/ogg_files/press.ogg"
        }

        self.track = {key: pygame.mixer.Sound(path) for key, path in self.paths.items()}
        self.set_volume(self.volume)

    def play(self, key):
        self.track[key].play()

    def set_volume(self, v):
        self.volume = max(0, min(100, v))
        for sound in self.track.values():
            sound.set_volume(self.volume / 100)

music = Music()
soundfx = Soundfx()