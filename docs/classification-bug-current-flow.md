# Diagram 1: Current Classification Flow (With Bug)

## The Misclassification Pipeline - Why 10 min/mi Shows as "Walk"

```mermaid
flowchart TB
    Start([Workout Data:<br/>9/24/25, 30min<br/>10 min/mi, 3 miles]) --> LoadData

    LoadData[intelligence_service.py:63-105<br/>_load_workout_data] --> Delegate

    Delegate[Delegates to:<br/>model_manager.classify_workouts] --> CheckModel

    CheckModel{Is trained<br/>model available?} -->|Yes| PrepFeatures
    CheckModel -->|No| EraFallback1[Era-based Classification<br/>Post-2018 → pup_walk]

    PrepFeatures[model_manager.py:548-556<br/>Extract features:<br/>pace=10.0, dist=3.0, dur=30.0] --> Filter

    Filter[Apply filters:<br/>pace ✓, distance ✓, duration ✓] --> Scale

    Scale[StandardScaler.transform<br/>Scale to normalized space] --> KMeans

    KMeans[K-means Prediction<br/>Returns integer: 1] --> MapCluster

    MapCluster[model_manager.py:577<br/>cluster_to_activity_map.get] --> BUG

    BUG{{🐛 TYPE MISMATCH BUG<br/>Map has string keys: '1', '2', '0'<br/>Cluster is integer: 1<br/>Lookup fails → returns 'unknown'}}

    style BUG fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px,color:#fff

    BUG --> Unknown[predicted_activity_type = 'unknown'<br/>classification_method = 'error']

    Unknown --> CheckUnclassified{Are there<br/>unclassified<br/>workouts?}

    CheckUnclassified -->|Yes| EraFallback2[model_manager.py:585-587<br/>_apply_era_based_fallback]

    EraFallback2 --> CheckDate{workout_date <<br/>2018-06-01?}

    CheckDate -->|No| PostChoco[Post-Choco Era:<br/>predicted_activity_type = 'pup_walk'<br/>confidence = 0.4<br/>method = 'era_fallback']

    CheckDate -->|Yes| PreChoco[Pre-Choco Era:<br/>predicted_activity_type = 'real_run'<br/>confidence = 0.4<br/>method = 'era_fallback']

    PostChoco --> Display
    PreChoco --> Display

    Display[intelligence.py:293-300<br/>Display Mapping:<br/>'pup_walk' → 'Walk'] --> UI

    UI([UI Shows: 'Walk'<br/>❌ INCORRECT!<br/>Should show: 'Run'])

    style UI fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    style Start fill:#e3f2fd,stroke:#1976d2
    style PostChoco fill:#fff3cd,stroke:#856404

    %% Add note boxes
    Note1[/"💡 What Should Happen:<br/>K-means correctly predicts cluster 1<br/>Cluster 1 → 'real_run'<br/>Confidence: 81.9%"/]
    Note2[/"🔍 Root Cause:<br/>JSON serialization converts<br/>dict keys to strings<br/>Python int ≠ JSON string"/]

    KMeans -.->|"Correct prediction"| Note1
    BUG -.->|"Bug explanation"| Note2

    style Note1 fill:#d4edda,stroke:#28a745
    style Note2 fill:#fff3cd,stroke:#ffc107
```

## Key Points

### The Bug Location
**File:** `src/ml/model_manager.py:577`
**Line:** `activity_type = self.current_model.cluster_to_activity_map.get(cluster, 'unknown')`

### Why It Fails
1. **Training Phase** (`model_manager.py:436-443`): Cluster IDs stored as integers in Python dict
2. **Serialization** (`model_manager.py:246-256`): JSON.dump converts dict keys to strings: `{1: 'real_run'}` → `{"1": "real_run"}`
3. **Loading** (`model_manager.py:203-215`): Loaded back with string keys: `{"1": "real_run", "2": "mixed", "0": "pup_walk"}`
4. **Classification** (`model_manager.py:567-577`): K-means returns integer cluster ID: `1`
5. **Lookup Failure**: `dict.get(1, 'unknown')` with string keys returns `'unknown'`
6. **Fallback Triggered**: All workouts marked as 'unknown' → era_fallback → pup_walk (post-2018)

### Impact
- **ALL recent workouts** (Sept 2025) misclassified as "pup_walk"
- 10 min/mi workouts shown as "Walk" instead of "Run"
- ML model predictions completely ignored
- Users see inaccurate classifications despite trained model working correctly

### Cluster Centers (for reference)
```
Cluster 0 → pup_walk:  pace=23.07 min/mi, distance=2.00mi, duration=44.6min
Cluster 1 → real_run:  pace=9.58 min/mi,  distance=4.42mi, duration=41.5min
Cluster 2 → mixed:     pace=11.69 min/mi, distance=9.80mi, duration=103.6min
```

### Test Case Workout
```
Date: 09/24/25
Pace: 10.0 min/mi (running pace)
Distance: 3.0 miles
Duration: 30 minutes

Model Prediction: Cluster 1 (real_run) - 81.9% confidence ✅
Actual Display: "Walk" (pup_walk via era_fallback) ❌
```