"""
The Choco Effect Dashboard - Showcasing AI-Driven Fitness Intelligence

A portfolio-quality demonstration of how a dog transformed fitness data patterns,
featuring machine learning classification and statistical analysis.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
import os

# Add the src directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database_service import DatabaseService
from services.intelligence_service import FitnessIntelligenceService
from utils.consistency_analyzer import ConsistencyAnalyzer

# Page configuration
st.set_page_config(
    page_title="The Choco Effect", 
    page_icon="🐕",
    layout="wide"
)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_workout_data():
    """Load and cache workout data with error handling."""
    try:
        db = DatabaseService()
        query = """
        SELECT workout_date, activity_type, kcal_burned, distance_mi, 
               duration_sec, avg_pace, max_pace, steps
        FROM workout_summary 
        ORDER BY workout_date
        """
        return db.execute_query(query)
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return []

@st.cache_data(ttl=300)
def get_choco_analysis(workout_data):
    """Get comprehensive Choco Effect analysis."""
    if not workout_data:
        return None
    
    try:
        df = pd.DataFrame(workout_data)
        df['workout_date'] = pd.to_datetime(df['workout_date'])
        
        # Initialize intelligence service
        intelligence = FitnessIntelligenceService()
        
        # Get workout classifications
        classified_workouts = intelligence.classify_workout_types(df)
        
        # Calculate consistency metrics
        analyzer = ConsistencyAnalyzer(df)
        
        # Define Choco arrival date
        choco_date = pd.to_datetime('2018-06-01')
        
        # Split data into pre/post Choco periods
        pre_choco = df[df['workout_date'] < choco_date].copy()
        post_choco = df[df['workout_date'] >= choco_date].copy()
        
        return {
            'df': df,
            'classified_df': classified_workouts,
            'pre_choco': pre_choco,
            'post_choco': post_choco,
            'choco_date': choco_date,
            'analyzer': analyzer,
            'intelligence': intelligence
        }
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        return None

def create_transformation_timeline(analysis_data):
    """Create the main transformation timeline visualization."""
    df = analysis_data['df']
    choco_date = analysis_data['choco_date']
    
    # Create timeline showing workout frequency and pace
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Workout Frequency Over Time', 'Average Pace Transformation'),
        vertical_spacing=0.12
    )
    
    # Monthly workout counts
    monthly_counts = df.groupby(df['workout_date'].dt.to_period('M')).size()
    monthly_counts.index = monthly_counts.index.to_timestamp()
    
    # Workout frequency timeline
    colors = ['#3498db' if date < choco_date else '#e74c3c' for date in monthly_counts.index]
    
    fig.add_trace(
        go.Bar(
            x=monthly_counts.index,
            y=monthly_counts.values,
            name='Monthly Workouts',
            marker_color=colors,
            opacity=0.8,
            hovertemplate='<b>%{x|%B %Y}</b><br>Workouts: %{y}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add Choco arrival line
    fig.add_vline(
        x=choco_date, 
        line_dash="dash", 
        line_color="#9b59b6", 
        line_width=3,
        annotation_text="🐕 Choco Arrives",
        annotation_position="top",
        row=1, col=1
    )
    
    # Monthly average pace
    monthly_pace = df.groupby(df['workout_date'].dt.to_period('M'))['avg_pace'].mean()
    monthly_pace.index = monthly_pace.index.to_timestamp()
    
    # Filter out extreme outliers for visualization
    pace_filtered = monthly_pace[monthly_pace <= 30]  # Remove extreme outliers
    
    fig.add_trace(
        go.Scatter(
            x=pace_filtered.index,
            y=pace_filtered.values,
            mode='lines+markers',
            name='Average Pace',
            line=dict(color='#2c3e50', width=3),
            marker=dict(size=6),
            hovertemplate='<b>%{x|%B %Y}</b><br>Avg Pace: %{y:.1f} min/mi<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Add Choco arrival line to pace chart
    fig.add_vline(
        x=choco_date, 
        line_dash="dash", 
        line_color="#9b59b6", 
        line_width=3,
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        title_text="<b>The Choco Effect: A Data-Driven Transformation Story</b>",
        title_x=0.5,
        showlegend=False,
        font=dict(size=12),
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # Update y-axes
    fig.update_yaxes(title_text="Workouts per Month", row=1, col=1)
    fig.update_yaxes(title_text="Average Pace (min/mile)", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    
    return fig

def create_before_after_comparison(analysis_data):
    """Create before/after comparison charts."""
    pre_choco = analysis_data['pre_choco']
    post_choco = analysis_data['post_choco']
    
    # Calculate key metrics
    metrics = {
        'Pre-Choco (7 years)': {
            'Total Workouts': len(pre_choco),
            'Avg Workouts/Month': len(pre_choco) / 84,  # 7 years ≈ 84 months
            'Avg Pace (min/mi)': pre_choco['avg_pace'][pre_choco['avg_pace'] <= 30].mean(),
            'Avg Distance (mi)': pre_choco['distance_mi'].mean(),
            'Longest Streak': 'Analysis needed'
        },
        'Post-Choco (6.5 years)': {
            'Total Workouts': len(post_choco),
            'Avg Workouts/Month': len(post_choco) / 78,  # 6.5 years ≈ 78 months
            'Avg Pace (min/mi)': post_choco['avg_pace'][post_choco['avg_pace'] <= 30].mean(),
            'Avg Distance (mi)': post_choco['distance_mi'].mean(),
            'Longest Streak': 'Analysis needed'
        }
    }
    
    # Create comparison cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏃‍♂️ Pre-Choco Era")
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; color: white; margin: 10px 0;">
            <h4>The Consistent Runner</h4>
            <ul>
                <li><strong>{metrics['Pre-Choco (7 years)']['Total Workouts']}</strong> total workouts</li>
                <li><strong>{metrics['Pre-Choco (7 years)']['Avg Workouts/Month']:.1f}</strong> workouts/month</li>
                <li><strong>{metrics['Pre-Choco (7 years)']['Avg Pace (min/mi)']:.1f}</strong> min/mile average</li>
                <li><strong>{metrics['Pre-Choco (7 years)']['Avg Distance (mi)']:.1f}</strong> mile average distance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🐕 Post-Choco Era")
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 20px; border-radius: 10px; color: white; margin: 10px 0;">
            <h4>The Daily Adventurer</h4>
            <ul>
                <li><strong>{metrics['Post-Choco (6.5 years)']['Total Workouts']}</strong> total workouts</li>
                <li><strong>{metrics['Post-Choco (6.5 years)']['Avg Workouts/Month']:.1f}</strong> workouts/month</li>
                <li><strong>{metrics['Post-Choco (6.5 years)']['Avg Pace (min/mi)']:.1f}</strong> min/mile average</li>
                <li><strong>{metrics['Post-Choco (6.5 years)']['Avg Distance (mi)']:.1f}</strong> mile average distance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Calculate and display the transformation magnitude
    freq_increase = (metrics['Post-Choco (6.5 years)']['Avg Workouts/Month'] / 
                    metrics['Pre-Choco (7 years)']['Avg Workouts/Month'])
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #f093fb 100%); 
                padding: 25px; border-radius: 15px; color: white; text-align: center; 
                margin: 20px 0; font-size: 18px;">
        <h3>🚀 The Transformation</h3>
        <p><strong>{freq_increase:.1f}x</strong> increase in workout frequency</p>
        <p>From <strong>{metrics['Pre-Choco (7 years)']['Avg Workouts/Month']:.0f}</strong> to <strong>{metrics['Post-Choco (6.5 years)']['Avg Workouts/Month']:.0f}</strong> workouts per month</p>
    </div>
    """, unsafe_allow_html=True)
    
    return metrics

