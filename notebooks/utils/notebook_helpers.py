"""
Utility functions for fitness data analysis notebooks.

This module provides reusable plotting functions, data processing utilities,
and interactive widget generators optimized for educational demonstrations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display, HTML
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Set consistent styling
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class FitnessDataVisualizer:
    """Interactive visualization tools for fitness data analysis."""
    
    def __init__(self):
        self.colors = {
            'real_run': '#2E8B57',      # Sea Green
            'choco_adventure': '#DAA520', # Goldenrod  
            'mixed': '#4682B4',         # Steel Blue
            'outlier': '#DC143C',       # Crimson
            'unknown': '#778899'        # Light Slate Gray
        }
        
    def plot_timeline_overview(self, df: pd.DataFrame, figsize=(15, 8)) -> None:
        """Create comprehensive timeline view showing the Choco Effect."""
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle('The Choco Effect: 14 Years of Fitness Data Evolution', fontsize=16)
        
        # Convert workout_date to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(df['workout_date']):
            df['workout_date'] = pd.to_datetime(df['workout_date'])
            
        df['year'] = df['workout_date'].dt.year
        
        # Plot 1: Workout frequency over time
        yearly_counts = df.groupby('year').size()
        axes[0,0].plot(yearly_counts.index, yearly_counts.values, marker='o', linewidth=2)
        axes[0,0].axvline(x=2018, color='red', linestyle='--', alpha=0.7, label='Choco Arrives')
        axes[0,0].set_title('Workout Frequency by Year')
        axes[0,0].set_ylabel('Number of Workouts')
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
        
        # Plot 2: Average pace evolution
        yearly_pace = df.groupby('year')['avg_pace'].mean()
        axes[0,1].plot(yearly_pace.index, yearly_pace.values, marker='o', linewidth=2, color='orange')
        axes[0,1].axvline(x=2018, color='red', linestyle='--', alpha=0.7, label='Choco Arrives')
        axes[0,1].set_title('Average Pace Trend')
        axes[0,1].set_ylabel('Average Pace (min/mile)')
        axes[0,1].legend()
        axes[0,1].grid(True, alpha=0.3)
        
        # Plot 3: Pace distribution pre/post 2018
        pre_2018 = df[df['year'] < 2018]['avg_pace']
        post_2018 = df[df['year'] >= 2018]['avg_pace']
        
        axes[1,0].hist(pre_2018, alpha=0.7, bins=30, label='Pre-2018', color='skyblue')
        axes[1,0].hist(post_2018, alpha=0.7, bins=30, label='Post-2018', color='lightcoral')
        axes[1,0].set_title('Pace Distribution: Before vs After')
        axes[1,0].set_xlabel('Average Pace (min/mile)')
        axes[1,0].set_ylabel('Frequency')
        axes[1,0].legend()
        axes[1,0].grid(True, alpha=0.3)
        
        # Plot 4: Distance patterns
        yearly_distance = df.groupby('year')['distance_mi'].mean()
        axes[1,1].plot(yearly_distance.index, yearly_distance.values, marker='o', linewidth=2, color='green')
        axes[1,1].axvline(x=2018, color='red', linestyle='--', alpha=0.7, label='Choco Arrives')
        axes[1,1].set_title('Average Distance Trend')
        axes[1,1].set_xlabel('Year')
        axes[1,1].set_ylabel('Average Distance (miles)')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
    def plot_classification_results(self, df: pd.DataFrame, classification_col='predicted_class') -> None:
        """Visualize ML classification results with confidence scoring."""
        if classification_col not in df.columns:
            print(f"Warning: Column '{classification_col}' not found. Showing data structure instead.")
            print(df.columns.tolist())
            return
            
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Classification Distribution', 'Confidence by Class', 
                          'Pace vs Distance (Colored by Class)', 'Confidence Distribution'),
            specs=[[{"type": "pie"}, {"type": "box"}],
                   [{"type": "scatter"}, {"type": "histogram"}]]
        )
        
        # Classification distribution pie chart
        class_counts = df[classification_col].value_counts()
        fig.add_trace(go.Pie(
            labels=class_counts.index,
            values=class_counts.values,
            name="Classification"
        ), row=1, col=1)
        
        # Confidence by classification box plot
        if 'confidence' in df.columns:
            for class_name in df[classification_col].unique():
                class_data = df[df[classification_col] == class_name]
                fig.add_trace(go.Box(
                    y=class_data['confidence'],
                    name=class_name,
                    marker_color=self.colors.get(class_name, '#778899')
                ), row=1, col=2)
        
        # Scatter plot: pace vs distance, colored by classification
        fig.add_trace(go.Scatter(
            x=df['distance_mi'],
            y=df['avg_pace'],
            mode='markers',
            marker=dict(
                color=[self.colors.get(c, '#778899') for c in df[classification_col]],
                size=8,
                opacity=0.7
            ),
            text=df[classification_col],
            name="Workouts"
        ), row=2, col=1)
        
        # Confidence distribution histogram
        if 'confidence' in df.columns:
            fig.add_trace(go.Histogram(
                x=df['confidence'],
                nbinsx=20,
                name="Confidence"
            ), row=2, col=2)
        
        fig.update_layout(height=800, showlegend=True, title_text="ML Classification Analysis")
        fig.show()
        
    def create_interactive_pace_explorer(self, df: pd.DataFrame) -> None:
        """Create interactive widget for exploring pace patterns."""
        
        # Date range slider
        min_date = df['workout_date'].min()
        max_date = df['workout_date'].max()
        
        date_range = widgets.SelectionRangeSlider(
            options=pd.date_range(min_date, max_date, freq='M').tolist(),
            index=(0, len(pd.date_range(min_date, max_date, freq='M')) - 1),
            description='Date Range',
            layout=widgets.Layout(width='600px')
        )
        
        # Pace range slider  
        pace_range = widgets.FloatRangeSlider(
            value=[df['avg_pace'].min(), df['avg_pace'].max()],
            min=df['avg_pace'].min(),
            max=df['avg_pace'].max(),
            step=0.5,
            description='Pace Range:',
            layout=widgets.Layout(width='400px')
        )
        
        # Activity type filter
        activity_filter = widgets.SelectMultiple(
            options=df['activity_type'].unique().tolist(),
            value=df['activity_type'].unique().tolist(),
            description='Activity Types:'
        )
        
        output = widgets.Output()
        
        def update_plot(*args):
            with output:
                output.clear_output(wait=True)
                
                # Filter data
                filtered_df = df[
                    (df['workout_date'] >= date_range.value[0]) &
                    (df['workout_date'] <= date_range.value[1]) &
                    (df['avg_pace'] >= pace_range.value[0]) &
                    (df['avg_pace'] <= pace_range.value[1]) &
                    (df['activity_type'].isin(activity_filter.value))
                ]
                
                if len(filtered_df) == 0:
                    print("No data matches the current filters.")
                    return
                    
                # Create plot
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
                
                # Timeline plot
                ax1.scatter(filtered_df['workout_date'], filtered_df['avg_pace'], 
                          alpha=0.6, s=50)
                ax1.set_xlabel('Date')
                ax1.set_ylabel('Average Pace (min/mile)')
                ax1.set_title(f'Pace Timeline ({len(filtered_df)} workouts)')
                ax1.grid(True, alpha=0.3)
                
                # Histogram
                ax2.hist(filtered_df['avg_pace'], bins=20, alpha=0.7, edgecolor='black')
                ax2.axvline(filtered_df['avg_pace'].mean(), color='red', linestyle='--', 
                          label=f'Mean: {filtered_df["avg_pace"].mean():.1f}')
                ax2.axvline(filtered_df['avg_pace'].median(), color='green', linestyle='--',
                          label=f'Median: {filtered_df["avg_pace"].median():.1f}')
                ax2.set_xlabel('Average Pace (min/mile)')
                ax2.set_ylabel('Frequency')
                ax2.set_title('Pace Distribution')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
                
                plt.tight_layout()
                plt.show()
                
                # Summary statistics
                print(f"\n📊 Summary for {len(filtered_df)} selected workouts:")
                print(f"   • Pace range: {filtered_df['avg_pace'].min():.1f} - {filtered_df['avg_pace'].max():.1f} min/mile")
                print(f"   • Distance range: {filtered_df['distance_mi'].min():.1f} - {filtered_df['distance_mi'].max():.1f} miles")
                print(f"   • Time period: {filtered_df['workout_date'].min().strftime('%Y-%m')} to {filtered_df['workout_date'].max().strftime('%Y-%m')}")
        
        # Connect widgets to update function
        date_range.observe(update_plot, names='value')
        pace_range.observe(update_plot, names='value')
        activity_filter.observe(update_plot, names='value')
        
        # Initial plot
        update_plot()
        
        # Display widgets
        display(widgets.VBox([
            widgets.HTML("<h3>🔍 Interactive Pace Explorer</h3>"),
            date_range,
            pace_range, 
            activity_filter,
            output
        ]))

class ConfidenceAnalyzer:
    """Tools for analyzing and visualizing ML confidence scores."""
    
    @staticmethod
    def calculate_confidence_calibration(y_true: np.array, y_pred: np.array, 
                                       confidence: np.array, n_bins: int = 10) -> Dict:
        """Calculate confidence calibration metrics."""
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]
        
        accuracies = []
        confidences = []
        counts = []
        
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            in_bin = (confidence > bin_lower) & (confidence <= bin_upper)
            prop_in_bin = in_bin.mean()
            
            if prop_in_bin > 0:
                accuracy_in_bin = (y_true[in_bin] == y_pred[in_bin]).mean()
                avg_confidence_in_bin = confidence[in_bin].mean()
                accuracies.append(accuracy_in_bin)
                confidences.append(avg_confidence_in_bin)
                counts.append(in_bin.sum())
            else:
                accuracies.append(0)
                confidences.append(0)
                counts.append(0)
        
        return {
            'accuracies': accuracies,
            'confidences': confidences,
            'counts': counts,
            'calibration_error': np.mean(np.abs(np.array(accuracies) - np.array(confidences)))
        }
    
    @staticmethod
    def plot_calibration_curve(calibration_data: Dict, title: str = "Confidence Calibration") -> None:
        """Plot confidence calibration curve."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Calibration curve
        ax1.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration')
        ax1.plot(calibration_data['confidences'], calibration_data['accuracies'], 
                'o-', label='Model Calibration')
        ax1.set_xlabel('Mean Predicted Confidence')
        ax1.set_ylabel('Actual Accuracy')
        ax1.set_title(f'{title}\nCalibration Error: {calibration_data["calibration_error"]:.3f}')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Confidence histogram
        ax2.bar(range(len(calibration_data['counts'])), calibration_data['counts'], 
               alpha=0.7, color='skyblue')
        ax2.set_xlabel('Confidence Bin')
        ax2.set_ylabel('Number of Predictions')
        ax2.set_title('Confidence Distribution')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

