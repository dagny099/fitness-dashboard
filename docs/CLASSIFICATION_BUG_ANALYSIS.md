# Classification Bug Analysis Report

**Date:** September 29, 2025
**Investigator:** Claude Code
**Severity:** HIGH - All ML classifications failing, entire system using fallback logic

---

## Executive Summary

A critical bug in the workout classification system is causing **ALL recent workouts to be misclassified**. The K-means ML model correctly predicts activity types, but a **type mismatch** in the cluster lookup logic causes all predictions to fail silently and fall back to era-based classification.

### Impact
- ✅ K-means model: **Working correctly** (81.9% confidence on test case)
- ❌ Classification results: **100% wrong** (all using era_fallback)
- 🔴 User experience: **Misleading** (10 min/mi pace shown as "Walk")
- 📊 Recent data: **35/35 Sept 2025 workouts misclassified** (100% error rate)

---

## The Bug

### Location
**File:** `src/ml/model_manager.py`
**Line:** 577
**Function:** `classify_workouts()`

```python
# BUGGY CODE:
activity_type = self.current_model.cluster_to_activity_map.get(cluster, 'unknown')
#                                                               ^^^^^^^
#                                                               Integer from K-means
# But map has STRING keys: {'1': 'real_run', '2': 'mixed', '0': 'pup_walk'}
# Lookup returns 'unknown' → triggers era_fallback
```

### Root Cause
1. **Training Phase:** Cluster mapping created with integer keys in Python dict
2. **Serialization:** `json.dump()` converts all dict keys to strings (JSON requirement)
3. **Loading:** Model loaded back with string keys: `{"1": "real_run", ...}`
4. **Classification:** K-means returns integer cluster ID: `1`
5. **Lookup:** `dict.get(1, 'unknown')` fails because keys are strings
6. **Fallback:** All workouts marked 'unknown' → triggers era-based classification

### Why It Went Unnoticed
- Model **training** works perfectly
- Model **predictions** work correctly
- Classification **fails silently** (returns 'unknown', no exception)
- Era-based fallback **provides plausible results** (walks after 2018)
- No error messages in logs
- Tests likely didn't validate classification_method field

---

## Evidence

### Test Case: 9/24/25 Workout
```
Workout Details:
  Date: 09/24/25
  Pace: 10.0 min/mi (running pace)
  Distance: 3.0 miles
  Duration: 30 minutes

K-means Model Prediction:
  ✅ Cluster: 1 (real_run cluster)
  ✅ Confidence: 81.9%
  ✅ Distance to cluster center: 0.809 (very close)

Actual System Output:
  ❌ predicted_activity_type: pup_walk
  ❌ classification_confidence: 0.4 (40%)
  ❌ classification_method: era_fallback
  ❌ Display: "Walk"
```

### Cluster Centers (From Trained Model)
```
Cluster 0 (pup_walk):  pace=23.07 min/mi, distance=2.00mi, duration=44.63min
Cluster 1 (real_run):  pace=9.58 min/mi,  distance=4.42mi, duration=41.53min
Cluster 2 (mixed):     pace=11.69 min/mi, distance=9.80mi, duration=103.59min

Test workout (10.0 min/mi, 3.0mi, 30min) is CLOSEST to Cluster 1 ✅
```

### Classification Results (Sept 2025)
```
Total workouts: 35
Classification distribution:
  - pup_walk: 35 (100%)
  - real_run: 0 (0%)
  - mixed: 0 (0%)

Classification methods:
  - era_fallback: 35 (100%)    ← Everything using fallback!
  - ml_trained: 0 (0%)         ← ML never used!

Known running-pace workouts misclassified:
  - 09/24/25: 10.00 min/mi → classified as pup_walk ❌ (should be real_run)
  - 09/21/25: 9.57 min/mi  → classified as pup_walk ❌ (should be real_run)
```

---

## The Fix

### Option 1: Quick Fix (Recommended for immediate deployment)
Convert integer cluster to string at lookup:

