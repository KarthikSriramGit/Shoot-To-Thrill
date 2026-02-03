"""
Particle effects: explosions, sparks.
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


class Particle:
    """Single particle (sphere) that moves and fades."""

    def __init__(self, position, velocity, lifetime=0.5, scale=0.3, col=None):
        self.position = Vec3(position) if hasattr(position, "__len__") else position
        self.velocity = Vec3(velocity) if velocity else Vec3(0, 0, 0)
        self.lifetime = lifetime
        self.scale = scale
        self.col = col or color.orange
        self.entity = None
        self._spawn_time = time.perf_counter()
        self._alive = True
        if URSINA_AVAILABLE:
            self.entity = Entity(
                model="sphere",
                scale=scale,
                position=self.position,
                color=self.col,
                alpha=0.9,
                double_sided=True,
            )

    def update(self, dt):
        if not self._alive:
            return False
        elapsed = time.perf_counter() - self._spawn_time
        if elapsed >= self.lifetime:
            self.destroy()
            return False
        self.position += self.velocity * dt
        if self.entity:
            self.entity.position = self.position
            self.entity.alpha = 0.9 * (1.0 - elapsed / self.lifetime)
        return True

    def destroy(self):
        self._alive = False
        if URSINA_AVAILABLE and self.entity:
            destroy(self.entity)
            self.entity = None


class ParticleSystem:
    """Spawn and update particles (explosions)."""

    def __init__(self):
        self.particles = []

    def explode(self, position, count=12, speed=8.0, lifetime=0.5):
        for _ in range(count):
            vel = Vec3(
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                random.uniform(-1, 1),
            ).normalized() * speed
            p = Particle(position, vel, lifetime=lifetime, col=color.rgb(255, 180, 80))
            self.particles.append(p)

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]
