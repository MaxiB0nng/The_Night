import pygame

class Music:
    def __init__(self):
        self.current = None
        self.volume = 100

        self.track = {
        "night": "music\ogg_files\The_night_theme.ogg",
        "home":  "music\ogg_files\Home_theme.ogg",
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
        
        self.track = {
        "down": "sound_fx/down.mid",
        "up": "sound_fx/up.mid",
        "press": "sound_fx/press.mid",
        }

    def set_volume(self, v):
        self.volume = max(0, min(100, v))
        pygame.mixer.Sound.set_volume(self.volume/100)


        
music = Music()
