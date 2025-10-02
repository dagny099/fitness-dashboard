"""
Model Management Dashboard

A comprehensive interface for managing ML models in the fitness dashboard.
Provides full control over model training, evaluation, versioning, and deployment.

Features:
- Model status and performance overview
- Training controls with progress tracking
- Model version comparison and history
- Learned parameters visualization
- Performance metrics and quality assessment
- Model approval and deployment workflow
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Optional

from ml.model_manager import model_manager, ModelManager, WorkoutClassificationModel
from services.intelligence_service import FitnessIntelligenceService
from config.app import ACTIVITY_TYPE_CONFIG
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def render_model_management_header():
    """Render the model management page header."""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 25px; border-radius: 15px; color: white; margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin: 0; font-size: 2.5rem;">🤖 Model Management</h1>
                <p style="margin: 5px 0 0 0; font-size: 1.1rem; opacity: 0.9;">
                    Control and monitor your ML classification models
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_model_status_overview():
    """Render comprehensive model status overview."""
    st.header("🔍 Current Model Status")

    model_stats = model_manager.get_model_stats()

    if not model_stats['model_available']:
        st.error("❌ No trained model available")
        st.info("Click 'Train New Model' below to create your first model from historical data.")
        return None

    model_summary = model_stats['model_summary']

    # Main status metrics in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🎯 Model Status",
            value=model_summary['status'].title(),
            delta=f"v{model_summary['version']}"
        )

    with col2:
        st.metric(
            label="📊 Quality Rating",
            value=model_summary['quality_rating'],
            delta=f"{model_summary['silhouette_score']} silhouette"
        )

    with col3:
        st.metric(
            label="🏋️ Training Data",
            value=f"{model_summary['training_workouts']:,}",
            delta="workouts"
        )

    with col4:
        days_since_training = (datetime.now() - datetime.strptime(model_summary['trained_at'], '%Y-%m-%d %H:%M:%S')).days
        st.metric(
            label="⏰ Model Age",
            value=f"{days_since_training} days",
            delta="since training"
        )

    # Detailed information in expandable sections
    with st.expander("📋 Model Details", expanded=True):
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("**Model Information:**")
            st.write(f"• **ID:** `{model_summary['model_id']}`")
            st.write(f"• **Trained:** {model_summary['trained_at']}")
            st.write(f"• **Training Period:** {model_summary['training_period']}")
            st.write(f"• **Clusters:** {model_summary['clusters']}")

        with col_right:
            st.markdown("**Classification Mapping:**")
            for cluster, activity in model_summary['classification_mapping'].items():
                activity_config = ACTIVITY_TYPE_CONFIG.get(activity, {})
                emoji = activity_config.get('emoji', '❓')
                display_name = activity_config.get('display_name', activity.replace('_', ' ').title())
                st.write(f"• **{cluster}** → {emoji} {display_name}")

    return model_stats


def render_activity_type_breakdown(model_stats: Dict):
    """Render detailed breakdown of learned activity types."""
    st.header("🎯 Learned Activity Patterns")

    activity_stats = model_stats['activity_type_stats']

    if not activity_stats:
        st.warning("No activity type statistics available.")
        return

    # Create activity distribution chart
    activity_counts = {activity: stats['count'] for activity, stats in activity_stats.items()}

    fig = px.pie(
        values=list(activity_counts.values()),
        names=[ACTIVITY_TYPE_CONFIG.get(k, {}).get('display_name', k.replace('_', ' ').title())
               for k in activity_counts.keys()],
        title="Training Data Distribution",
        color_discrete_map={
            ACTIVITY_TYPE_CONFIG.get(k, {}).get('display_name', k): ACTIVITY_TYPE_CONFIG.get(k, {}).get('color', '#cccccc')
            for k in activity_counts.keys()
        }
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)

    col_chart, col_details = st.columns([1, 1])

    with col_chart:
        st.plotly_chart(fig, use_container_width=True)

    with col_details:
        st.markdown("#### 📊 Activity Characteristics")

        for activity_type, stats in activity_stats.items():
            activity_config = ACTIVITY_TYPE_CONFIG.get(activity_type, {})
            emoji = activity_config.get('emoji', '❓')
            display_name = activity_config.get('display_name', activity_type.replace('_', ' ').title())

            with st.container():
                st.markdown(f"**{emoji} {display_name}** ({stats['count']} workouts)")

                col_pace, col_dist = st.columns(2)
                with col_pace:
                    st.write(f"⏱️ **Pace:** {stats['avg_pace']:.1f} min/mi")
                with col_dist:
                    st.write(f"📏 **Distance:** {stats['avg_distance']:.1f} mi")

                st.write(f"⏳ **Duration:** {stats['avg_duration']:.0f} min")

                pace_range = stats.get('pace_range', [0, 0])
                st.write(f"📈 **Pace Range:** {pace_range[0]:.1f} - {pace_range[1]:.1f} min/mi")

                st.markdown("---")


def render_model_performance_charts(model_stats: Dict):
    """Render detailed model performance visualizations."""
    st.header("📈 Model Performance Analysis")

    performance_metrics = model_stats['performance_metrics']

    if 'error' in performance_metrics:
        st.error(f"Performance data unavailable: {performance_metrics['error']}")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Silhouette score gauge
        silhouette_score = performance_metrics['silhouette_score']

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=silhouette_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Silhouette Score<br><span style='font-size:12px'>(Clustering Quality)</span>"},
            delta={'reference': 0.5, 'suffix': " vs Good"},
            gauge={
                'axis': {'range': [None, 1]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 0.3], 'color': "lightgray"},
                    {'range': [0.3, 0.5], 'color': "yellow"},
                    {'range': [0.5, 0.7], 'color': "lightgreen"},
                    {'range': [0.7, 1], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0.7
                }
            }
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        # Cluster distribution
        cluster_dist = performance_metrics.get('cluster_distribution', {})

        if cluster_dist:
            fig_clusters = px.bar(
                x=list(cluster_dist.keys()),
                y=list(cluster_dist.values()),
                title="Workouts per Cluster",
                labels={'x': 'Cluster ID', 'y': 'Number of Workouts'},
                color=list(cluster_dist.values()),
                color_continuous_scale='viridis'
            )
            fig_clusters.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_clusters, use_container_width=True)

    # Confidence statistics
    confidence_stats = performance_metrics.get('confidence_stats', {})
    if confidence_stats:
        st.subheader("🎯 Classification Confidence Analysis")

        conf_col1, conf_col2, conf_col3, conf_col4 = st.columns(4)

        with conf_col1:
            st.metric("Mean Confidence", f"{confidence_stats['mean']:.3f}")
        with conf_col2:
            st.metric("Median Confidence", f"{confidence_stats['median']:.3f}")
        with conf_col3:
            st.metric("Std Deviation", f"{confidence_stats['std']:.3f}")
        with conf_col4:
            st.metric("Min Confidence", f"{confidence_stats['min']:.3f}")


def render_model_history():
    """Render model version history and comparison features."""
    st.header("📚 Model History & Versions")

    archived_models = model_manager.get_archived_models()

    if not archived_models:
        st.info("No archived models found. Models will appear here after retraining.")
        return

    st.write(f"Found {len(archived_models)} archived models:")

    # Create comparison table
    history_data = []
    for archived in archived_models:
        trained_date = archived.get('trained_at', 'Unknown')
        if trained_date != 'Unknown':
            try:
                trained_date = datetime.fromisoformat(trained_date).strftime('%Y-%m-%d %H:%M')
            except:
                pass

        history_data.append({
            'Model ID': archived.get('model_id', 'Unknown')[:20] + '...',
            'Version': archived.get('version', '1.0.0'),
            'Trained': trained_date,
            'Training Data': f"{archived.get('training_workouts', 0):,} workouts",
            'Quality Score': f"{archived.get('silhouette_score', 0):.3f}",
            'Clusters': archived.get('clusters', 3)
        })

    if history_data:
        df_history = pd.DataFrame(history_data)
        st.dataframe(df_history, use_container_width=True, hide_index=True)

        # Model comparison visualization
        if len(archived_models) > 0:
            st.subheader("📊 Model Performance Over Time")

            # Extract performance data for plotting
            model_dates = []
            silhouette_scores = []
            training_sizes = []

            for archived in archived_models:
                try:
                    if archived.get('trained_at'):
                        model_dates.append(datetime.fromisoformat(archived['trained_at']))
                        silhouette_scores.append(archived.get('silhouette_score', 0))
                        training_sizes.append(archived.get('training_workouts', 0))
                except:
                    continue

            # Add current model if available
            current_stats = model_manager.get_model_stats()
            if current_stats['model_available']:
                current_summary = current_stats['model_summary']
                try:
                    current_date = datetime.strptime(current_summary['trained_at'], '%Y-%m-%d %H:%M:%S')
                    model_dates.append(current_date)
                    silhouette_scores.append(current_summary['silhouette_score'])
                    training_sizes.append(current_summary['training_workouts'])
                except:
                    pass

            if model_dates and silhouette_scores:
                # Sort by date
                combined = list(zip(model_dates, silhouette_scores, training_sizes))
                combined.sort(key=lambda x: x[0])
                model_dates, silhouette_scores, training_sizes = zip(*combined)

                col_perf, col_data = st.columns(2)

                with col_perf:
                    # Performance over time chart
                    fig_perf = px.line(
                        x=model_dates,
                        y=silhouette_scores,
                        title="Model Quality Over Time",
                        labels={'x': 'Training Date', 'y': 'Silhouette Score'},
                        markers=True
                    )
                    fig_perf.add_hline(y=0.5, line_dash="dash", line_color="orange",
                                      annotation_text="Good Threshold")
                    fig_perf.update_layout(height=300)
                    st.plotly_chart(fig_perf, use_container_width=True)

                with col_data:
                    # Training data size over time
                    fig_data = px.line(
                        x=model_dates,
                        y=training_sizes,
                        title="Training Data Growth",
                        labels={'x': 'Training Date', 'y': 'Number of Workouts'},
                        markers=True,
                        color_discrete_sequence=['green']
                    )
                    fig_data.update_layout(height=300)
                    st.plotly_chart(fig_data, use_container_width=True)


def render_training_controls():
    """Render model training and retraining controls."""
    st.header("🔧 Model Training Controls")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        **Training Options:**
        - **Retrain Model**: Creates new model using all current historical data
        - **Force Retrain**: Overwrites existing model even if recently trained
        - Models are automatically versioned and archived
        """)

    with col2:
        if st.button("🔄 Retrain Model", type="primary", use_container_width=True):
            st.session_state['trigger_training'] = True

        if st.button("⚠️ Force Retrain", use_container_width=True):
            st.session_state['trigger_force_training'] = True

    # Handle training triggers
    if st.session_state.get('trigger_training'):
        _handle_model_training(force=False)
        st.session_state['trigger_training'] = False

    if st.session_state.get('trigger_force_training'):
        _handle_model_training(force=True)
        st.session_state['trigger_force_training'] = False


