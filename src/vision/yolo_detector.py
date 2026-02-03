"""
YOLO11 detector for real-time object detection (AI showcase).
Runs on GPU when available; can overlay detections on camera feed.
"""

import numpy as np
import cv2
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

YOLO_AVAILABLE = False
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO = None


class YOLODetector:
    """YOLO11-based object detector for optional AR/overlay effects."""

    def __init__(self, model_name=None, device=None, confidence=0.5):
        self.model_name = model_name or config.YOLO_MODEL
        self.device = device or config.YOLO_DEVICE
        self.confidence = confidence or config.YOLO_CONFIDENCE
        self._model = None
        if YOLO_AVAILABLE and YOLO is not None:
            try:
                self._model = YOLO(self.model_name)
            except Exception:
                self._model = YOLO("yolo11n.pt")

    def detect(self, frame_bgr):
        """
        Run detection on BGR frame. Returns list of detections:
        [{bbox: (x1,y1,x2,y2), class_id, class_name, confidence}, ...]
        """
        if self._model is None:
            return []
        try:
            results = self._model(
                frame_bgr,
                conf=self.confidence,
                device=self.device if self._device_available() else "cpu",
                verbose=False,
            )
        except Exception:
            results = self._model(frame_bgr, conf=self.confidence, verbose=False)
        out = []
        if not results or len(results) == 0:
            return out
        r = results[0]
        if r.boxes is None:
            return out
        for box in r.boxes:
            xyxy = box.xyxy[0].cpu().numpy()
            cid = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            name = r.names.get(cid, "?")
            out.append({
                "bbox": tuple(map(float, xyxy)),
                "class_id": cid,
                "class_name": name,
                "confidence": conf,
            })
        return out

    def _device_available(self):
        try:
            import torch
            return "cuda" in str(self.device) and torch.cuda.is_available()
        except Exception:
            return False

    def draw_detections(self, frame_bgr, detections, color=(0, 255, 0), thickness=2):
        """Draw bounding boxes and labels on frame."""
        for d in detections:
            x1, y1, x2, y2 = map(int, d["bbox"])
            label = f"{d['class_name']} {d['confidence']:.2f}"
            cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), color, thickness)
            cv2.putText(
                frame_bgr, label, (x1, max(0, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA,
            )
        return frame_bgr
