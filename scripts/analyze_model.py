"""
Script to analyze the trained K-means model and investigate workout misclassification.

This script loads the trained model and analyzes why a specific workout
(9/24/25: 30min, 10 min/mi pace, ~3mi) is being misclassified as "Walk".
"""

import sys
import os
import pickle
import json
import numpy as np
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from ml.model_manager import model_manager
from sklearn.preprocessing import StandardScaler

def load_model():
    """Load the active trained model."""
    models_dir = Path("models")
    active_model_path = models_dir / "active" / "current_model"
    metadata_path = active_model_path.with_suffix('.json')
    sklearn_path = active_model_path.with_suffix('.pkl')

    if not (metadata_path.exists() and sklearn_path.exists()):
        print("❌ No trained model found!")
        return None, None

    # Load metadata
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    # Load sklearn objects
    with open(sklearn_path, 'rb') as f:
        sklearn_objects = pickle.load(f)

    return metadata, sklearn_objects

def analyze_cluster_centers(metadata, sklearn_objects):
    """Analyze the cluster centers and their activity mappings."""
    print("\n" + "="*80)
    print("CLUSTER CENTER ANALYSIS")
    print("="*80)

    kmeans = sklearn_objects['kmeans']
    scaler = sklearn_objects['scaler']
    cluster_map = metadata['cluster_to_activity_map']

    # Get cluster centers in original scale
    centers_scaled = kmeans.cluster_centers_
    centers_original = scaler.inverse_transform(centers_scaled)

    feature_names = metadata['feature_columns']

    print(f"\nNumber of clusters: {len(centers_original)}")
    print(f"Features used: {feature_names}")
    print(f"\nCluster-to-Activity Mapping:")
    for cluster_id, activity in cluster_map.items():
        print(f"  Cluster {cluster_id} → {activity}")

    print(f"\n{'Cluster':<10} {'Activity':<15} {'Avg Pace':<12} {'Distance':<12} {'Duration':<12}")
    print("-" * 80)

    for i, center in enumerate(centers_original):
        activity = cluster_map.get(str(i), 'unknown')
        pace, distance, duration = center
        print(f"{i:<10} {activity:<15} {pace:<12.2f} {distance:<12.2f} {duration:<12.2f}")

    return centers_original, feature_names, cluster_map, kmeans, scaler

def simulate_workout_classification(kmeans, scaler, feature_names, cluster_map):
    """Simulate classification of the problematic workout."""
    print("\n" + "="*80)
    print("WORKOUT CLASSIFICATION SIMULATION")
    print("="*80)

    # The problematic workout: 30 min, 10 min/mi pace, ~3 miles
    workout_data = {
        'avg_pace': 10.0,      # 10 min/mi (should indicate running)
        'distance_mi': 3.0,     # 3 miles (30 min / 10 min/mi)
        'duration_min': 30.0    # 30 minutes
    }

    print(f"\n📊 Workout to Classify:")
    print(f"   Pace: {workout_data['avg_pace']} min/mi")
    print(f"   Distance: {workout_data['distance_mi']} miles")
    print(f"   Duration: {workout_data['duration_min']} minutes")
    print(f"\n   👉 Expected: 'real_run' (10 min/mi is running pace)")

    # Prepare features
    features = np.array([[workout_data['avg_pace'], workout_data['distance_mi'], workout_data['duration_min']]])

    # Scale features
    features_scaled = scaler.transform(features)

    # Predict cluster
    predicted_cluster = kmeans.predict(features_scaled)[0]
    predicted_activity = cluster_map.get(str(predicted_cluster), 'unknown')

    # Calculate distances to all cluster centers
    distances = kmeans.transform(features_scaled)[0]

    print(f"\n🔍 Classification Results:")
    print(f"   Predicted Cluster: {predicted_cluster}")
    print(f"   Predicted Activity: {predicted_activity}")

    # Calculate confidence
    min_distance = np.min(distances)
    max_distance = np.max(distances)
    confidence = 1.0 - (min_distance / max_distance) if max_distance > 0 else 1.0

    print(f"   Confidence: {confidence:.2%}")

    print(f"\n📏 Distance to Each Cluster Center:")
    for i, dist in enumerate(distances):
        activity = cluster_map.get(str(i), 'unknown')
        closest = " ← CLOSEST" if i == predicted_cluster else ""
        print(f"   Cluster {i} ({activity}): {dist:.4f}{closest}")

    # Show feature values after scaling
    print(f"\n🔢 Scaled Feature Values:")
    for i, feature_name in enumerate(feature_names):
        print(f"   {feature_name}: {features_scaled[0][i]:.4f}")

    return predicted_cluster, predicted_activity, confidence, distances

