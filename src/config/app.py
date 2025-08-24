"""Application configuration management."""

import os
import toml
from typing import Dict, Any, Optional
from pathlib import Path


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