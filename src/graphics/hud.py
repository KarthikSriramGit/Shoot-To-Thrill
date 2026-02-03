"""
Iron Man style holographic HUD: health, energy, score, wave.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

try:
    from ursina import WindowPanel, Text, Entity, color, camera
    URSINA_AVAILABLE = True
except ImportError:
    URSINA_AVAILABLE = False


class GameHUD:
    """Heads-up display: health bar, energy, score, wave. Styled for Iron Man."""

    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.health_text = None
        self.energy_text = None
        self.score_text = None
        self.wave_text = None
        if not URSINA_AVAILABLE:
            return
        self._create_hud()

    def _create_hud(self):
        if not URSINA_AVAILABLE:
            return
        # Top-left: health, energy
        self.health_text = Text(
            text="HP: 100",
            position=(-0.85, 0.45),
            scale=2,
            color=color.rgb(0, 255, 100),
            origin=(-0.5, 0.5),
        )
        self.energy_text = Text(
            text="ENERGY: 100",
            position=(-0.85, 0.40),
            scale=2,
            color=color.rgb(100, 200, 255),
            origin=(-0.5, 0.5),
        )
        # Top-right: score, wave
        self.score_text = Text(
            text="SCORE: 0",
            position=(0.85, 0.45),
            scale=2,
            color=color.rgb(255, 220, 100),
            origin=(0.5, 0.5),
        )
        self.wave_text = Text(
            text="WAVE 1",
            position=(0.85, 0.40),
            scale=2,
            color=color.rgb(200, 200, 255),
            origin=(0.5, 0.5),
        )

    def update(self, health, energy, score, wave):
        if not URSINA_AVAILABLE:
            return
        if self.health_text:
            self.health_text.text = f"HP: {max(0, int(health))}"
        if self.energy_text:
            self.energy_text.text = f"ENERGY: {max(0, int(energy))}"
        if self.score_text:
            self.score_text.text = f"SCORE: {score}"
        if self.wave_text:
            self.wave_text.text = f"WAVE {wave}"