def _handle_model_training(force: bool = False):
    """Handle model training with progress tracking."""
    with st.spinner("🔄 Training model on full historical dataset..."):
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Update progress
        progress_bar.progress(0.1)
        status_text.text("Loading historical workout data...")

        # Trigger training
        training_result = model_manager.train_new_model(force_retrain=force)

        progress_bar.progress(0.8)
        status_text.text("Evaluating model performance...")

        progress_bar.progress(1.0)
        status_text.text("Training complete!")

        # Show results
        if training_result['success']:
            st.success("✅ Model training successful!")

            model_summary = training_result['model_summary']
            training_info = training_result['training_data_info']
            performance = training_result['performance_metrics']

            # Display training results
            result_col1, result_col2 = st.columns(2)

            with result_col1:
                st.metric("Training Workouts", f"{training_info['total_workouts']:,}")
                st.metric("Quality Rating", model_summary['quality_rating'])

            with result_col2:
                st.metric("Training Span", f"{training_info['date_range']['span_days']} days")
                st.metric("Silhouette Score", f"{performance['silhouette_score']:.3f}")

            st.info("🔄 Page will refresh to show new model...")
            st.rerun()

        else:
            st.error(f"❌ Training failed: {training_result['message']}")
            if 'error' in training_result:
                with st.expander("Error Details"):
                    st.code(training_result['error'])


