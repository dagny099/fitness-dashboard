# Run/Walk/Hybrid Classification — Detailed Briefing
**Date:** 2025-09-10 18:59

## 1) Problem Statement & Constraints
We classify workouts into **Run**, **Walk**, or **Hybrid** from summary metrics. Because a single workout can contain both behaviors, we explicitly model **uncertainty** and treat **Hybrid** as a valid, interpretable outcome. Objectives:
- **Explorability:** Users can toggle algorithms, tune parameters, and compare outcomes.
- **Explainability:** Every prediction ships with a **confidence** and a **rationale**.
- **Reproducibility:** Each batch of predictions is persisted with code/data/param lineage.

---

## 2) Data & Feature Engineering
**Inputs:** `avg_pace`, `distance_mi`, `duration_sec`, `steps`, optional `max_pace`, `workout_date`.
**Derived:**
- `steps_per_min = steps / (duration_sec/60)` (guard against divide‑by‑zero).
- `speed_mph = distance_mi / (duration_sec/3600)`.
- `zpace = (avg_pace - median_past_90d) / mad` for personal normalization.
- **Context:** hour of day (sin/cos), day of week (one‑hot), pre/post event flags (e.g., “Choco”).

**Validation gates (drop or flag):**
- `duration_sec >= 180`, `0.1 <= distance_mi <= 200`, `3 <= avg_pace <= 30`.
- Null handling: if `steps` missing, still compute pace‑based features.

---

## 3) Algorithms
### 3.1 Baseline: Rule‑based
Simple, transparent thresholds (pace or speed). Pros: instant; Cons: brittle to outliers.

### 3.2 Probabilistic: Gaussian Mixture Model
- Fit 3‑component GMM on standardized features (pace, speed, steps/min).
- Get **posterior probabilities** → class = argmax; confidence = max prob.
- “Hybrid” if `max_prob` within **ambiguous band** (e.g., 0.4–0.6).
- Strength: overlaps handled gracefully; Limitation: component shape is elliptical.

### 3.3 Tree Ensemble: Random Forest
- Robust to non‑linearities & interactions.
- Provides **feature importance** and neighbors (leaf indices) for explanation.
- Calibrate probabilities with **isotonic** or **Platt** on a validation split.

### 3.4 Margin‑based: SVM (RBF)
- Excellent separators; must **calibrate** decision function to probabilities.
- Use class weighting if labels are imbalanced (when you add partial labels).

### 3.5 Ensemble (Recommended Default)
- Weighted average of calibrated probabilities from (GMM, RF, SVM) plus rule vote.
- Learn weights from CV or set heuristic (e.g., RF 0.4, GMM 0.3, SVM 0.2, Rules 0.1).
- Confidence = max ensemble prob; **Hybrid** band configurable (default 0.45–0.55).

**Note on labels:** Start **weakly‑supervised**: auto‑label clear cases (pace < 10 → Run; > 20 → Walk), leave the rest unlabeled for evaluation by **agreement** and user spot‑checks.

---

## 4) Explainability (XAI)
- **Global:** feature importances (RF permutation), distribution plots by class.
- **Local:** show the **top contributing features**; distance‑to‑threshold; nearest prototypes from each class (by Mahalanobis or standardized Euclidean).
- **Reliability:** plot predicted probability vs empirical frequency (**reliability diagram**), report **Brier** and **Expected Calibration Error (ECE)**.
- **Hybrid rationale:** probability mass split & conflict among models.

---

## 5) Storage & Versioning
### 5.1 Minimal (V0)
- Keep an in‑memory cache and write a CSV export (`classifications_{datetime}.csv`) for inspection.

### 5.2 Robust (V1) — Two Tables
```sql
CREATE TABLE classification_runs (
  run_id CHAR(36) PRIMARY KEY,
  algorithm VARCHAR(64) NOT NULL,
  version VARCHAR(32) NOT NULL,         -- e.g., "rf-0.1.0"
  params JSON NOT NULL,                  -- hyperparameters & thresholds
  data_snapshot VARCHAR(64),             -- e.g., "sweat.workout_summary@YYYY-MM-DD"
  code_sha CHAR(40),                     -- git commit
  ran_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workout_classifications (
  workout_id VARCHAR(20) NOT NULL,
  run_id CHAR(36) NOT NULL,
  predicted_type VARCHAR(20) NOT NULL,   -- Run | Walk | Hybrid
  confidence DECIMAL(4,3) NOT NULL,      -- 0.000–1.000
  features_used JSON,                    -- persisted features
  explanations JSON,                     -- top contributions / notes
  classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (workout_id, run_id),
  FOREIGN KEY (workout_id) REFERENCES workout_summary(workout_id),
  FOREIGN KEY (run_id) REFERENCES classification_runs(run_id)
);
```
**Why not mutate `workout_summary`?** We want **multiple runs** per workout, audit trails, and A/B comparisons without overwriting history.

---

