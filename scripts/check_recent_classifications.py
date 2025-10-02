"""
Check recent workout classifications in the database to understand the discrepancy
between what the model predicts and what the UI displays.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
from services.database_service import DatabaseService
from services.intelligence_service import FitnessIntelligenceService
from datetime import datetime, timedelta

def main():
    print("\n🔍 Checking Recent Workout Classifications")
    print("="*80)

    # Initialize services
    db_service = DatabaseService()
    intel_service = FitnessIntelligenceService(db_service)

    # Load workout data with classifications
    print("\n1️⃣ Loading workout data through intelligence service...")
    df = intel_service._load_workout_data()

    if df.empty:
        print("❌ No workout data found!")
        return

    print(f"✅ Loaded {len(df)} total workouts")

    # Filter to recent workouts (last 30 days from most recent workout)
    most_recent = df['workout_date'].max()
    cutoff_date = most_recent - timedelta(days=30)
    recent_df = df[df['workout_date'] >= cutoff_date].copy()

    print(f"\n2️⃣ Filtering to last 30 days (from {most_recent.date()})...")
    print(f"   Cutoff date: {cutoff_date.date()}")
    print(f"   Recent workouts: {len(recent_df)}")

    # Sort by date (most recent first)
    recent_df = recent_df.sort_values('workout_date', ascending=False)

    print(f"\n3️⃣ Most Recent Workouts with Classifications:")
    print("="*80)

    # Display in table format
    print(f"\n{'Date':<12} {'Duration':<10} {'Distance':<10} {'Pace':<10} {'Calories':<10} {'Classification':<15} {'Confidence':<12} {'Method':<20}")
    print("-"*120)

    for idx, row in recent_df.head(20).iterrows():
        date_str = row['workout_date'].strftime('%m/%d/%y')
        duration_str = f"{int(row['duration_sec']//60)}m" if pd.notna(row['duration_sec']) else "N/A"
        distance_str = f"{row['distance_mi']:.1f}mi" if pd.notna(row['distance_mi']) else "N/A"
        pace_str = f"{row['avg_pace']:.1f}" if pd.notna(row['avg_pace']) else "N/A"
        calories_str = f"{int(row['kcal_burned'])}" if pd.notna(row['kcal_burned']) else "N/A"

        classification = row.get('predicted_activity_type', 'unknown')
        confidence = row.get('classification_confidence', 0.0)
        method = row.get('classification_method', 'unknown')

        confidence_str = f"{confidence:.1%}" if confidence > 0 else "N/A"

        print(f"{date_str:<12} {duration_str:<10} {distance_str:<10} {pace_str:<10} {calories_str:<10} {classification:<15} {confidence_str:<12} {method:<20}")

    # Check specifically for ~10 min/mi pace workouts in recent data
    print(f"\n4️⃣ Workouts with ~10 min/mi pace (9-11 min/mi):")
    print("="*80)

    pace_filter = (recent_df['avg_pace'] >= 9.0) & (recent_df['avg_pace'] <= 11.0)
    pace_10_workouts = recent_df[pace_filter]

    if len(pace_10_workouts) > 0:
        print(f"\nFound {len(pace_10_workouts)} workouts with pace between 9-11 min/mi:")
        print(f"\n{'Date':<12} {'Pace':<10} {'Distance':<10} {'Duration':<10} {'Classification':<15} {'Should Be':<15}")
        print("-"*80)

        for idx, row in pace_10_workouts.iterrows():
            date_str = row['workout_date'].strftime('%m/%d/%y')
            pace_str = f"{row['avg_pace']:.2f}"
            distance_str = f"{row['distance_mi']:.1f}mi"
            duration_str = f"{int(row['duration_sec']//60)}m"
            classification = row.get('predicted_activity_type', 'unknown')

            # Determine what it should be based on pace
            should_be = "real_run" if row['avg_pace'] < 12 else "pup_walk"

            # Highlight mismatches
            mismatch = " ❌ MISMATCH!" if classification != should_be else ""

            print(f"{date_str:<12} {pace_str:<10} {distance_str:<10} {duration_str:<10} {classification:<15} {should_be:<15}{mismatch}")
    else:
        print("No workouts found with 9-11 min/mi pace in recent data")

    # Classification distribution
    print(f"\n5️⃣ Classification Distribution (Recent 30 Days):")
    print("="*80)

    if 'predicted_activity_type' in recent_df.columns:
        counts = recent_df['predicted_activity_type'].value_counts()
        print(f"\nTotal: {len(recent_df)} workouts")
        for activity, count in counts.items():
            pct = (count / len(recent_df)) * 100
            print(f"   {activity}: {count} ({pct:.1f}%)")
    else:
        print("❌ No classification data available in DataFrame")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()