"""
Wave-based enemy spawner: Ultron drones with increasing difficulty.
"""

import sys
import os
import time
import random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config
from .ultron_enemy import UltronEnemy

try:
    from ursina import Vec3, camera
    URSINA_AVAILABLE = True
except ImportError:
    URSINA_AVAILABLE = False


class EnemySpawner:
    """Spawns Ultron enemies in waves with scaling difficulty."""

    def __init__(self):
        self.wave = 0
        self.enemies = []
        self._next_spawn_time = 0.0
        self._spawn_interval = config.WAVE_SPAWN_INTERVAL
        self._enemies_this_wave = 0
        self._enemies_to_spawn = config.WAVE_ENEMY_COUNT_BASE
        self._wave_cleared = True

    def start_next_wave(self):
        self.wave += 1
        self._wave_cleared = False
        self._enemies_this_wave = 0
        self._enemies_to_spawn = (
            config.WAVE_ENEMY_COUNT_BASE
            + (self.wave - 1) * config.WAVE_ENEMY_COUNT_INCREMENT
        )
        self._next_spawn_time = time.perf_counter()

    def update(self, dt):
        now = time.perf_counter()
        # Spawn new enemy if wave not complete and interval passed
        if not self._wave_cleared and self._enemies_this_wave < self._enemies_to_spawn:
            if now >= self._next_spawn_time:
                self._spawn_one()
                self._enemies_this_wave += 1
                self._next_spawn_time = now + self._spawn_interval
        # Update all enemies
        cam_z = camera.z if URSINA_AVAILABLE and camera else 0
        self.enemies = [e for e in self.enemies if e.update(dt, cam_z)]
        if not self._wave_cleared and self._enemies_this_wave >= self._enemies_to_spawn and len(self.enemies) == 0:
            self._wave_cleared = True
        return self._wave_cleared

    def _spawn_one(self):
        # Spawn ahead of camera
        cam_z = camera.z + 40 if URSINA_AVAILABLE and camera else 40
        x = random.uniform(-15, 15)
        y = random.uniform(-5, 15)
        z = cam_z + random.uniform(0, 20)
        # Difficulty scaling
        health = 20 + self.wave * 5
        speed = 12 + self.wave * 0.5
        variant = "drone"
        if self.wave % config.BOSS_WAVE_INTERVAL == 0 and self._enemies_this_wave == 0:
            variant = "heavy"
            health = 100 + self.wave * 10
            speed = 8
        elif self.wave > 2 and random.random() < 0.3:
            variant = "standard"
            health = 40 + self.wave * 5
        e = UltronEnemy(Vec3(x, y, z), health=health, speed=speed, variant=variant)
        self.enemies.append(e)

    def get_enemies(self):
        return self.enemies
