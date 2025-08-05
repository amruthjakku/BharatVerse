"""
Centralized Configuration Manager for BharatVerse
Replaces scattered configuration and environment detection logic
"""

import os
import streamlit as st
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class AppConfig:
    """Application configuration"""
    # Environment
    environment: str = "development"
    debug: bool = False
    
    # API settings
    api_url: str = "http://localhost:8000"
    
    # Audio settings
    supported_audio_formats: List[str] = None
    max_audio_file_size_mb: int = 50
    audio_sample_rate: int = 16000
    audio_channels: int = 1
    
    # AI settings
    ai_mode: str = "cloud"
    processing_timeout: int = 300
    
    # Storage settings
    max_file_size_mb: int = 100
    
    # UI settings
    page_title: str = "BharatVerse - Cultural Heritage Platform"
    page_icon: str = "🏛️"
    
    def __post_init__(self):
        if self.supported_audio_formats is None:
            self.supported_audio_formats = ['.wav', '.mp3', '.m4a', '.ogg', '.flac']

class ConfigManager:
    """Centralized configuration management"""
    
    def __init__(self):
        self._config = AppConfig()
        self._load_from_environment()
        self._detect_environment()
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        # Environment detection
        self._config.environment = os.getenv("ENVIRONMENT", "development")
        self._config.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # API settings
        self._config.api_url = os.getenv("API_URL", self._config.api_url)
        
        # AI settings
        self._config.ai_mode = os.getenv("AI_MODE", self._config.ai_mode)
        
        # File size limits
        try:
            self._config.max_audio_file_size_mb = int(os.getenv("MAX_AUDIO_FILE_SIZE_MB", "50"))
            self._config.max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
        except ValueError:
            logger.warning("Invalid file size configuration, using defaults")
        
        # Timeouts
        try:
            self._config.processing_timeout = int(os.getenv("PROCESSING_TIMEOUT", "300"))
        except ValueError:
            logger.warning("Invalid timeout configuration, using default")
    
    def _detect_environment(self):
        """Detect the deployment environment"""
        # Cloud environment indicators
        cloud_indicators = [
            '/mount/src/',  # Streamlit Cloud
            '/app/',        # Heroku
            '/workspace/',  # GitHub Codespaces
            'STREAMLIT_CLOUD' in os.environ,
            'HEROKU' in os.environ,
            'CODESPACE_NAME' in os.environ,
            'RAILWAY_ENVIRONMENT' in os.environ,
        ]
        
        current_path = os.getcwd()
        is_cloud = any(
            indicator in current_path if isinstance(indicator, str) else indicator 
            for indicator in cloud_indicators
        )
        
        if is_cloud:
            self._config.environment = "cloud"
            logger.info("Cloud environment detected")
        
        # Local development detection
        if current_path.endswith("bharatverse") and os.path.exists("Home.py"):
            self._config.environment = "development"
            self._config.debug = True
            logger.info("Local development environment detected")
    
    @property
    def config(self) -> AppConfig:
        """Get the current configuration"""
        return self._config
    
    def is_cloud_environment(self) -> bool:
        """Check if running in cloud environment"""
        return self._config.environment == "cloud"
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self._config.environment == "development"
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self._config.environment == "production"
    
    def get_audio_config(self) -> Dict[str, Any]:
        """Get audio-specific configuration"""
        return {
            'supported_formats': self._config.supported_audio_formats,
            'max_file_size_mb': self._config.max_audio_file_size_mb,
            'sample_rate': self._config.audio_sample_rate,
            'channels': self._config.audio_channels,
            'processing_timeout': self._config.processing_timeout
        }
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI-specific configuration"""
        return {
            'page_title': self._config.page_title,
            'page_icon': self._config.page_icon,
            'layout': "wide",
            'initial_sidebar_state': "expanded"
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API-specific configuration"""
        return {
            'api_url': self._config.api_url,
            'timeout': self._config.processing_timeout
        }
    
    def update_config(self, **kwargs):
        """Update configuration values"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
                logger.info(f"Configuration updated: {key} = {value}")
            else:
                logger.warning(f"Unknown configuration key: {key}")
    
    def get_language_options(self) -> List[str]:
        """Get supported language options"""
        return [
            "Auto-detect", "Hindi", "Bengali", "Tamil", "Telugu", "Marathi", 
            "Gujarati", "Kannada", "Malayalam", "Punjabi", "Odia", "Assamese", 
            "Urdu", "Sanskrit", "English"
        ]
    
    def get_category_options(self) -> List[str]:
        """Get content category options"""
        return [
            "Folk Song", "Story", "Poetry", "Prayer", "Chant", "Lullaby", 
            "Historical Account", "Interview", "Speech", "Other"
        ]
    
    def get_region_options(self) -> List[str]:
        """Get region options"""
        return [
            "All Regions", "North India", "South India", "East India", "West India", 
            "Central India", "Northeast India", "Kashmir", "Punjab", "Rajasthan", 
            "Gujarat", "Maharashtra", "Karnataka", "Tamil Nadu", "Kerala", 
            "Andhra Pradesh", "Telangana", "West Bengal", "Odisha", "Assam", 
            "Bihar", "Uttar Pradesh", "Madhya Pradesh", "Jharkhand", "Chhattisgarh"
        ]
    
    def validate_file_size(self, file_size_bytes: int, file_type: str = "general") -> bool:
        """Validate file size against limits"""
        size_mb = file_size_bytes / (1024 * 1024)
        
        if file_type == "audio":
            return size_mb <= self._config.max_audio_file_size_mb
        else:
            return size_mb <= self._config.max_file_size_mb
    
    def get_file_size_limit(self, file_type: str = "general") -> int:
        """Get file size limit in MB"""
        if file_type == "audio":
            return self._config.max_audio_file_size_mb
        else:
            return self._config.max_file_size_mb

# Global configuration manager instance
_config_manager = None

@st.cache_resource
def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

# Convenience functions
def get_config() -> AppConfig:
    """Get the current configuration"""
    return get_config_manager().config

def is_cloud_environment() -> bool:
    """Check if running in cloud environment"""
    return get_config_manager().is_cloud_environment()

def is_development() -> bool:
    """Check if running in development mode"""
    return get_config_manager().is_development()

def get_audio_config() -> Dict[str, Any]:
    """Get audio configuration"""
    return get_config_manager().get_audio_config()

def get_ui_config() -> Dict[str, Any]:
    """Get UI configuration"""
    return get_config_manager().get_ui_config()

def get_language_options() -> List[str]:
    """Get language options"""
    return get_config_manager().get_language_options()

def get_category_options() -> List[str]:
    """Get category options"""
    return get_config_manager().get_category_options()

def get_region_options() -> List[str]:
    """Get region options"""
    return get_config_manager().get_region_options()