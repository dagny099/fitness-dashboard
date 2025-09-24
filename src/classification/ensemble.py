from __future__ import annotations
import numpy as np, pandas as pd
from .utils import CLASSES

def blend(*proba_frames: pd.DataFrame, weights: list[float] | None=None) -> pd.DataFrame:
    frames = [p[CLASSES].values for p in proba_frames]
    arr = np.stack(frames, axis=0)
    if weights is None:
        weights = np.ones(arr.shape[0]) / arr.shape[0]
    w = np.asarray(weights).reshape(-1,1,1)
    blended = (arr * w).sum(axis=0)
    blended = blended / blended.sum(axis=1, keepdims=True)
    return pd.DataFrame(blended, index=proba_frames[0].index, columns=CLASSES)
