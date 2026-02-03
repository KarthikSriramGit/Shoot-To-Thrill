"""
3D game scene: sky, clouds, flying effect. Supports ultrawide resolutions.
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

try:
    from ursina import (
        Ursina, Entity, Sky, camera, window,
        Vec3, color, destroy,
        Mesh, load_texture,
    )
    from ursina.prefabs.first_person_controller import FirstPersonController
    URSINA_AVAILABLE = True
except ImportError:
    URSINA_AVAILABLE = False


class CloudEntity:
    """Single cloud for procedural sky."""

    def __init__(self, parent, position, scale, alpha=0.6):
        if not URSINA_AVAILABLE:
            self.entity = None
            return
        self.entity = Entity(
            parent=parent,
            model="sphere",
            scale=scale,
            position=position,
            color=color.white,
            alpha=alpha,
            double_sided=True,
        )
        self.entity.original_x = position.x

    def update(self, dt):
        if self.entity is None:
            return
        # Clouds drift slightly for parallax
        self.entity.x -= 2.0 * dt
        if self.entity.x < -80:
            self.entity.x = 80


class GameScene:
    """3D scene: procedural sky, clouds, flying effect. Resolution-aware."""

    def __init__(self, width=None, height=None, fullscreen=False, create_app=True):
        self.width = width or config.WINDOW_WIDTH
        self.height = height or config.WINDOW_HEIGHT
        self.fullscreen = fullscreen
        self.app = None
        self.sky = None
        self.clouds = []
        self._fly_speed = 20.0
        self._camera_entity = None
        if not URSINA_AVAILABLE:
            return
        if create_app:
            window.size = (self.width, self.height)
            window.fullscreen = self.fullscreen
            window.title = "Shoot To Thrill - Iron Man Arc Reactor"
            self.app = Ursina(
                borderless=False,
                vsync=True,
                development_mode=False,
            )
        self._setup_scene()

    def _setup_scene(self):
        if not URSINA_AVAILABLE:
            return
        # Sky - blue gradient feel (Ursina Sky uses texture or color)
        self.sky = Sky(color=color.rgb(100, 150, 255))
        self.sky.scale = 500
        # Ground / horizon - invisible plane far below for reference (optional)
        # Camera: first-person style, fixed forward for "flying" feel
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        camera.fov = 90
        self._camera_entity = camera
        # Procedural clouds - layers of spheres
        self._spawn_clouds()

    def _spawn_clouds(self):
        import random
        if not URSINA_AVAILABLE:
            return
        # Parent to scene (None = scene) so camera can fly through
        parent = camera  # Sky follows camera; clouds in world space need a scene entity
        try:
            from ursina import scene
            parent = scene
        except Exception:
            parent = camera
        for _ in range(30):
            x = random.uniform(-60, 60)
            y = random.uniform(5, 40)
            z = random.uniform(20, 200)  # ahead of player
            scale = random.uniform(8, 25)
            alpha = random.uniform(0.3, 0.7)
            c = CloudEntity(parent, Vec3(x, y, z), scale, alpha)
            self.clouds.append(c)

    def update(self, dt):
        """Update flying effect and clouds."""
        if not URSINA_AVAILABLE:
            return
        for c in self.clouds:
            c.update(dt)
        # Flying forward: move camera forward through the world
        self._camera_entity.z += self._fly_speed * dt
        # Wrap clouds: move far clouds back ahead when we pass them
        try:
            from ursina import scene
            for c in self.clouds:
                if c.entity and c.entity.z < camera.z - 30:
                    c.entity.z += 230
        except Exception:
            pass

    def set_fly_speed(self, speed):
        self._fly_speed = speed

    def get_camera(self):
        return self._camera_entity

    def run(self):
        """Run Ursina app (blocking). Use only if scene owns the main loop."""
        if self.app:
            self.app.run()

    def step(self):
        """Single frame step (when game loop is external)."""
        if self.app and hasattr(self.app, "step"):
            self.app.step()
