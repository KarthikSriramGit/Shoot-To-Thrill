# Shoot To Thrill — Iron Man Arc Reactor Game

A 3D hand-controlled shooter where you fly through the sky and take down Ultron drones using repulsor beams. Built with **Python**, **computer vision** (MediaPipe Hands + YOLO11), **Ursina 3D**, and a **Jarvis-style voice AI** you can talk to.

## Features

- **Dual-hand repulsor control**: Use both hands to aim and shoot. Open palm to aim, pull your hand back then release to fire, close fist to recharge energy.
- **Computer vision**: MediaPipe Hands for real-time hand tracking; optional YOLO11 for object detection (AI showcase).
- **3D flying shooter**: Procedural sky, clouds, wave-based Ultron enemies with increasing difficulty. Supports **all resolutions** including **5120×1440** super ultrawide.
- **GPU-friendly**: Designed to run well on NVIDIA RTX 3070 (OpenGL via Ursina, YOLO on CUDA when available).
- **Jarvis AI**: Voice assistant with speech recognition, LLM conversation (OpenAI), and TTS. Ask for status, help, or chat during the game.

## Requirements

- Python 3.10+
- Webcam
- Microphone (for Jarvis)
- Optional: NVIDIA GPU (CUDA) for YOLO and smoother graphics
- Optional: `OPENAI_API_KEY` for Jarvis conversation and Whisper

## Installation

1. Clone the repo and enter the project folder:
   ```bash
   cd Shoot-To-Thrill
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   # or: source venv/bin/activate  # Linux/macOS
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. For GPU (CUDA) with PyTorch (YOLO, etc.):
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
   ```

5. Optional: set `OPENAI_API_KEY` for Jarvis and Whisper:
   ```bash
   set OPENAI_API_KEY=your_key_here   # Windows
   export OPENAI_API_KEY=your_key_here # Linux/macOS
   ```

## Running the game

```bash
python main.py
```

- **Resolution**: Edit `config.py` and set `WINDOW_WIDTH`, `WINDOW_HEIGHT`, or use `SUPPORTED_RESOLUTIONS` (e.g. `"super_ultrawide": (5120, 1440)`).
- **Fullscreen**: Set `FULLSCREEN = True` in `config.py` if desired.

## Controls (gestures)

| Gesture        | Action                          |
|----------------|----------------------------------|
| Open palm      | Aim (move hand to point)        |
| Pull hand back | Charge repulsor                  |
| Release        | Fire repulsor                    |
| Closed fist    | Recharge energy                 |

You can also talk to Jarvis (e.g. "status", "help", "what wave is it?").

## Project structure

```
Shoot-To-Thrill/
├── main.py              # Entry point
├── config.py            # Resolution, gameplay, vision, Jarvis settings
├── requirements.txt
├── src/
│   ├── game/             # Game loop, player, enemies, collision, audio
│   ├── vision/           # Camera, MediaPipe hands, gesture detection, YOLO11
│   ├── graphics/         # Ursina scene, repulsor beams, particles, HUD
│   └── jarvis/           # Voice assistant, STT, TTS, LLM conversation
└── assets/
    ├── models/
    ├── textures/
    ├── sounds/           # repulsor.ogg, explosion.ogg; BGM in project root
    └── fonts/
```

## Optional assets

- **Sounds**: Place `repulsor.ogg` and `explosion.ogg` in `assets/sounds/` for repulsor and explosion SFX. BGM can be placed in project root (e.g. `Christmas_Box_Pops.mp3`) or in `assets/sounds/` and referenced in `config` / `src/game/audio.py`.

## Performance (RTX 3070)

- YOLO uses `cuda:0` by default (`config.YOLO_DEVICE`). Set to `"cpu"` if you have no NVIDIA GPU.
- The game window uses vsync for smooth rendering. For ultrawide (e.g. 5120×1440), keep vsync on unless you need uncapped FPS for benchmarking.

## License

Use and modify as you like. Original Christmas Box game credits: ECE-GY 6183 DSP Lab (Vanshika Sachdev & Karthik Sriram). This Iron Man variant extends that project with CV, 3D, and AI voice.
