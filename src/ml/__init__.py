"""
ML package for fitness dashboard classification system.

This package provides complete machine learning model lifecycle management
for workout classification, replacing the ad-hoc training approach with
a proper, persistent ML architecture.
"""

from .model_manager import ModelManager, WorkoutClassificationModel, model_manager

__all__ = ['ModelManager', 'WorkoutClassificationModel', 'model_manager']