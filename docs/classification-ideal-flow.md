# Diagram 2: Ideal Classification Flow (Fixed)

## How Classification Should Work - Accurate 10 min/mi → "Run"

```mermaid
flowchart TB
    Start([Workout Data:<br/>9/24/25, 30min<br/>10 min/mi, 3 miles]) --> LoadData

    LoadData[intelligence_service.py:63-105<br/>_load_workout_data] --> Delegate

    Delegate[Delegates to:<br/>model_manager.classify_workouts] --> CheckModel

    CheckModel{Is trained<br/>model available?} -->|Yes| PrepFeatures
    CheckModel -->|No| EraFallback1[Era-based Classification<br/>Post-2018 → pup_walk]

    PrepFeatures[model_manager.py:548-556<br/>Extract features:<br/>pace=10.0, dist=3.0, dur=30.0] --> Filter

    Filter[Apply filters:<br/>✓ pace valid<br/>✓ distance valid<br/>✓ duration valid] --> Scale

    Scale[StandardScaler.transform<br/>Normalize to trained space] --> KMeans

    KMeans[K-means Prediction<br/>Returns integer: 1] --> FixedMap

    FixedMap[✅ FIXED: model_manager.py:577<br/>Convert int to str for lookup:<br/>str\(cluster\) or use int keys]

    style FixedMap fill:#d4edda,stroke:#28a745,stroke-width:3px

    FixedMap --> LookupSuccess{Cluster found<br/>in map?}

    LookupSuccess -->|Yes| AssignActivity[predicted_activity_type = 'real_run'<br/>confidence = 0.819<br/>method = 'ml_trained']

    LookupSuccess -->|No| EraFallback2[Fallback to era-based<br/>only for truly unknown]

    AssignActivity --> CalculateConfidence[Calculate distance-based confidence:<br/>Closer to center = higher confidence]

    CalculateConfidence --> ValidateResult{Classification<br/>makes sense?}

    ValidateResult -->|Yes| StoreResult[Store in DataFrame:<br/>- predicted_activity_type<br/>- classification_confidence<br/>- classification_method]

    ValidateResult -->|No, low confidence| ConsiderOverride[Optional: Apply rule-based override<br/>for edge cases]

    StoreResult --> Display
    ConsiderOverride --> Display

    Display[intelligence.py:293-300<br/>Display Mapping:<br/>'real_run' → 'Run'] --> UI

    UI([✅ UI Shows: 'Run'<br/>CORRECT!])

    style UI fill:#d4edda,stroke:#28a745,stroke-width:2px
    style Start fill:#e3f2fd,stroke:#1976d2
    style AssignActivity fill:#d4edda,stroke:#28a745

    %% Add feature boxes
    Features[/"📊 K-means Features:<br/>1. avg_pace: 10.0 → -1.16 \(scaled\)<br/>2. distance_mi: 3.0 → -0.02 \(scaled\)<br/>3. duration_min: 30.0 → -0.78 \(scaled\)"/]

    Clusters[/"🎯 Cluster Centers:<br/>Cluster 0 \(pup_walk\): 23.07 min/mi<br/>Cluster 1 \(real_run\): 9.58 min/mi ← CLOSEST<br/>Cluster 2 \(mixed\): 11.69 min/mi"/]

    Confidence[/"📈 Confidence Calculation:<br/>Distance to Cluster 0: 1.876<br/>Distance to Cluster 1: 0.809 ← MIN<br/>Distance to Cluster 2: 4.471<br/>Confidence = 1 - \(0.809/4.471\) = 81.9%"/]

    Scale -.->|"Feature transformation"| Features
    KMeans -.->|"Cluster assignment"| Clusters
    CalculateConfidence -.->|"How confidence works"| Confidence

    style Features fill:#e3f2fd,stroke:#1976d2
    style Clusters fill:#fff3cd,stroke:#856404
    style Confidence fill:#d4edda,stroke:#28a745
```

## The Fix

### Option 1: Convert int to string (Simple)
**Location:** `src/ml/model_manager.py:577`

```python
# BEFORE (buggy):
activity_type = self.current_model.cluster_to_activity_map.get(cluster, 'unknown')

# AFTER (fixed):
activity_type = self.current_model.cluster_to_activity_map.get(str(cluster), 'unknown')
```

### Option 2: Use integer keys (Better long-term)
**Location:** `src/ml/model_manager.py:102` and `model_manager.py:436-443`