def create_classification_demo(analysis_data):
    """Create an interactive workout classification demonstration."""
    classified_df = analysis_data['classified_df']
    
    if classified_df is None or 'predicted_activity_type' not in classified_df.columns:
        st.warning("Classification data not available")
        return
    
    st.markdown("### 🤖 AI Workout Classifier in Action")
    st.markdown("*How machine learning automatically identifies workout types from pace and distance patterns*")
    
    # Show classification statistics
    classification_stats = classified_df['predicted_activity_type'].value_counts()
    
    # Create pie chart of classifications
    fig = px.pie(
        values=classification_stats.values, 
        names=classification_stats.index,
        title="Workout Classification Results",
        color_discrete_map={
            'real_run': '#3498db',
            'choco_adventure': '#e74c3c', 
            'mixed': '#9b59b6',
            'outlier': '#95a5a6'
        }
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Classification Breakdown")
        for activity_type, count in classification_stats.items():
            percentage = (count / len(classified_df)) * 100
            
            # Map activity types to emojis and descriptions
            type_info = {
                'real_run': ('🏃‍♂️', 'Focused running sessions'),
                'choco_adventure': ('🐕', 'Dog walking adventures'), 
                'mixed': ('🚶‍♂️', 'Mixed activity sessions'),
                'outlier': ('🤔', 'Unusual workout patterns')
            }
            
            emoji, description = type_info.get(activity_type, ('📊', 'Unknown activity'))
            
            st.markdown(f"""
            **{emoji} {activity_type.replace('_', ' ').title()}**  
            {count} workouts ({percentage:.1f}%)  
            *{description}*
            """)
    
    # Interactive sample viewer
    st.markdown("#### 🔍 Sample Classifications")
    
    # Show a sample of each classification type
    sample_data = []
    for activity_type in classification_stats.index[:4]:  # Top 4 types
        samples = classified_df[classified_df['predicted_activity_type'] == activity_type].head(3)
        for _, row in samples.iterrows():
            sample_data.append({
                'Date': row['workout_date'].strftime('%Y-%m-%d'),
                'Classified As': activity_type.replace('_', ' ').title(),
                'Pace (min/mi)': f"{row['avg_pace']:.1f}",
                'Distance (mi)': f"{row['distance_mi']:.1f}",
                'Duration (min)': f"{row['duration_sec']/60:.0f}",
                'Confidence': 'High'  # Could add actual confidence scores
            })
    
    sample_df = pd.DataFrame(sample_data)
    st.dataframe(sample_df, use_container_width=True, height=300)

def create_consistency_insights(analysis_data):
    """Create consistency and intelligence insights."""
    analyzer = analysis_data['analyzer']
    intelligence = analysis_data['intelligence']
    df = analysis_data['df']
    
    st.markdown("### 🧠 AI-Generated Insights")
    
    try:
        # Generate intelligence brief
        brief = intelligence.generate_daily_intelligence_brief(df)
        
        if brief and 'insights' in brief:
            insights = brief['insights']
            
            # Display key insights in cards
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎯 Performance Intelligence")
                for insight in insights.get('performance', [])[:3]:
                    st.info(f"💡 {insight}")
            
            with col2:
                st.markdown("#### 📈 Trend Intelligence") 
                for insight in insights.get('trends', [])[:3]:
                    st.success(f"📊 {insight}")
        
        # Generate consistency insights
        consistency_insights = analyzer.generate_consistency_insights()
        
        if consistency_insights:
            st.markdown("#### ⚡ Consistency Intelligence")
            for insight in consistency_insights[:4]:
                st.markdown(f"🔥 {insight}")
    
    except Exception as e:
        st.error(f"Intelligence analysis failed: {e}")

def main():
    """Main dashboard function."""
    # Header with styling
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; margin-bottom: 30px;">
        <h1 style="color: white; margin: 0;">🐕 The Choco Effect Dashboard</h1>
        <p style="color: white; margin: 10px 0 0 0; font-size: 18px;">
            How a rescue dog transformed 14 years of fitness data
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    with st.spinner("🔄 Loading workout data and running AI analysis..."):
        workout_data = load_workout_data()
        
        if not workout_data:
            st.error("❌ No workout data available. Please check your database connection.")
            return
            
        analysis_data = get_choco_analysis(workout_data)
        
        if not analysis_data:
            st.error("❌ Failed to analyze workout data.")
            return
    
    # Success metrics
    total_workouts = len(analysis_data['df'])
    date_range = (analysis_data['df']['workout_date'].max() - 
                 analysis_data['df']['workout_date'].min()).days
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Workouts", f"{total_workouts:,}")
    col2.metric("Years Tracked", f"{date_range/365:.1f}")
    col3.metric("Pre-Choco", len(analysis_data['pre_choco']))
    col4.metric("Post-Choco", len(analysis_data['post_choco']))
    
    st.markdown("---")
    
    # Main transformation timeline
    st.markdown("## 📊 The Data Story")
    timeline_fig = create_transformation_timeline(analysis_data)
    st.plotly_chart(timeline_fig, use_container_width=True)
    
    st.markdown("---")
    
    # Before/After comparison
    st.markdown("## ⚖️ The Transformation Metrics")
    create_before_after_comparison(analysis_data)
    
    st.markdown("---")
    
    # AI Classification demo
    create_classification_demo(analysis_data)
    
    st.markdown("---")
    
    # Intelligence insights
    create_consistency_insights(analysis_data)
    
    # Footer with technical details
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: #7f8c8d;">
        <p><strong>Technical Implementation:</strong> Python • Streamlit • MySQL • scikit-learn • Plotly</p>
        <p><strong>AI Features:</strong> K-means Clustering • Statistical Analysis • Trend Detection • Anomaly Detection</p>
        <p>🔗 <em>Portfolio project demonstrating data science and machine learning capabilities</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()