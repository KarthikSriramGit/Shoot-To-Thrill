"""
Threaded webcam capture for hand tracking and optional YOLO overlay.
"""

import threading
import time
import cv2
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config


class CameraCapture:
    """Threaded camera capture; provides latest frame for vision pipeline."""

    def __init__(self, camera_index=None, width=None, height=None):
        self.camera_index = camera_index if camera_index is not None else config.CAMERA_INDEX
        self.width = width or config.CAMERA_WIDTH
        self.height = height or config.CAMERA_HEIGHT
        self._cap = None
        self._frame = None
        self._lock = threading.Lock()
        self._running = False
        self._thread = None

    def start(self):
        self._cap = cv2.VideoCapture(self.camera_index)
        if not self._cap.isOpened():
            raise RuntimeError("Could not open camera")
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        # Wait for first frame
        for _ in range(30):
            with self._lock:
                if self._frame is not None:
                    break
            time.sleep(0.05)

    def _capture_loop(self):
        while self._running and self._cap and self._cap.isOpened():
            ret, frame = self._cap.read()
            if ret:
                with self._lock:
                    self._frame = frame.copy()
            else:
                time.sleep(0.02)

    def read(self):
        """Return latest BGR frame or None."""
        with self._lock:
            return self._frame.copy() if self._frame is not None else None

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        if self._cap:
            self._cap.release()
            self._cap = None
