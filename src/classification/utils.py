from typing import Sequence, Tuple
import numpy as np

CLASSES = ["Run", "Walk", "Hybrid"]

def to_label(probs: Sequence[float], hybrid_low: float = 0.45, hybrid_high: float = 0.55) -> Tuple[str, float]:
    probs = np.asarray(probs, dtype=float)
    k = int(np.argmax(probs)); p = float(probs[k])
    if hybrid_low <= p <= hybrid_high:
        return "Hybrid", p
    return CLASSES[k], p
