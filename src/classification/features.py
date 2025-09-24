from __future__ import annotations
import pandas as pd
import numpy as np

REQUIRED_COLS = ["workout_id", "avg_pace", "distance_mi", "duration_sec"]
OPTIONAL_COLS = ["steps"]

def _quality_mask(df: pd.DataFrame) -> pd.Series:
    return (
        (df["duration_sec"] >= 180) &
        (df["distance_mi"] >= 0.1) &
        (df["avg_pace"].between(3, 30))
    )

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if "steps" not in df.columns:
        df["steps"] = np.nan
    df["steps_per_min"] = df.apply(lambda r: float(r["steps"]) / (r["duration_sec"]/60.0) if (pd.notna(r["steps"]) and r["duration_sec"]>0) else np.nan, axis=1)
    df["speed_mph"] = df.apply(lambda r: float(r["distance_mi"]) / (r["duration_sec"]/3600.0) if r["duration_sec"]>0 else np.nan, axis=1)
    df["is_valid"] = _quality_mask(df)
    cols = ["workout_id","avg_pace","distance_mi","duration_sec","steps","steps_per_min","speed_mph","is_valid"]
    return df[cols].set_index("workout_id")