def analyze_why_misclassified(centers_original, workout_data, feature_names):
    """Analyze why the workout is misclassified."""
    print("\n" + "="*80)
    print("MISCLASSIFICATION ANALYSIS")
    print("="*80)

    print("\n🔍 Why is 10 min/mi classified as Walk instead of Run?")

    workout_features = np.array([workout_data['avg_pace'], workout_data['distance_mi'], workout_data['duration_min']])

    print(f"\n1️⃣ Feature Space Position:")
    print(f"   Workout: pace={workout_data['avg_pace']}, distance={workout_data['distance_mi']}, duration={workout_data['duration_min']}")

    print(f"\n2️⃣ Comparison to Cluster Centers:")
    for i, center in enumerate(centers_original):
        # Calculate Euclidean distance
        euclidean_dist = np.sqrt(np.sum((workout_features - center) ** 2))

        print(f"\n   Cluster {i}:")
        print(f"      Center: pace={center[0]:.2f}, distance={center[1]:.2f}, duration={center[2]:.2f}")
        print(f"      Euclidean Distance: {euclidean_dist:.4f}")

        # Show per-feature differences
        for j, feature_name in enumerate(feature_names):
            diff = workout_features[j] - center[j]
            print(f"      {feature_name} diff: {diff:+.2f}")

    print(f"\n3️⃣ Key Insight:")
    print(f"   - The 10 min/mi pace SHOULD indicate running")
    print(f"   - BUT the 30-minute duration and 3-mile distance")
    print(f"     may be more similar to longer walks in the training data")
    print(f"   - K-means uses ALL 3 features equally (no pace priority)")
    print(f"   - This creates counter-intuitive classifications")

def main():
    """Main analysis function."""
    print("\n🔬 Workout Misclassification Analysis")
    print("="*80)

    # Load model
    metadata, sklearn_objects = load_model()

    if metadata is None:
        print("\n⚠️  No trained model found. Please train a model first:")
        print("   python scripts/train_model.py")
        return

    # Analyze cluster centers
    centers_original, feature_names, cluster_map, kmeans, scaler = analyze_cluster_centers(metadata, sklearn_objects)

    # Simulate problematic workout classification
    predicted_cluster, predicted_activity, confidence, distances = simulate_workout_classification(
        kmeans, scaler, feature_names, cluster_map
    )

    # Analyze why misclassified
    workout_data = {
        'avg_pace': 10.0,
        'distance_mi': 3.0,
        'duration_min': 30.0
    }
    analyze_why_misclassified(centers_original, workout_data, feature_names)

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\n✅ Model Analysis Complete!")
    print(f"\n📊 Model Info:")
    print(f"   - Training workouts: {metadata['training_data_info']['total_workouts']}")
    print(f"   - Training period: {metadata['training_data_info']['date_range']['start_date']} to {metadata['training_data_info']['date_range']['end_date']}")
    print(f"   - Silhouette score: {metadata['performance_metrics']['silhouette_score']:.3f}")

    print(f"\n❌ Misclassification Identified:")
    print(f"   - Workout: 30 min @ 10 min/mi pace")
    print(f"   - Predicted: {predicted_activity} (Cluster {predicted_cluster})")
    print(f"   - Expected: real_run")
    print(f"   - Confidence: {confidence:.2%}")

    print(f"\n💡 Root Cause:")
    print(f"   - K-means treats all features equally")
    print(f"   - Duration + distance combination pulls workout toward walk clusters")
    print(f"   - Pace alone (10 min/mi) is insufficient to override")
    print(f"   - Training data may have created walk-biased cluster centers")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()