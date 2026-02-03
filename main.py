"""
Iron Man Arc Reactor Game - Shoot To Thrill
Entry point. Run with: python main.py
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from src.game.game_manager import GameManager


def main():
    gm = GameManager(
        width=config.WINDOW_WIDTH,
        height=config.WINDOW_HEIGHT,
        fullscreen=config.FULLSCREEN,
    )
    gm.run()


if __name__ == "__main__":
    main()
