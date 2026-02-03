"""
Main game loop: Ursina window, vision pipeline, gameplay, collision, scoring.
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

# Optional: vision (may fail if cv2/mediapipe missing)
from enum import Enum
class _HandStateFallback(Enum):
    IDLE = 0
    AIMING = 1
    CHARGING = 2
    FIRING = 3
    RECHARGING = 4
try:
    from src.vision.camera import CameraCapture
    from src.vision.hand_tracker import HandTracker
    from src.vision.gesture_detector import GestureDetector, HandState
    VISION_AVAILABLE = True
except Exception:
    VISION_AVAILABLE = False
    HandState = _HandStateFallback
    CameraCapture = None
    HandTracker = None
    GestureDetector = None

game_audio = None
try:
    from ursina import Ursina, window, camera
    from src.graphics.scene import GameScene
    from src.graphics.repulsor_beam import RepulsorBeamManager
    from src.graphics.particles import ParticleSystem
    from src.graphics.hud import GameHUD
    from src.game.player import Player
    from src.game.enemy_spawner import EnemySpawner
    from src.game.collision import check_all_beams_vs_enemies
    try:
        from src.game import audio as game_audio
    except Exception:
        game_audio = None
    URSINA_AVAILABLE = True
except ImportError:
    URSINA_AVAILABLE = False

try:
    from src.jarvis.voice_assistant import JarvisVoiceAssistant
    JARVIS_AVAILABLE = True
except Exception:
    JARVIS_AVAILABLE = False


SCORE_PER_KILL = {"drone": 10, "standard": 30, "heavy": 100}
BEAM_DAMAGE = 25


class GameManager:
    def __init__(self, width=1920, height=1080, fullscreen=False):
        self.width = width or config.WINDOW_WIDTH
        self.height = height or config.WINDOW_HEIGHT
        self.fullscreen = fullscreen
        self.app = None
        self.scene = None
        self.player = None
        self.beam_manager = None
        self.particle_system = None
        self.spawner = None
        self.hud = None
        self.camera_capture = None
        self.hand_tracker = None
        self.gesture_detector = None
        self._dt = 0.0
        self._last_time = 0.0
        self._game_over = False
        if not URSINA_AVAILABLE:
            return
        window.size = (self.width, self.height)
        window.fullscreen = self.fullscreen
        window.title = "Shoot To Thrill - Iron Man Arc Reactor"
        self.app = Ursina(borderless=False, vsync=True, development_mode=False)
        self.scene = GameScene(self.width, self.height, self.fullscreen, create_app=False)
        self.player = Player()
        self.player.set_camera(camera)
        self.beam_manager = RepulsorBeamManager()
        self.particle_system = ParticleSystem()
        self.spawner = EnemySpawner()
        self.hud = GameHUD(self.width, self.height)
        self.jarvis = None
        if JARVIS_AVAILABLE:
            def game_state():
                return (self.player.health, self.player.energy, self.player.score, self.spawner.wave)
            self.jarvis = JarvisVoiceAssistant(game_state_callback=game_state)
            try:
                self.jarvis.start_listening()
            except Exception:
                pass
        if VISION_AVAILABLE:
            self.gesture_detector = GestureDetector(
                pull_back_threshold=config.PULL_BACK_THRESHOLD,
                smoothing=config.GESTURE_SMOOTHING,
            )
            self.hand_tracker = HandTracker(
                min_detection_confidence=config.HAND_TRACKING_CONFIDENCE,
                min_tracking_confidence=config.MIN_HAND_PRESENCE,
            )
            self.hand_tracker.set_gesture_detector(self.gesture_detector)
            self.camera_capture = CameraCapture()
            try:
                self.camera_capture.start()
            except Exception:
                self.camera_capture = None
        self.spawner.start_next_wave()
        if game_audio:
            try:
                game_audio.play_bgm()
            except Exception:
                pass
        self._last_time = time.perf_counter()
        self.app.update = self._update

    def _update(self):
        if self._game_over:
            return
        now = time.perf_counter()
        self._dt = min(now - self._last_time, 0.1)
        self._last_time = now
        # Vision: get hand state and aim
        left_state = HandState.AIMING
        right_state = HandState.AIMING
        left_aim = (0.5, 0.5)
        right_aim = (0.5, 0.5)
        if VISION_AVAILABLE and self.camera_capture and self.gesture_detector:
            frame = self.camera_capture.read()
            if frame is not None:
                self.hand_tracker.process(frame)
                left_state = self.gesture_detector.get_left_state()
                right_state = self.gesture_detector.get_right_state()
                left_aim = self.gesture_detector.get_left_aim()
                right_aim = self.gesture_detector.get_right_aim()
        # Recharge when fist
        if left_state == HandState.RECHARGING or right_state == HandState.RECHARGING:
            self.player.recharge(self._dt)
        # Fire repulsors
        if left_state == HandState.FIRING and self.player.can_fire_left(now) and self.player.energy >= self.player.repulsor_cost:
            origin, direction = self.player.get_aim_ray_left(left_aim[0], left_aim[1])
            if origin and direction:
                self.beam_manager.fire(origin, direction, hand="left")
                self.player.consume_fire_left(now)
                if game_audio:
                    try:
                        game_audio.play_repulsor()
                    except Exception:
                        pass
        if right_state == HandState.FIRING and self.player.can_fire_right(now) and self.player.energy >= self.player.repulsor_cost:
            origin, direction = self.player.get_aim_ray_right(right_aim[0], right_aim[1])
            if origin and direction:
                self.beam_manager.fire(origin, direction, hand="right")
                self.player.consume_fire_right(now)
                if game_audio:
                    try:
                        game_audio.play_repulsor()
                    except Exception:
                        pass
        # Collision: beams vs enemies
        hits = check_all_beams_vs_enemies(self.beam_manager.beams, self.spawner.enemies)
        for beam, enemy in hits:
            beam.destroy()
            if enemy.take_damage(BEAM_DAMAGE):
                self.particle_system.explode(enemy.get_position())
                variant = getattr(enemy, "variant", "drone")
                self.player.score += SCORE_PER_KILL.get(variant, 10)
        # Update systems
        self.beam_manager.update(self._dt)
        self.spawner.update(self._dt)
        self.particle_system.update(self._dt)
        self.scene.update(self._dt)
        wave_cleared = self.spawner._wave_cleared
        if wave_cleared and len(self.spawner.enemies) == 0:
            self.spawner.start_next_wave()
            if self.jarvis:
                try:
                    self.jarvis.wave_started(self.spawner.wave)
                except Exception:
                    pass
        self.hud.update(self.player.health, self.player.energy, self.player.score, self.spawner.wave)
        if not self.player.is_alive():
            self._game_over = True

    def run(self):
        if not URSINA_AVAILABLE:
            print("Ursina not available. Install: pip install ursina")
            return
        try:
            self.app.run()
        finally:
            if self.camera_capture:
                try:
                    self.camera_capture.stop()
                except Exception:
                    pass
            if self.jarvis:
                try:
                    self.jarvis.stop_listening()
                except Exception:
                    pass
            if game_audio:
                try:
                    game_audio.stop_bgm()
                except Exception:
                    pass
