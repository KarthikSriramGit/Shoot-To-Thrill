"""
Hit detection between repulsor beams and Ultron enemies.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from ursina import Vec3
    URSINA_AVAILABLE = True
except ImportError:
    URSINA_AVAILABLE = False


def _distance_point_to_segment(p, a, b):
    """Squared distance from point p to segment a-b (for speed)."""
    ab = Vec3(b) - Vec3(a)
    ap = Vec3(p) - Vec3(a)
    t = max(0, min(1, ap.dot(ab) / (ab.length_squared() + 1e-9)))
    closest = a + ab * t
    return (Vec3(p) - closest).length_squared()


def check_beam_enemy_collision(beam, enemy, hit_radius=3.0):
    """
    Check if beam (with position and direction) hits enemy (position, bounding size).
    beam: RepulsorBeam with get_position(); we use current position and approximate extent.
    enemy: UltronEnemy with get_position() and entity.scale.
    Returns True if hit.
    """
    if not beam or not enemy or not beam.is_alive() or not enemy.is_alive():
        return False
    beam_pos = beam.get_position()
    enemy_pos = enemy.get_position()
    if beam_pos is None or enemy_pos is None:
        return False
    # Simple sphere-sphere: beam is a moving point, enemy has radius ~scale
    dist_sq = (Vec3(beam_pos) - Vec3(enemy_pos)).length_squared()
    enemy_radius = 2.0  # approximate from entity scale
    if hasattr(enemy, "entity") and enemy.entity and hasattr(enemy.entity, "scale"):
        s = enemy.entity.scale
        enemy_radius = max(s[0], s[1], s[2])
    return dist_sq <= (hit_radius + enemy_radius) ** 2


def check_all_beams_vs_enemies(beams, enemies, hit_radius=3.0):
    """
    Check all beams against all enemies. Returns list of (beam, enemy) pairs that hit.
    Caller applies damage and removes beam.
    """
    hits = []
    for beam in beams:
        if not beam.is_alive():
            continue
        for enemy in enemies:
            if not enemy.is_alive():
                continue
            if check_beam_enemy_collision(beam, enemy, hit_radius):
                hits.append((beam, enemy))
                break  # one beam hits one enemy only
    return hits
