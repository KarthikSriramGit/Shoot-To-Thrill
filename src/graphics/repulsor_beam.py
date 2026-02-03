"""
Arc reactor repulsor beam: glowing projectile with trail.
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

try:
    from ursina import Entity, Vec3, color, destroy, camera
    URSINA_AVAILABLE = True
except ImportError:
    URSINA_AVAILABLE = False


class RepulsorBeam:
    """Single repulsor beam: moves along direction, despawns after lifetime or distance."""

    def __init__(self, origin, direction, speed=120.0, lifetime=1.0, hand="left"):
        self.origin = Vec3(origin) if origin else None
        self.direction = Vec3(direction).normalized() if direction else None
        self.speed = speed
        self.lifetime = lifetime
        self.hand = hand
        self.entity = None
        self.trail_entities = []
        self._spawn_time = time.perf_counter()
        self._alive = True
        if not URSINA_AVAILABLE:
            return
        self._create_beam()
        self._create_trail()

    def _create_beam(self):
        if not URSINA_AVAILABLE:
            return
        self.entity = Entity(
            model="sphere",
            scale=(0.4, 0.4, 0.8),
            position=Vec3(self.origin),
            color=color.rgb(100, 200, 255),
            alpha=0.95,
            double_sided=True,
        )
        self.entity.look_at(self.entity.position + self.direction)
        self.entity.repulsor_beam = self

    def _create_trail(self):
        # Trail: small quads or spheres behind the beam (simplified: we'll add a few)
        self.trail_entities = []

    def update(self, dt):
        if not self._alive or self.entity is None:
            return False
        elapsed = time.perf_counter() - self._spawn_time
        if elapsed >= self.lifetime:
            self.destroy()
            return False
        self.entity.position += self.direction * self.speed * dt
        return True

    def destroy(self):
        self._alive = False
        if URSINA_AVAILABLE and self.entity:
            destroy(self.entity)
            self.entity = None
        for e in self.trail_entities:
            if e:
                destroy(e)
        self.trail_entities.clear()

    def get_position(self):
        if self.entity:
            return self.entity.world_position
        return self.origin

    def is_alive(self):
        return self._alive


class RepulsorBeamManager:
    """Spawns and updates all active repulsor beams."""

    def __init__(self):
        self.beams = []

    def fire(self, origin, direction, hand="left"):
        beam = RepulsorBeam(origin, direction, hand=hand)
        if beam.entity is not None:
            self.beams.append(beam)
        return beam

    def update(self, dt):
        self.beams = [b for b in self.beams if b.update(dt)]