## 6) UI/UX Spec (Streamlit)
### 6.1 Controls
- Algorithm selector (Rules, GMM, RF, SVM, Ensemble).
- Parameter group (e.g., #trees, C/gamma, n_components).
- **Confidence threshold** & **Hybrid band** sliders.
- Toggle calibration & feature standardization.

### 6.2 Panels
- **Summary:** class histogram, **reliability curve**, mean confidence, count in Hybrid.
- **Leaderboard:** top N **most uncertain** workouts (good labeling targets).
- **Drill‑down:** row details with features, explanation bullets, neighbor examples.
- **What‑if:** sliders for pace/duration to see class boundary shifts.

### 6.3 Exports
- “Save run to DB” → writes to `classification_runs` + `workout_classifications` with `code_sha`, `params` JSON, and `data_snapshot` tag.

---

## 7) Evaluation Plan
- **Weak labels:** clear pace thresholds for initial ground truth; evaluate on that subset.
- **Metrics:** balanced accuracy on labeled subset; **Brier** and **ECE** overall; macro‑F1 optional.
- **Stress tests:** extreme short/long durations; missing steps; outlier pace.
- **Temporal slices:** pre/post event (e.g., dog adoption), weekday vs weekend.

---

## 8) Testing & Quality Gates
- **Unit:** rule thresholds; feature builders; calibration math; Hybrid band logic.
- **Property‑based:** monotonicity (faster pace should not increase Walk probability).
- **Integration:** end‑to‑end run persists and reloads; reproducible with fixed seed.
- **UI tests:** algorithm switch doesn’t crash; exported CSV/DB row counts match.
- **Performance:** classify 10k rows under N seconds; cache hits validated.

---

## 9) Implementation Roadmap (2–3 focused sprints)
**Sprint 1 — Baseline to Demo**
- Rule‑based + GMM; feature builder; Hybrid band; UI controls; CSV export.
- Reliability chart; uncertain leaderboard.

**Sprint 2 — Robustness**
- RF + calibration + ensemble; DB schema + persistence; run metadata (code SHA).

**Sprint 3 — Shine**
- What‑if sandbox; neighbor prototypes; A/B compare between runs; labeling assist panel.

---

## 10) “Build Prompt” for a Coding Assistant
> **Role:** Senior Python engineer working on a Streamlit app with MySQL.  
> **Task:** Implement a toggleable Run/Walk/Hybrid classifier with confidence, explanations, and DB‑persisted runs.
>
> **Deliverables:**
> 1. `features.py`: build validated features (pace, speed_mph, steps_per_min, context) with guards.
> 2. `classifiers/`: `rules.py`, `gmm.py`, `rf.py`, `svm.py`, `ensemble.py`—each exposes `predict_proba(df)` returning calibrated class probabilities with a fixed class order `[Run, Walk, Hybrid]`.
> 3. `calibration.py`: isotonic/Platt wrappers with fit/transform.
> 4. `persistence.py`: create tables if missing; write/read `classification_runs` & `workout_classifications`.
> 5. `ui_classify.py`: Streamlit pane with algorithm selector, params, Hybrid band slider, reliability chart, uncertain leaderboard, row drill‑down and “Save run”. 
> 6. `tests/`: unit tests for features & rules; integration test that fits GMM on a tiny fixture and persists a run; golden seed reproducibility.
>
> **Acceptance Criteria:**
> - Switching algorithms updates predictions without app restart.
> - Each prediction has `predicted_type`, `confidence`, and `explanations` (dict of top features/notes).
> - Reliability diagram + Brier/ECE computed and rendered.
> - “Save run” writes one row to `classification_runs` and N rows to `workout_classifications`.
> - Code has type hints, docstrings, and passes tests with `pytest -q`.

---

## 11) Code Sketches
### 11.1 Interface
```python
from dataclasses import dataclass
from typing import Dict, Any, List
import pandas as pd

CLASSES = ["Run", "Walk", "Hybrid"]

@dataclass(frozen=True)
class Prediction:
    predicted_type: str
    confidence: float
    explanations: Dict[str, float]

class BaseClassifier:
    def predict_proba(self, X: pd.DataFrame) -> pd.DataFrame: ...
    def explain(self, X: pd.DataFrame, proba: pd.DataFrame) -> List[Dict[str, Any]]: ...
```

### 11.2 Hybrid Band
```python
import numpy as np
CLASSES = ["Run", "Walk", "Hybrid"]
def to_label(probs, hybrid_low=0.45, hybrid_high=0.55):
    # probs: array-like probabilities in CLASSES order
    k = int(np.argmax(probs))
    p = float(probs[k])
    if hybrid_low <= p <= hybrid_high:
        return "Hybrid", p
    return (CLASSES[k], p)
```

### 11.3 DB Persistence
```python
def save_run(conn, algorithm, version, params, code_sha, data_snapshot, preds_df):
    run_id = new_uuid()
    insert_run(conn, run_id, algorithm, version, params, data_snapshot, code_sha)
    bulk_insert_predictions(conn, run_id, preds_df)  # workout_id, predicted_type, confidence, features, explanations
    return run_id
```

---

## 12) Risks & Mitigations
- **Ambiguity:** Embrace via Hybrid; show uncertainty transparently.
- **Calibration drift:** Re‑calibrate per cohort or time window.
- **Data quality:** validation gates + dashboards for nulls/outliers.
- **Overfitting:** keep features lean; prefer cross‑validated weights.

---

## 13) Next Steps
1. Implement **Sprint 1** items with a tiny fixture dataset and golden seed.
2. Wire DB V1 tables and “Save run” button.
3. Add calibration & ensemble; ship reliability chart.
