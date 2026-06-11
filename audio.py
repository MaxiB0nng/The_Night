import pygame

track = {
    "home":  "music/ogg_files/Home_theme.ogg",
    "night": "music/ogg_files/The_night_theme.ogg",
}


_current = None
enabled = True
volume = 1.0


def switch(track_key):
    global _current
    if not enabled or track_key == _current:
        return
    _current = track_key
    path = track.get(track_key)
    if path:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)


def stop():
    pygame.mixer.music.stop()
    global _current
    _current = None

def toggle():
    global enabled
    enabled = not enabled
    if enabled:
        switch(_current or "home")  # resume
    else:
        stop()

def set_volume(v):
    global volume
    volume = max(0.0, min(1.0, v))
    pygame.mixer.music.set_volume(volume)