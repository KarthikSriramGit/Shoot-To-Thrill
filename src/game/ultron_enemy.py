"""
Ultron enemy: 3D entity with AI movement and health.
"""

import sys
import os
import time
import random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

try:
    from ursina import Entity, Vec3, color, destroy
    URSINA_AVAILABLE = True
except ImportError:
    URSINA_AVAILABLE = False


class UltronEnemy:
    """Single Ultron drone: moves toward player, has health."""

    def __init__(self, position, health=30, speed=15.0, variant="drone"):
        self.position = Vec3(position) if position else Vec3(0, 0, 50)
        self.health = health
        self.max_health = health
        self.speed = speed
        self.variant = variant  # drone, standard, heavy
        self.entity = None
        self._alive = True
        self._velocity = Vec3(0, 0, -1).normalized() * speed  # toward camera
        if not URSINA_AVAILABLE:
            return
        self._create_entity()

    def _create_entity(self):
        if not URSINA_AVAILABLE:
            return
        scale = 2.0 if self.variant == "heavy" else (1.5 if self.variant == "standard" else 1.0)
        col = color.rgb(80, 80, 90)  # metallic gray
        self.entity = Entity(
            model="cube",
            scale=(scale * 0.8, scale * 1.2, scale * 0.6),
            position=self.position,
            color=col,
            double_sided=True,
        )
        self.entity.ultron_enemy = self

    def update(self, dt, camera_z=0):
        if not self._alive or self.entity is None:
            return False
        # Move toward player (camera at z)
        self.position.z -= self.speed * dt
        self.position.x += (random.random() - 0.5) * 2 * dt
        self.position.y += (random.random() - 0.5) * 2 * dt
        if self.entity:
            self.entity.position = self.position
        if self.position.z < camera_z - 20:
            self.destroy()
            return False
        return True

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.destroy()
            return True
        return False

    def destroy(self):
        self._alive = False
        if URSINA_AVAILABLE and self.entity:
            destroy(self.entity)
            self.entity = None

    def get_position(self):
        return self.position

    def is_alive(self):
        return self._alive