**File:** `src/ml/model_manager.py:577`
```python
# Change this line:
activity_type = self.current_model.cluster_to_activity_map.get(cluster, 'unknown')

# To this:
activity_type = self.current_model.cluster_to_activity_map.get(str(cluster), 'unknown')
```

### Option 2: Proper Fix (Recommended for long-term)
Use integer keys throughout:

**File:** `src/ml/model_manager.py:102` (in `from_dict` method)
```python
# Add type conversion when loading from JSON:
self.cluster_to_activity_map = {
    int(k): v for k, v in data.get('cluster_to_activity_map', {}).items()
}
```

**Then retrain the model or convert existing models on load.**

### Option 3: Defensive Fix (Most robust)
Handle both types:

**File:** `src/ml/model_manager.py:577`
```python
# Support both int and str keys:
activity_type = (
    self.current_model.cluster_to_activity_map.get(cluster) or
    self.current_model.cluster_to_activity_map.get(str(cluster), 'unknown')
)
```

---

## Verification Steps

### 1. Apply the fix
Choose Option 1 or 2 above.

### 2. Test with analysis script
```bash
python scripts/analyze_model.py
```
Expected output:
```
Predicted Cluster: 1
Predicted Activity: real_run  ← Should NOT be empty/unknown
Confidence: 81.90%
```

### 3. Check recent classifications
```bash
python scripts/check_recent_classifications.py
```
Expected changes:
```
09/24/25     30m     3.0mi      10.0       329        real_run        81.9%        ml_trained
09/21/25     19m     2.0mi      9.6        217        real_run        85.2%        ml_trained
                                                      ^^^^^^^^        ^^^^^        ^^^^^^^^^^
                                                      FIXED!          HIGH         USING ML!
```

### 4. UI verification
Start the app and check intelligence dashboard:
```bash
STREAMLIT_DEV_MODE=true streamlit run src/streamlit_app.py
```
Navigate to Intelligence page and verify:
- Individual workouts table shows "Run" for 10 min/mi workouts
- Classification breakdown shows runs, walks, AND mixed (not 100% walks)
- Classification method shows "ml_trained" not "era_fallback"

---

## Expected Impact After Fix

### Classification Distribution (Sept 2025)
```
Before fix:
  pup_walk: 35 (100%)  ← All era_fallback
  real_run: 0 (0%)
  mixed: 0 (0%)

After fix (estimated):
  pup_walk: ~25 (71%)  ← ML classification
  real_run: ~8 (23%)   ← ML classification (includes 10 min/mi workouts)
  mixed: ~2 (6%)       ← ML classification
```

### Confidence Scores
```
Before: All 40% (low confidence fallback)
After: 60-90% (high confidence ML predictions)
```

### User Experience
- ✅ Running workouts (8-12 min/mi) correctly shown as "Run"
- ✅ Walking workouts (20+ min/mi) correctly shown as "Walk"
- ✅ Mixed activities properly identified
- ✅ High confidence scores for clear classifications
- ✅ Low confidence scores prompt user review (appropriate)

---

## Prevention & Testing Recommendations

### 1. Add Integration Tests
```python
def test_classification_with_real_model():
    """Test that ML classification actually works end-to-end"""
    # Load or train model
    model_manager.train_new_model()

    # Create test workout with running pace
    test_df = pd.DataFrame([{
        'avg_pace': 10.0,
        'distance_mi': 3.0,
        'duration_min': 30.0,
        'workout_date': datetime.now()
    }])

    # Classify
    result = model_manager.classify_workouts(test_df)

    # Assert ML classification was used
    assert result.iloc[0]['classification_method'] == 'ml_trained'
    assert result.iloc[0]['predicted_activity_type'] == 'real_run'
    assert result.iloc[0]['classification_confidence'] > 0.7
```