def load_sample_data(file_path: str = 'data/sample_workouts.csv') -> pd.DataFrame:
    """Load and preprocess sample workout data for notebooks."""
    try:
        df = pd.read_csv(file_path)
        
        # Convert date column
        if 'workout_date' in df.columns:
            df['workout_date'] = pd.to_datetime(df['workout_date'])
            
        # Add derived features commonly used in analysis
        if 'avg_pace' in df.columns and 'distance_mi' in df.columns:
            df['pace_category'] = pd.cut(df['avg_pace'], 
                                       bins=[0, 8, 12, 20, np.inf],
                                       labels=['Fast', 'Moderate', 'Slow', 'Very Slow'])
            
        if 'duration_sec' in df.columns:
            df['duration_min'] = df['duration_sec'] / 60
            
        print(f"✅ Loaded {len(df)} workouts from {file_path}")
        print(f"📅 Date range: {df['workout_date'].min().strftime('%Y-%m-%d')} to {df['workout_date'].max().strftime('%Y-%m-%d')}")
        
        return df
        
    except FileNotFoundError:
        print(f"❌ Data file not found: {file_path}")
        print("💡 Make sure you're running from the notebooks directory")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        return pd.DataFrame()

def display_data_quality_report(df: pd.DataFrame) -> None:
    """Generate and display comprehensive data quality report."""
    
    print("📊 DATA QUALITY REPORT")
    print("=" * 50)
    
    # Basic info
    print(f"📈 Dataset Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"📅 Date Range: {df['workout_date'].min().strftime('%Y-%m-%d')} to {df['workout_date'].max().strftime('%Y-%m-%d')}")
    
    # Missing values
    print(f"\n🔍 Missing Values:")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(1)
    for col in missing.index[missing > 0]:
        print(f"   • {col}: {missing[col]} ({missing_pct[col]}%)")
    
    if missing.sum() == 0:
        print("   ✅ No missing values found!")
    
    # Data types
    print(f"\n📋 Data Types:")
    for dtype in df.dtypes.value_counts().index:
        cols = df.select_dtypes(include=[dtype]).columns.tolist()
        print(f"   • {dtype}: {len(cols)} columns")
    
    # Numerical summaries
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        print(f"\n📊 Numerical Summaries:")
        display(df[numeric_cols].describe().round(2))
    
    # Categorical summaries
    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        print(f"\n🏷️  Categorical Summaries:")
        for col in categorical_cols[:5]:  # Show first 5 categorical columns
            unique_count = df[col].nunique()
            print(f"   • {col}: {unique_count} unique values")
            if unique_count <= 10:
                print(f"     Values: {df[col].value_counts().head().to_dict()}")

def create_info_box(title: str, content: str, box_type: str = "info") -> None:
    """Create styled information box for notebooks."""
    
    colors = {
        "info": "#e7f3ff",
        "warning": "#fff8e7", 
        "success": "#e7ffe7",
        "error": "#ffe7e7"
    }
    
    icons = {
        "info": "ℹ️",
        "warning": "⚠️",
        "success": "✅", 
        "error": "❌"
    }
    
    color = colors.get(box_type, colors["info"])
    icon = icons.get(box_type, icons["info"])
    
    html_content = f"""
    <div style="
        background-color: {color};
        border-left: 5px solid #007acc;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        font-family: 'Segoe UI', Arial, sans-serif;
    ">
        <h4 style="margin-top: 0; color: #333;">
            {icon} {title}
        </h4>
        <p style="margin-bottom: 0; color: #555; line-height: 1.5;">
            {content}
        </p>
    </div>
    """
    
    display(HTML(html_content))

# Example usage functions for demonstrations
def demo_choco_effect():
    """Demonstrate the Choco Effect with sample data."""
    create_info_box(
        "The Choco Effect", 
        "This analysis reveals how the arrival of a dog named Choco in 2018 fundamentally changed workout patterns from focused running to leisurely walking adventures. This behavioral shift creates the 'mixed activity type' problem that our ML classification system solves.",
        "info"
    )

def demo_ambiguous_classification():
    """Show examples of genuinely ambiguous workouts."""
    create_info_box(
        "Real-World Ambiguity",
        "Some workouts are genuinely unclear even to human reviewers. A 45-minute session averaging 14 min/mile might include warm-up, intervals, and cooldown - is this a 'run' or 'walk'? Our confidence scoring system appropriately flags these cases rather than forcing binary decisions.",
        "warning"
    )

def demo_confidence_scoring():
    """Explain confidence scoring methodology.""" 
    create_info_box(
        "Understanding Confidence Scores",
        "Confidence scores (0-100%) indicate how certain our ML model is about each classification. High confidence usually means clear patterns; low confidence often indicates genuinely ambiguous cases that benefit from human review. This builds trust through honest uncertainty communication.",
        "success"
    )