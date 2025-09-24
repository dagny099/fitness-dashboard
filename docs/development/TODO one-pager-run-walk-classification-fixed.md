# Run/Walk/Hybrid Classification — One-Pager (Fixed Mermaid)
**Date:** 2025-09-10 19:57  
**Goal:** Ship a user-friendly, *explainable* classifier for workouts with quick iteration, clear versioning, and crisp UI affordances.

---

## Conceptual Model
- **Task:** Assign each workout to **Run**, **Walk**, or **Hybrid** with **confidence** and **explanations**.
- **Reality Check:** Labels are fuzzy; “Hybrid” is a **first-class** outcome, not a failure case.
- **Interaction:** Users can **switch algorithms**, **tune parameters**, and **inspect evidence** (features & explanations).

```mermaid
flowchart LR
  A[Workout summary<br/>(avg_pace, distance_mi,<br/>duration_sec, steps, etc.)] --> B[Feature builder]

  subgraph Options
    direction TB
    C[Rules]
    D[GMM]
    E[Random Forest]
    F[SVM RBF]
    G[Ensemble]
  end

  B --> C
  B --> D
  B --> E
  B --> F
  B --> G

  C --> H{Decision}
  D --> H
  E --> H
  F --> H
  G --> H

  H --> I[Prediction: Run/Walk/Hybrid]
  H --> J[Confidence & Rationale]
  I --> K[(DB: classification tables)]
  J --> K

  classDef alg fill:#eef,stroke:#99f,stroke-width:1px;
  class C,D,E,F,G alg;
```

---

## Algorithms (pick at runtime)
1. **Rule-based (baseline):** pace thresholds.
2. **Gaussian Mixture (soft clusters):** overlaps → **probabilities**.
3. **Random Forest:** non-linearities + **feature importance**.
4. **SVM RBF:** strong boundaries; pair with **calibration**.
5. **Ensemble (recommended):** weighted blend with calibration.

**Confidence** = calibrated probability (or distance-to-boundary).  
**Hybrid** = probability near 0.5 (e.g., 0.4–0.6) or conflicting votes.

---

## Features
- **Primary:** avg_pace, steps_per_min, speed_mph.
- **Secondary:** max_pace, distance_mi / duration_sec, z-scores vs personal baseline.
- **Context:** time-of-day, day-of-week, “pre/post-Choco”, seasonality.
- **Quality Guards:** duration > 3 min, distance > 0.1 mi, pace ∈ [3, 30] min/mi.

---

## Storage (fast now, robust later)
- **V0 (quick):** in-memory cache + optional CSV export.
- **V1 (robust):** `workout_classifications` and `classification_runs` (versioned).

```mermaid
erDiagram
  workout_summary ||--o{ workout_classifications : "workout_id"
  classification_runs ||--o{ workout_classifications : "run_id"
  workout_summary {
    VARCHAR(20) workout_id PK
    DATETIME workout_date
    FLOAT distance_mi
    FLOAT duration_sec
    FLOAT avg_pace
    BIGINT steps
  }
  classification_runs {
    UUID run_id PK
    VARCHAR algorithm
    VARCHAR version
    JSON params
    TIMESTAMP ran_at
    VARCHAR data_snapshot
    VARCHAR code_sha
  }
  workout_classifications {
    VARCHAR(20) workout_id FK
    UUID run_id FK
    VARCHAR predicted_type
    DECIMAL(4,3) confidence
    JSON features_used
    JSON explanations
    TIMESTAMP classified_at
    PRIMARY KEY (workout_id, run_id)
  }
```
(If your Mermaid theme dislikes curly braces in `erDiagram`, switch to markdown table ER or PlantUML.)

---

## UI (Streamlit)
- **Left rail:** Algorithm selector, parameter sliders, **confidence threshold**, “Mark Hybrid range”.
- **Main:** Class distribution, **reliability curve**, top-K **most uncertain**.
- **Details:** Row-level panel with features, **rationale**, and “What-if” controls.
- **Export:** Save run → DB with `algorithm`, `params`, `code_sha`, `data_snapshot`.

---

## Evaluation & XAI
- **Metrics:** balanced accuracy (if labels exist), **Brier score**, **ECE** (calibration), coverage of Hybrid.
- **Explanations:** feature contributions, **prototype/neighbor** examples, threshold distance.
- **Diagnostics:** reliability diagram, cumulative gain by confidence, error breakdown across time-of-day and pace bands.

---

## Acceptance Criteria (V1)
- Switchable algorithms with default params.
- Confidence returned and displayed; **Hybrid** logic configurably tied to probability band.
- “Explain” button shows features & rationale.
- Persist a **classification run** with metadata & parameters.
- Unit tests for rules; integration tests that round-trip a run to DB; golden seed for determinism.
