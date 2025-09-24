from __future__ import annotations
import pandas as pd
from .utils import CLASSES

def classify_pace(avg_pace: float) -> str:
    if avg_pace < 12: return "Run"
    elif avg_pace > 20: return "Walk"
    else: return "Hybrid"

def predict_proba(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        label = classify_pace(float(r["avg_pace"])) if r.get("is_valid", True) else "Hybrid"
        if label == "Run": probs = [0.98,0.01,0.01]
        elif label == "Walk": probs = [0.01,0.98,0.01]
        else: probs = [0.01,0.01,0.98]
        rows.append(probs)
    return pd.DataFrame(rows, index=df.index, columns=CLASSES)