### 2. Add Validation Checks
**File:** `src/ml/model_manager.py:575-583`
```python
# After classification, add validation:
for i, idx in enumerate(clean_indices):
    cluster = predicted_clusters[i]
    activity_type = self.current_model.cluster_to_activity_map.get(str(cluster), 'unknown')

    # ADD THIS CHECK:
    if activity_type == 'unknown':
        logger.warning(f"Cluster {cluster} not found in mapping! Keys: {list(self.cluster_to_activity_map.keys())}")

    confidence = confidences[i]
    result_df.loc[idx, 'predicted_activity_type'] = activity_type
    result_df.loc[idx, 'classification_confidence'] = confidence
    result_df.loc[idx, 'classification_method'] = 'ml_trained' if activity_type != 'unknown' else 'ml_failed'
```

### 3. Add Monitoring Dashboard
Track classification methods over time:
```python
# Add to intelligence dashboard:
method_counts = df['classification_method'].value_counts()
st.metric("ML Success Rate", f"{method_counts.get('ml_trained', 0) / len(df) * 100:.1f}%")

if method_counts.get('era_fallback', 0) / len(df) > 0.5:
    st.warning("⚠️ More than 50% of workouts using fallback classification!")
```

### 4. Type Safety
Consider using TypedDict or dataclasses for cluster mappings:
```python
from typing import Dict, NewType

ClusterID = NewType('ClusterID', int)
ActivityType = NewType('ActivityType', str)

cluster_map: Dict[ClusterID, ActivityType] = {
    ClusterID(0): ActivityType('pup_walk'),
    ClusterID(1): ActivityType('real_run'),
    ClusterID(2): ActivityType('mixed')
}
```

---

## Related Files

### Analysis Scripts
- `scripts/analyze_model.py` - Model inspection and test case analysis
- `scripts/check_recent_classifications.py` - Database classification verification

### Documentation
- `docs/classification-bug-current-flow.md` - Diagram showing bug flow
- `docs/classification-ideal-flow.md` - Diagram showing correct flow

### Source Files
- `src/ml/model_manager.py:577` - Bug location (classification lookup)
- `src/ml/model_manager.py:102` - Alternative fix location (loading)
- `src/ml/model_manager.py:436-443` - Cluster mapping creation
- `src/services/intelligence_service.py:92-93` - Classification entry point

---

## Timeline

1. **Model Training:** Model trained successfully with 2,554 workouts, silhouette score 0.484
2. **Serialization:** Cluster mapping saved to JSON with string keys
3. **Classification Start:** All classifications begin failing silently
4. **Fallback Activation:** Era-based fallback handles 100% of recent workouts
5. **Bug Discovery:** Analysis of 9/24/25 workout reveals type mismatch
6. **Root Cause:** Integer-to-string key conversion identified

---

## Conclusion

This is a **critical but easily fixable bug**. The ML model works correctly; only the cluster lookup logic needs adjustment. The fix is simple (one line change), low-risk (defensive fallback still works), and has high impact (restores ML classification for all workouts).

**Recommended Action:** Apply Option 1 (quick fix) immediately, then implement Option 2 (proper fix) in next release with comprehensive testing.

**Priority:** HIGH - Affects core functionality and user trust in ML system

**Estimated Fix Time:** 5 minutes
**Estimated Testing Time:** 15 minutes
**Risk Level:** LOW (fallback still works if anything goes wrong)

---

## Appendix: Classification System Architecture

### Data Flow
```
Raw Workout → Feature Extraction → Scaling → K-means → Cluster Lookup → Activity Type
                                                            ↓
                                                        [BUG HERE]
                                                            ↓
                                                     Era Fallback
```

### Key Components
- **ModelManager:** Handles model lifecycle (train, save, load, classify)
- **WorkoutClassificationModel:** Encapsulates model, scaler, and cluster mapping
- **FitnessIntelligenceService:** Coordinates classification with other analytics
- **Era-based fallback:** Safety net when ML fails (working as designed)

### Design Intent
The era-based fallback is a **good design** - it ensures users never see "unknown" classifications. However, it should be used as a **last resort**, not as the primary classification method for all recent workouts.

The bug doesn't break the system (fallback works), but it completely negates the value of the trained ML model. Users see plausible but incorrect classifications, which is worse than seeing "unknown" with low confidence.