def render_model_testing_interface():
    """Render interface for testing model classifications."""
    st.header("🧪 Test Model Classifications")

    st.markdown("Test how the current model would classify workouts with different characteristics:")

    col1, col2, col3 = st.columns(3)

    with col1:
        test_pace = st.slider("Pace (min/mile)", 5.0, 30.0, 10.0, 0.1)

    with col2:
        test_distance = st.slider("Distance (miles)", 0.1, 20.0, 3.0, 0.1)

    with col3:
        test_duration = st.slider("Duration (minutes)", 5, 180, 30, 1)

    if st.button("🔍 Classify Test Workout"):
        # Create test workout DataFrame
        test_workout = pd.DataFrame({
            'workout_date': [datetime.now()],
            'avg_pace': [test_pace],
            'distance_mi': [test_distance],
            'duration_sec': [test_duration * 60],
            'duration_min': [test_duration]
        })

        # Get classification
        classified = model_manager.classify_workouts(test_workout)

        if not classified.empty:
            prediction = classified.iloc[0]['predicted_activity_type']
            confidence = classified.iloc[0]['classification_confidence']
            method = classified.iloc[0].get('classification_method', 'unknown')

            activity_config = ACTIVITY_TYPE_CONFIG.get(prediction, {})
            emoji = activity_config.get('emoji', '❓')
            display_name = activity_config.get('display_name', prediction.replace('_', ' ').title())

            st.success(f"**Classification:** {emoji} {display_name}")
            st.info(f"**Confidence:** {confidence:.3f} | **Method:** {method}")

            # Show reasoning
            with st.expander("🔍 Classification Reasoning"):
                st.write("**Test workout characteristics:**")
                st.write(f"• Pace: {test_pace:.1f} min/mile")
                st.write(f"• Distance: {test_distance:.1f} miles")
                st.write(f"• Duration: {test_duration} minutes")

                st.write(f"\n**Model's decision:**")
                st.write(f"• Classified as: {display_name}")
                st.write(f"• Confidence: {confidence:.1%}")
                st.write(f"• Method: {method}")


def main():
    """Main model management page function."""
    render_model_management_header()

    # Get current model status
    model_stats = render_model_status_overview()

    if model_stats and model_stats['model_available']:
        # Model available - show full management interface

        st.markdown("---")
        render_activity_type_breakdown(model_stats)

        st.markdown("---")
        render_model_performance_charts(model_stats)

        st.markdown("---")
        render_model_testing_interface()

        st.markdown("---")
        render_model_history()

    st.markdown("---")
    render_training_controls()

    # Footer with technical info
    st.markdown("---")
    with st.expander("ℹ️ Technical Information"):
        st.markdown("""
        **Model Architecture:**
        - Algorithm: K-means clustering (3 clusters)
        - Features: Pace, distance, duration
        - Training: Full historical dataset
        - Fallback: Era-based classification (pre/post Choco Effect)

        **Performance Metrics:**
        - Silhouette Score: Measures cluster separation quality
        - Confidence: Distance from cluster center (normalized)
        - Quality Rating: Human-readable assessment of model performance
        """)


if __name__ == "__main__":
    main()