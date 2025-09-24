"""Application configuration management."""

import os
import toml
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class AppConfig:
    """Application configuration manager."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "pyproject.toml"
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from pyproject.toml."""
        try:
            with open(self.config_file, "r") as f:
                return toml.load(f)
        except FileNotFoundError:
            return {}
    
    @property
    def input_filename(self) -> str:
        """Get input CSV filename from project config."""
        return self._config.get("tool", {}).get("project", {}).get("input_filename", "user2632022_workout_history.csv")
    
    @property
    def debug_mode(self) -> bool:
        """Get debug mode setting."""
        return self._config.get("tool", {}).get("project", {}).get("debug", False)
    
    @property
    def app_name(self) -> str:
        """Get application name."""
        return self._config.get("tool", {}).get("poetry", {}).get("name", "Fitness Dashboard")
    
    @property
    def version(self) -> str:
        """Get application version."""
        return self._config.get("tool", {}).get("poetry", {}).get("version", "0.1.0")
    
    @property
    def description(self) -> str:
        """Get application description."""
        return self._config.get("tool", {}).get("poetry", {}).get("description", "")

    @property
    def choco_effect_date(self) -> datetime:
        """
        Get the Choco Effect transition date from configuration.

        The Choco Effect represents a significant behavioral change in workout patterns,
        marking the transition from a primarily running-focused period to a walking/
        dog-walking focused period. This date is used throughout the application for:

        - Default workout classification (runs before, walks after)
        - Behavioral analysis and trend detection
        - Era-based performance comparisons
        - Historical context for fitness insights

        Business Logic:
        - Pre-Choco Era: Default classification = "real_run" (running-focused period)
        - Post-Choco Era: Default classification = "pup_walk" (walking/dog-walking period)
        - This reflects the user's actual behavioral transition around getting a dog

        Returns:
            datetime: The configured Choco Effect date, defaults to June 1, 2018

        Configuration:
            Set in pyproject.toml under [tool.project.business_dates]:
            choco_effect_date = "2018-06-01"
        """
        default_date = "2018-06-01"
        date_str = self._config.get("tool", {}).get("project", {}).get(
            "business_dates", {}
        ).get("choco_effect_date", default_date)

        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            # Fallback to default if configuration is invalid
            return datetime.strptime(default_date, "%Y-%m-%d")


# Style configuration
STYLE_CONFIG = {
    "colors": {
        "distance": "#5DADE2",
        "duration": "#28B463", 
        "calories": "#E74C3C",
        "speed": "#F39C12"
    },
    "font": {
        "heading": "Arial",
        "data_label": "Roboto"
    },
    "layout": {
        "background": "#FFFFFF",
        "padding": "10px",
        "margin": "5px"
    },
    "metric_container": {
        "background": "#FFFFFF",
        "padding": "10px",
        "margin": "5px"
    }
}

# Streamlit page configuration
STREAMLIT_CONFIG = {
    "page_title": "Fitness Dashboard",
    "page_icon": ":material/dashboard:",
    "layout": "wide",
    "menu_items": {
        "Get help": "https://www.streamlit.io/",
        "Report a bug": "mailto:dagny099@gmail.com"
    }
}

# Business Logic Constants
# These constants define key behavioral and classification rules used throughout the application

# Workout Classification Defaults
# Used when machine learning classification fails or insufficient data exists
CLASSIFICATION_DEFAULTS = {
    # Pre-Choco Era: Running-focused period, default to running classification
    "pre_choco_era_default": "real_run",

    # Post-Choco Era: Walking/dog-walking focused period, default to walking classification
    "post_choco_era_default": "pup_walk",

    # Minimum workouts required for ML clustering to be reliable
    "min_workouts_for_ml_classification": 5,

    # Classification confidence threshold for accepting ML predictions
    "min_confidence_threshold": 0.3
}

# Activity Type Definitions
# These define the possible workout classifications and their characteristics
ACTIVITY_TYPE_CONFIG = {
    "real_run": {
        "display_name": "Real Run",
        "emoji": "🏃‍♂️",
        "description": "Fast-paced running workout",
        "typical_pace_range": (6.0, 12.0),  # min/mile
        "typical_distance_range": (1.0, 26.2),  # miles
        "color": "#1f77b4"
    },
    "pup_walk": {
        "display_name": "Pup Walk",
        "emoji": "🐕",
        "description": "Leisurely walking/dog walking",
        "typical_pace_range": (15.0, 30.0),  # min/mile
        "typical_distance_range": (0.5, 5.0),  # miles
        "color": "#2ca02c"
    },
    "mixed": {
        "display_name": "Mixed Activity",
        "emoji": "🚶‍♂️",
        "description": "Combined running and walking",
        "typical_pace_range": (10.0, 20.0),  # min/mile
        "typical_distance_range": (0.5, 15.0),  # miles
        "color": "#ff7f0e"
    },
    "outlier": {
        "display_name": "Unusual Pattern",
        "emoji": "🤔",
        "description": "Outside normal workout patterns",
        "typical_pace_range": None,  # No typical range for outliers
        "typical_distance_range": None,
        "color": "#d62728"
    },
    "unknown": {
        "display_name": "Unknown",
        "emoji": "❓",
        "description": "Could not classify",
        "typical_pace_range": None,
        "typical_distance_range": None,
        "color": "#7f7f7f"
    }
}

# Global instance for easy access
app_config = AppConfig()