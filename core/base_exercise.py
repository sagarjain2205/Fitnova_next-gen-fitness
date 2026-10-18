import math 
from abc import ABC, abstractmethod


class BaseExercise(ABC):
    def __init__(self):
        self.reps = 0
        self.stage = None

    def calculate_angle(self, a, b, c):
        try:
            ax, ay = a[0] - b[0], a[1] - b[1]
            cx, cy = c[0] - b[0], c[1] - b[1]

            dot = ax * cx + ay * cy

            mag_a = math.sqrt(ax ** 2 + ay ** 2)
            mag_c = math.sqrt(cx ** 2 + cy ** 2)

            denom = mag_a * mag_c
            if denom == 0 or math.isnan(denom):
                return 0.0

            cos_angle = max(-1.0, min(1.0, dot / denom))
            if math.isnan(cos_angle):
                return 0.0

            return math.degrees(math.acos(cos_angle))
        except Exception:
            return 0.0

    def get_point(self, landmarks, idx):
        try:
            p = landmarks[idx]
            x = 0.0 if (p.x is None or math.isnan(p.x)) else float(p.x)
            y = 0.0 if (p.y is None or math.isnan(p.y)) else float(p.y)
            return (x, y)
        except Exception:
            return (0.0, 0.0)

    def get_vis(self, landmarks, idx):
        try:
            v = landmarks[idx].visibility
            return 0.0 if v is None else float(v)
        except Exception:
            return 0.0

    @abstractmethod
    def process(self, landmarks):
        pass

    @abstractmethod
    def reset(self):
        pass
