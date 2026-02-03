"""
Game audio: repulsor fire, explosions, optional BGM.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

try:
    import pygame
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    PYGAME_MIXER_AVAILABLE = True
except Exception:
    PYGAME_MIXER_AVAILABLE = False

_sounds = {}
_sound_files = {
    "repulsor": "repulsor.ogg",
    "explosion": "explosion.ogg",
    "bgm": "Christmas_Box_Pops.mp3",
}


def _path(name):
    f = _sound_files.get(name)
    if not f:
        return None
    p = os.path.join(config.SOUNDS_DIR, f)
    if os.path.isfile(p):
        return p
    p = os.path.join(config.PROJECT_ROOT, f)
    return p if os.path.isfile(p) else None


def play_repulsor():
    if not PYGAME_MIXER_AVAILABLE:
        return
    path = _path("repulsor")
    if path:
        try:
            s = _sounds.get("repulsor")
            if s is None:
                s = pygame.mixer.Sound(path)
                _sounds["repulsor"] = s
            s.play()
        except Exception:
            pass


def play_explosion():
    if not PYGAME_MIXER_AVAILABLE:
        return
    path = _path("explosion")
    if path:
        try:
            s = _sounds.get("explosion")
            if s is None:
                s = pygame.mixer.Sound(path)
                _sounds["explosion"] = s
            s.play()
        except Exception:
            pass


def play_bgm(loop=-1):
    if not PYGAME_MIXER_AVAILABLE:
        return
    path = _path("bgm")
    if path:
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(loop)
        except Exception:
            pass


def stop_bgm():
    if PYGAME_MIXER_AVAILABLE:
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
