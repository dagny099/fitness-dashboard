"""Database configuration management."""

import os
import platform
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Database configuration class."""
    
    host: str
    port: int
    username: str
    password: str
    database: str
    
    @classmethod
    def from_environment(cls) -> 'DatabaseConfig':
        """Create database configuration from environment variables."""
        env = cls._determine_environment()
        
        if env == "development":
            return cls(
                host="localhost",
                port=3306,
                username=os.environ.get("MYSQL_USER", ""),
                password=os.environ.get("MYSQL_PWD", ""),
                database="sweat"
            )
        else:  # production
            return cls(
                host=os.environ.get("RDS_ENDPOINT", ""),
                port=3306,
                username=os.environ.get("RDS_USER", ""),
                password=os.environ.get("RDS_PASSWORD", ""),
                database="sweat"
            )
    
    @staticmethod
    def _determine_environment() -> str:
        """Determine if running in development or production."""
        return "development" if platform.system() == "Darwin" else "production"
    
    def to_dict(self, include_password: bool = True) -> Dict[str, str]:
        """Convert to dictionary format."""
        config_dict = {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "database": self.database
        }
        
        if include_password:
            config_dict["password"] = self.password
            
        return config_dict
    
    def validate(self) -> bool:
        """Validate that all required configuration values are present."""
        required_fields = [self.host, self.username, self.password, self.database]
        return all(field for field in required_fields)


# Table schema configuration
TABLE_SCHEMA = {
    "workout_summary": """
        CREATE TABLE IF NOT EXISTS workout_summary (
            workout_id VARCHAR(20) PRIMARY KEY,
            workout_date DATETIME,
            activity_type VARCHAR(50),
            kcal_burned BIGINT,
            distance_mi FLOAT,
            duration_sec FLOAT,
            avg_pace FLOAT,
            max_pace FLOAT,
            steps BIGINT,
            link VARCHAR(100) 
        )
    """
}