"""
Player state: health, energy, score. Aim mapping from hand (normalized) to 3D world.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

try:
    from ursina import Vec3, camera
    URSINA_AVAILABLE = True
except ImportError:
    URSINA_AVAILABLE = False
    Vec3 = None
    camera = None


def aim_normalized_to_direction(normalized_x, normalized_y, cam=None):
    """
    Map normalized hand position (0..1, 0..1) to a 3D direction in front of camera.
    Returns (origin_vec3, direction_vec3) for spawning repulsor beams.
    """
    if not URSINA_AVAILABLE or cam is None:
        return (None, None)
    # View space: center (0.5, 0.5) = straight ahead; corners = edges of view
    view_x = (normalized_x - 0.5) * 2.0   # -1 to 1
    view_y = (0.5 - normalized_y) * 2.0  # -1 to 1 (y flip)
    # Build direction: forward + horizontal/vertical offset
    forward = Vec3(cam.forward)
    right = Vec3(cam.right)
    up = Vec3(cam.up)
    # Scale offset by FOV (wider FOV = more spread)
    fov_scale = 1.2
    direction = forward + right * view_x * fov_scale + up * view_y * fov_scale
    direction = direction.normalized()
    origin = Vec3(cam.world_position)
    return (origin, direction)


class Player:
    """Player state and aim mapping for repulsor control."""

    def __init__(self):
        self.health = config.PLAYER_MAX_HEALTH
        self.energy = config.PLAYER_MAX_ENERGY
        self.max_health = config.PLAYER_MAX_HEALTH
        self.max_energy = config.PLAYER_MAX_ENERGY
        self.score = 0
        self._camera = None
        self.recharge_rate = config.ENERGY_RECHARGE_RATE
        self.repulsor_cost = config.REPULSOR_ENERGY_COST
        self.repulsor_cooldown = config.REPULSOR_COOLDOWN
        self._last_fire_left = 0.0
        self._last_fire_right = 0.0

    def set_camera(self, cam):
        self._camera = cam

    def get_aim_ray_left(self, normalized_x, normalized_y):
        """(origin, direction) for left hand repulsor."""
        return aim_normalized_to_direction(normalized_x, normalized_y, self._camera)

    def get_aim_ray_right(self, normalized_x, normalized_y):
        """(origin, direction) for right hand repulsor."""
        return aim_normalized_to_direction(normalized_x, normalized_y, self._camera)

    def can_fire_left(self, current_time):
        return current_time - self._last_fire_left >= self.repulsor_cooldown

    def can_fire_right(self, current_time):
        return current_time - self._last_fire_right >= self.repulsor_cooldown

    def consume_fire_left(self, current_time):
        self._last_fire_left = current_time
        self.energy = max(0, self.energy - self.repulsor_cost)

    def consume_fire_right(self, current_time):
        self._last_fire_right = current_time
        self.energy = max(0, self.energy - self.repulsor_cost)

    def recharge(self, dt):
        """Call when fist closed; restores energy."""
        self.energy = min(self.max_energy, self.energy + self.recharge_rate * dt)

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        return self.health <= 0

    def is_alive(self):
        return self.health > 0
