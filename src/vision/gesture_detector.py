"""
Custom gesture detection for Iron Man repulsor control.
Open palm = aim, pull back = charge, release = fire, closed fist = recharge.
"""

from enum import Enum
from collections import deque
import time


class HandState(Enum):
    IDLE = 0
    AIMING = 1
    CHARGING = 2
    FIRING = 3
    RECHARGING = 4


class HandGestureState:
    """State for one hand (left or right)."""

    def __init__(self, pull_back_threshold=0.03, smoothing=0.2, charge_frames=3):
        self.state = HandState.IDLE
        self.pull_back_threshold = pull_back_threshold
        self.smoothing = smoothing
        self.charge_frames = charge_frames
        self._z_history = deque(maxlen=15)
        self._aim_pos = (0.5, 0.5)  # normalized x, y
        self._last_fire_time = 0.0
        self._fire_cooldown = 0.15
        self._was_charging = False

    def _point(self, landmarks, i):
        p = landmarks[i]
        if hasattr(p, "x"):
            return (p.x, p.y, p.z)
        return p

    def update(self, landmarks, handedness="Right"):
        """
        Update state from MediaPipe hand landmarks.
        landmarks: list of 21 (x, y, z) or objects with .x .y .z
        """
        if not landmarks or len(landmarks) < 21:
            self.state = HandState.IDLE
            return
        wrist = self._point(landmarks, 0)
        mid_mcp = self._point(landmarks, 9)
        x = (wrist[0] + mid_mcp[0]) / 2
        y = (wrist[1] + mid_mcp[1]) / 2
        z = wrist[2]
        self._z_history.append((time.perf_counter(), z))
        # Smooth aim position
        self._aim_pos = (
            self._aim_pos[0] * (1 - self.smoothing) + x * self.smoothing,
            self._aim_pos[1] * (1 - self.smoothing) + y * self.smoothing,
        )
        is_open = self._is_open_palm(landmarks)
        is_fist = self._is_closed_fist(landmarks)
        if is_fist:
            self.state = HandState.RECHARGING
            self._was_charging = False
            return
        if not is_open:
            self.state = HandState.IDLE
            self._was_charging = False
            return
        # Open palm: check for pull-back then release (fire)
        z_velocity = self._z_velocity()
        now = time.perf_counter()
        if now - self._last_fire_time < self._fire_cooldown:
            self.state = HandState.AIMING
            return
        if z_velocity > self.pull_back_threshold:
            self._was_charging = True
            self.state = HandState.CHARGING
        elif self._was_charging and z_velocity < -self.pull_back_threshold:
            self.state = HandState.FIRING
            self._last_fire_time = now
            self._was_charging = False
        else:
            self.state = HandState.AIMING
            if abs(z_velocity) < self.pull_back_threshold * 0.5:
                self._was_charging = False

    def _z_velocity(self):
        if len(self._z_history) < 5:
            return 0.0
        t0, z0 = self._z_history[0]
        t1, z1 = self._z_history[-1]
        dt = t1 - t0
        if dt < 1e-6:
            return 0.0
        return (z1 - z0) / dt

    def _is_open_palm(self, landmarks):
        """True if fingers are extended (open palm)."""
        try:
            p4, p3 = self._point(landmarks, 4), self._point(landmarks, 3)
            p8, p6 = self._point(landmarks, 8), self._point(landmarks, 6)
            p12, p10 = self._point(landmarks, 12), self._point(landmarks, 10)
            p16, p14 = self._point(landmarks, 16), self._point(landmarks, 14)
            p20, p18 = self._point(landmarks, 20), self._point(landmarks, 18)
            thumb_open = p4[1] < p3[1] or abs(p4[0] - p3[0]) > 0.05
            index_open = p8[1] < p6[1]
            middle_open = p12[1] < p10[1]
            ring_open = p16[1] < p14[1]
            pinky_open = p20[1] < p18[1]
            return (index_open and middle_open and ring_open and pinky_open) or thumb_open
        except (IndexError, AttributeError):
            return False

    def _is_closed_fist(self, landmarks):
        """True if all fingers are curled (fist)."""
        try:
            p8, p6 = self._point(landmarks, 8), self._point(landmarks, 6)
            p12, p10 = self._point(landmarks, 12), self._point(landmarks, 10)
            p16, p14 = self._point(landmarks, 16), self._point(landmarks, 14)
            p20, p18 = self._point(landmarks, 20), self._point(landmarks, 18)
            p4, p2 = self._point(landmarks, 4), self._point(landmarks, 2)
            index_curled = p8[1] > p6[1]
            middle_curled = p12[1] > p10[1]
            ring_curled = p16[1] > p14[1]
            pinky_curled = p20[1] > p18[1]
            thumb_curled = abs(p4[0] - p2[0]) < 0.08 and p4[1] > p2[1]
            return index_curled and middle_curled and ring_curled and pinky_curled
        except (IndexError, AttributeError):
            return False

    @property
    def aim_position(self):
        """Normalized (x, y) in [0,1] for screen mapping."""
        return self._aim_pos


class GestureDetector:
    """Dual-hand gesture detector for repulsor control."""

    def __init__(self, pull_back_threshold=0.03, smoothing=0.2):
        self.left = HandGestureState(pull_back_threshold, smoothing)
        self.right = HandGestureState(pull_back_threshold, smoothing)

    def update(self, multi_hand_landmarks, multi_handedness):
        """
        Update both hands from MediaPipe results.
        multi_hand_landmarks: list of 21 landmark lists
        multi_handedness: list of handedness labels ("Left", "Right")
        """
        self.left.state = HandState.IDLE
        self.right.state = HandState.IDLE
        if not multi_hand_landmarks:
            return
        for landmarks, handedness in zip(multi_hand_landmarks, multi_handedness or []):
            if hasattr(handedness, "classification") and handedness.classification:
                label = handedness.classification[0].label
            else:
                label = "Right"
            lm_list = list(landmarks.landmark) if hasattr(landmarks, "landmark") else landmarks
            if label == "Left":
                self.left.update(lm_list, label)
            else:
                self.right.update(lm_list, label)

    def get_left_state(self):
        return self.left.state

    def get_right_state(self):
        return self.right.state

    def get_left_aim(self):
        return self.left.aim_position

    def get_right_aim(self):
        return self.right.aim_position
