"""
MediaPipe Hands integration for dual-hand tracking.
Provides 21 landmarks per hand for the gesture detector.
"""

import cv2
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

try:
    import mediapipe as mp
except ImportError:
    mp = None


class HandTracker:
    """Real-time hand tracking using MediaPipe Hands."""

    def __init__(
        self,
        max_num_hands=2,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5,
    ):
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self._hands = None
        if mp:
            self._hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=max_num_hands,
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence,
            )
        self._mp_hands = mp
        self._gesture_detector = None

    def set_gesture_detector(self, detector):
        self._gesture_detector = detector

    def process(self, frame_bgr):
        """
        Process a BGR frame (e.g. from OpenCV). Returns multi_hand_landmarks and multi_handedness.
        """
        if self._hands is None:
            return None, None
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb)
        if self._gesture_detector and results.multi_hand_landmarks:
            self._gesture_detector.update(
                results.multi_hand_landmarks,
                results.multi_handedness,
            )
        return results.multi_hand_landmarks, results.multi_handedness

    def draw_landmarks(self, frame_bgr, multi_hand_landmarks, multi_handedness):
        """Draw hand landmarks and connections on frame for debug overlay."""
        if not self._mp_hands or not multi_hand_landmarks:
            return frame_bgr
        h, w, _ = frame_bgr.shape
        for hand_landmarks, handedness in zip(
            multi_hand_landmarks,
            multi_handedness or [],
        ):
            for lm in hand_landmarks.landmark:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame_bgr, (cx, cy), 4, (0, 255, 0), -1)
        return frame_bgr

    def close(self):
        if self._hands:
            self._hands.close()
