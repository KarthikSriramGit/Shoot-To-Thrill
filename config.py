"""
Iron Man Arc Reactor Game - Configuration
Supports all resolutions including 5120x1440 super ultrawide.
"""

import os

# -----------------------------------------------------------------------------
# Resolution & Display
# -----------------------------------------------------------------------------
SUPPORTED_RESOLUTIONS = {
    "1080p": (1920, 1080),
    "1440p": (2560, 1440),
    "4K": (3840, 2160),
    "ultrawide_1080": (3440, 1440),
    "super_ultrawide": (5120, 1440),
}

# Default to super ultrawide; can be overridden by auto-detect or user
DEFAULT_RESOLUTION = "super_ultrawide"
WINDOW_WIDTH, WINDOW_HEIGHT = SUPPORTED_RESOLUTIONS[DEFAULT_RESOLUTION]

# Fullscreen or windowed
FULLSCREEN = False

# -----------------------------------------------------------------------------
# Gameplay
# -----------------------------------------------------------------------------
PLAYER_MAX_HEALTH = 100
PLAYER_MAX_ENERGY = 100
ENERGY_RECHARGE_RATE = 15.0  # per second when fist closed
REPULSOR_ENERGY_COST = 8.0
REPULSOR_COOLDOWN = 0.15  # seconds between shots per hand

# Wave difficulty scaling
WAVE_ENEMY_COUNT_BASE = 3
WAVE_ENEMY_COUNT_INCREMENT = 2
WAVE_SPAWN_INTERVAL = 2.0  # seconds between spawns in a wave
BOSS_WAVE_INTERVAL = 5  # every N waves

# -----------------------------------------------------------------------------
# Vision / Hand Tracking
# -----------------------------------------------------------------------------
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
HAND_TRACKING_CONFIDENCE = 0.6
MIN_HAND_PRESENCE = 0.5
PULL_BACK_THRESHOLD = 0.03  # z-depth change to trigger fire
GESTURE_SMOOTHING = 0.2  # smoothing factor for aim position

# -----------------------------------------------------------------------------
# YOLO11 (optional showcase) & GPU
# -----------------------------------------------------------------------------
YOLO_MODEL = "yolo11n.pt"  # nano for speed; use yolo11m for better accuracy
YOLO_CONFIDENCE = 0.5
YOLO_DEVICE = "cuda:0"  # RTX 3070 - set to "cpu" if no NVIDIA GPU
# Ursina uses OpenGL; vsync is enabled in the game window for smooth RTX 3070 output

# -----------------------------------------------------------------------------
# Jarvis AI
# -----------------------------------------------------------------------------
JARVIS_SYSTEM_PROMPT = """You are J.A.R.V.I.S., Tony Stark's AI assistant, now assisting the pilot in an Iron Man arc reactor shooting game. You provide tactical commentary, respond to voice commands, and give brief, witty status updates. Keep responses short (1-2 sentences) during combat. You can discuss game state: health, energy, wave, score. Be helpful and in character."""
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
JARVIS_TTS_VOICE = "en-GB-RyanNeural"  # Edge TTS; British, clear
JARVIS_STT_LANGUAGE = "en"

# -----------------------------------------------------------------------------
# Paths (relative to project root)
# -----------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
MODELS_DIR = os.path.join(ASSETS_DIR, "models")
TEXTURES_DIR = os.path.join(ASSETS_DIR, "textures")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
SHADERS_DIR = os.path.join(PROJECT_ROOT, "src", "graphics", "shaders")
