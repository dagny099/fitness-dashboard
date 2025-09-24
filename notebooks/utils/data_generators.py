"""
Data generation utilities for fitness classification demonstrations.

This module creates synthetic datasets optimized for educational demonstrations,
including clear-cut examples for learning and edge cases for testing understanding.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class FitnessDataGenerator:
    """Generate realistic fitness data for educational demonstrations."""
    
    def __init__(self, random_seed: int = 42):
        """Initialize with reproducible random seed."""
        self.random_seed = random_seed
        np.random.seed(random_seed)
        
    def generate_clear_examples(self, n_runs: int = 50, n_walks: int = 50) -> pd.DataFrame:
        """Generate clear-cut examples for algorithm training and demonstration."""
        
        # Clear running examples (6-11 min/mile)
        run_paces = np.random.normal(8.5, 1.2, n_runs)
        run_paces = np.clip(run_paces, 6, 11)
        run_distances = np.random.normal(4.2, 1.5, n_runs) 
        run_distances = np.clip(run_distances, 1.5, 8)
        run_durations = run_paces * run_distances * 60  # seconds
        
        # Clear walking examples (20-30 min/mile)
        walk_paces = np.random.normal(24, 3, n_walks)
        walk_paces = np.clip(walk_paces, 20, 30)
        walk_distances = np.random.normal(2.1, 0.8, n_walks)
        walk_distances = np.clip(walk_distances, 0.8, 4)
        walk_durations = walk_paces * walk_distances * 60  # seconds
        
        # Create date range
        start_date = datetime(2020, 1, 1)
        run_dates = [start_date + timedelta(days=i*3) for i in range(n_runs)]
        walk_dates = [start_date + timedelta(days=1) + timedelta(days=i*3) for i in range(n_walks)]
        
        # Combine data
        df = pd.DataFrame({
            'workout_date': run_dates + walk_dates,
            'activity_type': ['Run'] * n_runs + ['Walk'] * n_walks,
            'avg_pace': np.concatenate([run_paces, walk_paces]),
            'distance_mi': np.concatenate([run_distances, walk_distances]),
            'duration_sec': np.concatenate([run_durations, walk_durations]),
            'true_class': ['real_run'] * n_runs + ['choco_adventure'] * n_walks,
            'difficulty': ['easy'] * (n_runs + n_walks)
        })
        
        # Add some noise to make it realistic
        df['kcal_burned'] = df['distance_mi'] * 100 + np.random.normal(0, 15, len(df))
        df['kcal_burned'] = np.clip(df['kcal_burned'], 50, 800)
        
        return df.sample(frac=1).reset_index(drop=True)  # Shuffle
    
    def generate_ambiguous_examples(self, n_ambiguous: int = 30) -> pd.DataFrame:
        """Generate genuinely ambiguous workouts for testing edge cases."""
        
        ambiguous_examples = []
        
        # Type 1: Interval training (starts walking, includes running bursts)
        n_intervals = n_ambiguous // 3
        interval_paces = np.random.normal(14, 2, n_intervals)  # 12-16 min/mile avg
        interval_distances = np.random.normal(3.5, 1, n_intervals)
        interval_dates = [datetime(2021, 1, 1) + timedelta(days=i*4) for i in range(n_intervals)]
        
        for i in range(n_intervals):
            ambiguous_examples.append({
                'workout_date': interval_dates[i],
                'activity_type': 'Interval Run',
                'avg_pace': interval_paces[i],
                'distance_mi': interval_distances[i],
                'duration_sec': interval_paces[i] * interval_distances[i] * 60,
                'true_class': 'mixed',
                'difficulty': 'hard',
                'scenario': 'Warm-up walk + running intervals + cool-down'
            })
        
        # Type 2: Recovery runs (very slow running)
        n_recovery = n_ambiguous // 3
        recovery_paces = np.random.normal(13, 1.5, n_recovery)  # 11-15 min/mile
        recovery_distances = np.random.normal(2.8, 0.8, n_recovery)
        recovery_dates = [datetime(2021, 2, 1) + timedelta(days=i*4) for i in range(n_recovery)]
        
        for i in range(n_recovery):
            ambiguous_examples.append({
                'workout_date': recovery_dates[i],
                'activity_type': 'Easy Run',
                'avg_pace': recovery_paces[i], 
                'distance_mi': recovery_distances[i],
                'duration_sec': recovery_paces[i] * recovery_distances[i] * 60,
                'true_class': 'mixed',
                'difficulty': 'hard',
                'scenario': 'Post-injury recovery running at conservative pace'
            })
        
        # Type 3: Fast hiking/power walking
        n_fast_walks = n_ambiguous - n_intervals - n_recovery
        fast_walk_paces = np.random.normal(16, 2, n_fast_walks)  # 14-18 min/mile
        fast_walk_distances = np.random.normal(4.2, 1.2, n_fast_walks)
        fast_walk_dates = [datetime(2021, 3, 1) + timedelta(days=i*4) for i in range(n_fast_walks)]
        
        for i in range(n_fast_walks):
            ambiguous_examples.append({
                'workout_date': fast_walk_dates[i],
                'activity_type': 'Brisk Walk',
                'avg_pace': fast_walk_paces[i],
                'distance_mi': fast_walk_distances[i], 
                'duration_sec': fast_walk_paces[i] * fast_walk_distances[i] * 60,
                'true_class': 'mixed',
                'difficulty': 'hard',
                'scenario': 'Power walking uphill or with weighted pack'
            })
        
        # Convert to DataFrame
        df = pd.DataFrame(ambiguous_examples)
        
        # Add calories burned
        df['kcal_burned'] = df['distance_mi'] * 85 + np.random.normal(0, 20, len(df))
        df['kcal_burned'] = np.clip(df['kcal_burned'], 40, 600)
        
        return df
    
    def generate_outlier_examples(self, n_outliers: int = 10) -> pd.DataFrame:
        """Generate outlier cases that should be flagged for human review."""
        
        outlier_examples = []
        
        # Ultra-fast paces (measurement errors or sprints)
        n_fast = n_outliers // 2
        fast_paces = np.random.uniform(4, 6, n_fast)  # Suspiciously fast
        fast_distances = np.random.uniform(0.1, 0.5, n_fast)  # Very short
        fast_dates = [datetime(2021, 6, 1) + timedelta(days=i*10) for i in range(n_fast)]
        
        for i in range(n_fast):
            outlier_examples.append({
                'workout_date': fast_dates[i],
                'activity_type': 'Run',
                'avg_pace': fast_paces[i],
                'distance_mi': fast_distances[i],
                'duration_sec': fast_paces[i] * fast_distances[i] * 60,
                'true_class': 'outlier',
                'difficulty': 'impossible',
                'scenario': 'GPS measurement error or sprint interval'
            })
        
        # Ultra-slow paces (standing around with GPS on)
        n_slow = n_outliers - n_fast
        slow_paces = np.random.uniform(45, 120, n_slow)  # Ridiculously slow
        slow_distances = np.random.uniform(0.1, 0.8, n_slow)
        slow_dates = [datetime(2021, 7, 1) + timedelta(days=i*10) for i in range(n_slow)]
        
        for i in range(n_slow):
            outlier_examples.append({
                'workout_date': slow_dates[i],
                'activity_type': 'Walk',
                'avg_pace': slow_paces[i],
                'distance_mi': slow_distances[i],
                'duration_sec': slow_paces[i] * slow_distances[i] * 60,
                'true_class': 'outlier', 
                'difficulty': 'impossible',
                'scenario': 'Forgot to turn off GPS while socializing'
            })
        
        # Convert to DataFrame
        df = pd.DataFrame(outlier_examples)
        
        # Add calories (very low for outliers)
        df['kcal_burned'] = np.random.uniform(5, 30, len(df))
        
        return df
    
    def generate_complete_dataset(self, 
                                n_clear_runs: int = 100,
                                n_clear_walks: int = 100, 
                                n_ambiguous: int = 50,
                                n_outliers: int = 15) -> pd.DataFrame:
        """Generate a complete dataset with all types of examples."""
        
        # Generate each type
        clear_df = self.generate_clear_examples(n_clear_runs, n_clear_walks)
        ambiguous_df = self.generate_ambiguous_examples(n_ambiguous) 
        outlier_df = self.generate_outlier_examples(n_outliers)
        
        # Add scenario column to clear examples
        clear_df['scenario'] = clear_df['true_class'].map({
            'real_run': 'Standard running workout',
            'choco_adventure': 'Leisurely walking adventure'
        })
        
        # Combine all data
        complete_df = pd.concat([clear_df, ambiguous_df, outlier_df], ignore_index=True)
        
        # Shuffle and add derived features
        complete_df = complete_df.sample(frac=1).reset_index(drop=True)
        complete_df['duration_min'] = complete_df['duration_sec'] / 60
        complete_df['year'] = complete_df['workout_date'].dt.year
        complete_df['month'] = complete_df['workout_date'].dt.month
        
        # Add some realistic data quality issues
        # Missing values (2% of data)
        missing_indices = np.random.choice(len(complete_df), int(len(complete_df) * 0.02), replace=False)
        complete_df.loc[missing_indices, 'kcal_burned'] = np.nan
        
        # Slightly inconsistent activity type labels (realistic messiness)
        inconsistent_indices = np.random.choice(len(complete_df), int(len(complete_df) * 0.05), replace=False)
        for idx in inconsistent_indices:
            if complete_df.loc[idx, 'avg_pace'] < 15:
                complete_df.loc[idx, 'activity_type'] = np.random.choice(['Run', 'Jog', 'Interval Run'])
            else:
                complete_df.loc[idx, 'activity_type'] = np.random.choice(['Walk', 'Brisk Walk', 'Hike'])
        
        return complete_df
    
    def create_classification_test_set(self) -> Dict[str, pd.DataFrame]:
        """Create labeled test datasets for algorithm comparison."""
        
        # Generate different difficulty levels
        easy_set = self.generate_clear_examples(30, 30)
        medium_set = self.generate_ambiguous_examples(20) 
        hard_set = self.generate_outlier_examples(10)
        
        # Add confidence expectations
        easy_set['expected_confidence'] = 'high'
        medium_set['expected_confidence'] = 'medium'
        hard_set['expected_confidence'] = 'low'
        
        return {
            'easy': easy_set,
            'medium': medium_set, 
            'hard': hard_set,
            'combined': pd.concat([easy_set, medium_set, hard_set], ignore_index=True).sample(frac=1).reset_index(drop=True)
        }
    
    def simulate_choco_effect_dataset(self, years_pre: int = 5, years_post: int = 5) -> pd.DataFrame:
        """Simulate the complete Choco Effect dataset showing behavioral shift."""
        
        # Pre-Choco period (mostly running)
        pre_start = datetime(2013, 1, 1)
        pre_workouts = []
        
        for year_offset in range(years_pre):
            year_workouts = 60 + np.random.poisson(20)  # ~60-80 workouts per year
            for i in range(year_workouts):
                workout_date = pre_start + timedelta(days=year_offset*365 + i*6 + np.random.randint(-2, 3))
                
                # 90% running, 10% walking
                if np.random.random() < 0.9:
                    pace = np.random.normal(9.5, 1.5)
                    pace = np.clip(pace, 7, 12)
                    distance = np.random.normal(4.5, 1.8) 
                    true_class = 'real_run'
                    activity_type = 'Run'
                else:
                    pace = np.random.normal(20, 2)
                    distance = np.random.normal(2.8, 1)
                    true_class = 'choco_adventure'
                    activity_type = 'Walk'
                
                distance = np.clip(distance, 0.5, 10)
                duration = pace * distance * 60
                
                pre_workouts.append({
                    'workout_date': workout_date,
                    'activity_type': activity_type,
                    'avg_pace': pace,
                    'distance_mi': distance,
                    'duration_sec': duration,
                    'true_class': true_class,
                    'period': 'pre_choco',
                    'kcal_burned': distance * 100 + np.random.normal(0, 20)
                })
        
        # Post-Choco period (mixed activities)
        post_start = datetime(2018, 1, 1)
        post_workouts = []
        
        for year_offset in range(years_post):
            year_workouts = 80 + np.random.poisson(30)  # More frequent workouts
            for i in range(year_workouts):
                workout_date = post_start + timedelta(days=year_offset*365 + i*4 + np.random.randint(-2, 3))
                
                # 25% running, 65% walking, 10% mixed
                rand = np.random.random()
                if rand < 0.25:  # Running
                    pace = np.random.normal(9, 1.2)
                    pace = np.clip(pace, 7, 12)
                    distance = np.random.normal(4.2, 1.5)
                    true_class = 'real_run'
                    activity_type = 'Run'
                elif rand < 0.9:  # Walking adventures
                    pace = np.random.normal(23, 3)
                    pace = np.clip(pace, 18, 30)
                    distance = np.random.normal(2.3, 0.9)
                    true_class = 'choco_adventure'
                    activity_type = 'Walk'
                else:  # Mixed activities
                    pace = np.random.normal(15, 3)
                    pace = np.clip(pace, 11, 20)
                    distance = np.random.normal(3.2, 1.2)
                    true_class = 'mixed'
                    activity_type = np.random.choice(['Interval Run', 'Brisk Walk'])
                
                distance = np.clip(distance, 0.5, 8)
                duration = pace * distance * 60
                
                post_workouts.append({
                    'workout_date': workout_date,
                    'activity_type': activity_type,
                    'avg_pace': pace,
                    'distance_mi': distance,
                    'duration_sec': duration,
                    'true_class': true_class,
                    'period': 'post_choco',
                    'kcal_burned': distance * 90 + np.random.normal(0, 25)  # Slightly lower calorie efficiency
                })
        
        # Combine and process
        all_workouts = pre_workouts + post_workouts
        df = pd.DataFrame(all_workouts)
        
        # Clean up calories
        df['kcal_burned'] = np.clip(df['kcal_burned'], 30, 800)
        
        # Add derived features
        df['duration_min'] = df['duration_sec'] / 60
        df['year'] = df['workout_date'].dt.year
        df['choco_effect'] = df['period'] == 'post_choco'
        
        return df.sort_values('workout_date').reset_index(drop=True)

# Convenience functions for notebook use
def load_or_generate_sample_data(file_path: str = 'data/sample_workouts.csv', 
                                force_generate: bool = False) -> pd.DataFrame:
    """Load existing sample data or generate new synthetic dataset."""
    
    if not force_generate:
        try:
            df = pd.read_csv(file_path)
            if 'workout_date' in df.columns:
                df['workout_date'] = pd.to_datetime(df['workout_date'])
            print(f"✅ Loaded {len(df)} workouts from {file_path}")
            return df
        except (FileNotFoundError, pd.errors.EmptyDataError):
            print(f"📁 File not found: {file_path}")
    
    print("🔄 Generating synthetic dataset...")
    generator = FitnessDataGenerator()
    df = generator.simulate_choco_effect_dataset()
    
    # Save for future use
    try:
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_csv(file_path, index=False)
        print(f"💾 Saved generated data to {file_path}")
    except Exception as e:
        print(f"⚠️ Could not save data: {str(e)}")
    
    print(f"✅ Generated {len(df)} synthetic workouts")
    return df

def create_algorithm_comparison_datasets() -> Dict[str, pd.DataFrame]:
    """Create datasets specifically designed for algorithm comparison demos."""
    
    generator = FitnessDataGenerator(random_seed=42)
    
    return {
        'training': generator.generate_complete_dataset(80, 80, 40, 10),
        'test_easy': generator.generate_clear_examples(25, 25),
        'test_hard': generator.generate_ambiguous_examples(20),
        'test_outliers': generator.generate_outlier_examples(10),
        'choco_effect': generator.simulate_choco_effect_dataset(3, 3)
    }