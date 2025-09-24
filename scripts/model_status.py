#!/usr/bin/env python3
"""
Model Status Check Script

Quick script to check the current status of the ML classification model.

Usage:
    python scripts/model_status.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from ml.model_manager import model_manager
import json

def main():
    """Check and display model status."""
    print("🔍 Fitness Dashboard Model Status")
    print("=" * 40)

    model_stats = model_manager.get_model_stats()

    if not model_stats['model_available']:
        print("❌ No trained model available")
        print("💡 Run 'python scripts/train_model.py' to train a new model")
        return

    model_summary = model_stats['model_summary']
    activity_stats = model_stats['activity_type_stats']
    performance = model_stats['performance_metrics']
    training_info = model_stats['training_data_info']

    print("✅ Model Available")
    print(f"Model ID: {model_summary['model_id']}")
    print(f"Version: {model_summary['version']}")
    print(f"Status: {model_summary['status']}")

    print(f"\n📅 Training Information:")
    print(f"   • Trained: {model_summary['trained_at']}")
    print(f"   • Training workouts: {model_summary['training_workouts']:,}")
    print(f"   • Training period: {model_summary['training_period']}")

    print(f"\n⚡ Performance Metrics:")
    print(f"   • Quality rating: {model_summary['quality_rating']}")
    print(f"   • Silhouette score: {model_summary['silhouette_score']}")
    print(f"   • Clusters: {model_summary['clusters']}")

    print(f"\n🎯 Activity Types:")
    for activity_type in model_summary['activity_types']:
        if activity_type in activity_stats:
            stats = activity_stats[activity_type]
            print(f"   • {activity_type.replace('_', ' ').title()}: {stats['count']} workouts")
            print(f"     - Avg pace: {stats['avg_pace']:.1f} min/mile")
            print(f"     - Avg distance: {stats['avg_distance']:.1f} miles")

    print(f"\n🔧 Classification Mapping:")
    for cluster, activity in model_summary['classification_mapping'].items():
        print(f"   • {cluster} → {activity}")

    # Check model files
    files_status = model_stats['model_files_exist']
    print(f"\n📁 Model Files:")
    print(f"   • Metadata file: {'✅' if files_status['metadata_file'] else '❌'}")
    print(f"   • ML model file: {'✅' if files_status['sklearn_file'] else '❌'}")
    print(f"   • Models directory: {'✅' if files_status['models_directory'] else '❌'}")

if __name__ == "__main__":
    main()