```python
# When loading from JSON (line 102):
self.cluster_to_activity_map = {
    int(k): v for k, v in data.get('cluster_to_activity_map', {}).items()
}

# When creating mapping during training (line 436-443):
for idx, (_, row) in enumerate(centers_sorted.iterrows()):
    cluster_id = int(row['cluster_id'])  # Already correct
    if idx == 0:
        model.cluster_to_activity_map[cluster_id] = 'real_run'  # Use int key
    elif idx == 1:
        model.cluster_to_activity_map[cluster_id] = 'mixed'
    else:
        model.cluster_to_activity_map[cluster_id] = 'pup_walk'
```

## How The System Works (When Fixed)

### 1. Training Phase
- Load **2,554 historical workouts** (2011-2025)
- Extract 3 features: pace, distance, duration
- Normalize using StandardScaler (fit on training data)
- K-means clusters into 3 groups
- Sort clusters by pace → assign activity labels
- **Save model with integer cluster keys**

### 2. Classification Phase
- Load new workout data
- Extract same 3 features
- Normalize using saved scaler (transform only)
- K-means predicts cluster using saved centers
- **Look up cluster ID (as int or convert to str)**
- Return activity type with confidence

### 3. Confidence Scoring
```
confidence = 1 - (distance_to_assigned_cluster / max_distance_to_any_cluster)
```
- Distance to Cluster 1 (real_run): 0.809
- Max distance (to Cluster 2): 4.471
- Confidence = 1 - (0.809/4.471) = **81.9%**

### 4. Fallback Logic (Only When Needed)
- **ML classification succeeds** → use it (preferred)
- **ML fails or data invalid** → use era-based fallback
  - Pre-2018: default to "real_run"
  - Post-2018: default to "pup_walk"
- **Confidence scoring helps identify** when to trust ML vs. fallback

## Expected Results After Fix

### Test Case: 9/24/25 Workout
```
Input:
  Date: 09/24/25
  Pace: 10.0 min/mi
  Distance: 3.0 miles
  Duration: 30 minutes

Processing:
  ✅ Features extracted: [10.0, 3.0, 30.0]
  ✅ Scaled: [-1.16, -0.02, -0.78]
  ✅ K-means predicts: Cluster 1
  ✅ Cluster lookup: 1 → "real_run" (SUCCESS)
  ✅ Confidence: 81.9%
  ✅ Method: "ml_trained"

Output:
  predicted_activity_type: real_run
  classification_confidence: 0.819
  classification_method: ml_trained

Display:
  ML Classification: Run ✅
```

### All Sept 2025 Workouts
After fix, **35 workouts** will be reclassified:
- Workouts with 9-11 min/mi → "Run" (currently misclassified as "Walk")
- Workouts with 20+ min/mi → "Walk" (correct, but via ML not era_fallback)
- Mixed pace workouts → "Mixed" (more nuanced classification)

### Classification Distribution (Expected)
```
Current (broken):
  pup_walk: 35 (100%)    ← All via era_fallback ❌

After fix (expected):
  pup_walk: ~25 (71%)    ← Via ML classification ✅
  real_run: ~8 (23%)     ← Via ML classification ✅
  mixed: ~2 (6%)         ← Via ML classification ✅
```

## Benefits of Fixed System

1. **Accuracy**: Uses trained ML model instead of simple date-based rules
2. **Confidence**: Provides numeric confidence scores (0-100%)
3. **Transparency**: Classification method tracked ("ml_trained" vs "era_fallback")
4. **Nuance**: Can detect "mixed" activities, not just runs or walks
5. **Learning**: Model improves as more training data added
6. **Validation**: Easy to audit why workouts classified certain ways

## Algorithm Flow Summary

```
Raw Workout Data
    ↓
Feature Extraction (pace, distance, duration)
    ↓
Normalization (StandardScaler)
    ↓
K-means Clustering (predict cluster)
    ↓
✅ Cluster → Activity Mapping (WITH TYPE CONVERSION)
    ↓
Confidence Calculation (distance-based)
    ↓
Result Validation
    ↓
Display Mapping (real_run → "Run")
    ↓
User Interface
```

## Testing the Fix

### Test Script
```python
# After applying fix, run:
python scripts/check_recent_classifications.py

# Expected output for 9/24/25 workout:
# 09/24/25     30m        3.0mi      10.0       329        real_run        81.9%        ml_trained
#                                                          ^^^^^^^^        ^^^^^        ^^^^^^^^^^
#                                                          CORRECT!        HIGH         USING ML!
```