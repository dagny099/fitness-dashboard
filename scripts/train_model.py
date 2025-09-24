#!/usr/bin/env python3
"""
Model Training Script for Fitness Classification

This script trains a new workout classification model on the full historical dataset.
It replaces the ad-hoc clustering approach with a proper ML pipeline that leverages
all available training data.

Usage:
    python scripts/train_model.py [--force] [--verbose]

Arguments:
    --force: Force retrain even if a model already exists
    --verbose: Show detailed training progress
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

import argparse
import logging
from ml.model_manager import model_manager
from services.intelligence_service import FitnessIntelligenceService

def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main training function."""
    parser = argparse.ArgumentParser(
        description='Train workout classification model on full historical dataset'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force retrain even if model exists'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed training progress'
    )

    args = parser.parse_args()

    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    print("🚀 Fitness Dashboard Model Training")
    print("=" * 50)

    # Check current model status
    model_stats = model_manager.get_model_stats()

    if model_stats['model_available'] and not args.force:
        current_model = model_stats['model_summary']
        print(f"✅ Model already exists:")
        print(f"   • Model ID: {current_model['model_id']}")
        print(f"   • Trained: {current_model['trained_at']}")
        print(f"   • Training workouts: {current_model['training_workouts']:,}")
        print(f"   • Quality: {current_model['quality_rating']}")
        print(f"\n💡 Use --force to retrain existing model")
        return

    # Train new model
    print("🔄 Training new model on full historical dataset...")

    training_result = model_manager.train_new_model(force_retrain=args.force)

    if training_result['success']:
        model_summary = training_result['model_summary']
        training_info = training_result['training_data_info']
        performance = training_result['performance_metrics']

        print("\n✅ Model Training Successful!")
        print("=" * 30)
        print(f"Model ID: {model_summary['model_id']}")
        print(f"Training Period: {training_info['date_range']['start_date']} to {training_info['date_range']['end_date']}")
        print(f"Training Workouts: {training_info['total_workouts']:,}")
        print(f"Training Span: {training_info['date_range']['span_days']} days")
        print(f"Silhouette Score: {performance['silhouette_score']:.3f}")
        print(f"Quality Rating: {model_summary['quality_rating']}")

        print(f"\n📊 Activity Distribution:")
        for activity_type, count in performance['cluster_distribution'].items():
            cluster_name = model_summary['classification_mapping'].get(f'Cluster {activity_type}', 'Unknown')
            print(f"   • {cluster_name}: {count} workouts")

        # Test classification with intelligence service
        print(f"\n🧪 Testing Integration...")
        intelligence_service = FitnessIntelligenceService()
        test_brief = intelligence_service.generate_daily_intelligence_brief(days_lookback=30)

        if 'error' not in test_brief:
            recent_workouts = test_brief['recent_workouts_analyzed']
            print(f"   • Successfully classified {recent_workouts} recent workouts")

            classification_data = test_brief.get('classification_intelligence', {})
            if 'summary' in classification_data:
                print(f"   • Recent classification distribution: {classification_data['summary']}")
        else:
            print(f"   ⚠️ Integration test failed: {test_brief['error']}")

        print(f"\n🎉 Model training complete and ready for use!")

    else:
        print(f"\n❌ Model Training Failed!")
        print(f"Error: {training_result['message']}")
        if 'error' in training_result:
            logger.error(f"Detailed error: {training_result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()