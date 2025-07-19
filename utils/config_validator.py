"""
Configuration Validator for BharatVerse Cloud Deployment
Loads and validates API keys, credentials, and environment variables

Module: config_validator.py  
Purpose: Centralized configuration management and validation
"""

import streamlit as st
import os
from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigSource(Enum):
    """Configuration source types"""
    STREAMLIT_SECRETS = "streamlit_secrets"
    ENVIRONMENT = "environment"
    FILE = "file"

@dataclass
class ConfigRequirement:
    """Defines a required configuration parameter"""
    key: str
    section: Optional[str] = None
    required: bool = True
    default_value: Any = None
    validation_func: Optional[callable] = None
    description: str = ""

class ConfigValidator:
    """
    Centralized configuration validator for BharatVerse cloud deployment
    
    Handles loading and validation of:
    - API keys and tokens
    - Database connection strings
    - Service endpoints
    - Feature flags
    """
    
    def __init__(self):
        self.config_cache = {}
        self.validation_results = {}
        
        # Define required configurations
        self.requirements = {
            # Database configurations
            "postgres_host": ConfigRequirement(
                key="host",
                section="postgres",
                required=True,
                validation_func=self._validate_hostname,
                description="Supabase PostgreSQL host"
            ),
            "postgres_password": ConfigRequirement(
                key="password", 
                section="postgres",
                required=True,
                description="Supabase PostgreSQL password"
            ),
            
            # Redis configurations
            "redis_url": ConfigRequirement(
                key="url",
                section="redis", 
                required=True,
                validation_func=self._validate_redis_url,
                description="Upstash Redis connection URL"
            ),
            
            # R2 Storage configurations
            "r2_endpoint": ConfigRequirement(
                key="endpoint_url",
                section="r2",
                required=True,
                validation_func=self._validate_url,
                description="Cloudflare R2 endpoint URL"
            ),
            "r2_access_key": ConfigRequirement(
                key="aws_access_key_id",
                section="r2",
                required=True,
                description="Cloudflare R2 access key"
            ),
            "r2_secret_key": ConfigRequirement(
                key="aws_secret_access_key",
                section="r2", 
                required=True,
                description="Cloudflare R2 secret key"
            ),
            "r2_bucket": ConfigRequirement(
                key="bucket_name",
                section="r2",
                required=True,
                description="Cloudflare R2 bucket name"
            ),
            
            # AI Inference configurations
            "huggingface_token": ConfigRequirement(
                key="huggingface_token",
                section="inference",
                required=True,
                validation_func=self._validate_hf_token,
                description="HuggingFace API token"
            ),
            
            # Authentication configurations
            "auth_secret": ConfigRequirement(
                key="secret_key",
                section="auth",
                required=False,
                default_value="dev-secret-key",
                description="Authentication secret key"
            ),
            
            # App configurations
            "app_environment": ConfigRequirement(
                key="environment",
                section="app",
                required=False,
                default_value="production",
                description="Application environment"
            )
        }
    
    def validate_all_configs(self) -> Dict[str, Any]:
        """
        Validate all required configurations
        
        Returns:
            Dict with validation results and loaded configs
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "configs": {},
            "source": None
        }
        
        # Try to load from Streamlit secrets first
        try:
            if hasattr(st, 'secrets') and st.secrets:
                results["source"] = ConfigSource.STREAMLIT_SECRETS
                results["configs"] = self._load_from_streamlit_secrets()
            else:
                # Fallback to environment variables
                results["source"] = ConfigSource.ENVIRONMENT  
                results["configs"] = self._load_from_environment()
                
        except Exception as e:
            results["valid"] = False
            results["errors"].append(f"Failed to load configurations: {str(e)}")
            return results
        
        # Validate each requirement
        for req_name, requirement in self.requirements.items():
            try:
                value = self._get_config_value(results["configs"], requirement)
                
                if value is None and requirement.required:
                    results["valid"] = False
                    results["errors"].append(
                        f"Missing required config: {requirement.section}.{requirement.key}"
                    )
                    continue
                
                if value is None and not requirement.required:
                    value = requirement.default_value
                    results["warnings"].append(
                        f"Using default value for {requirement.section}.{requirement.key}"
                    )
                
                # Run validation function if provided
                if requirement.validation_func and value:
                    if not requirement.validation_func(value):
                        results["valid"] = False
                        results["errors"].append(
                            f"Invalid value for {requirement.section}.{requirement.key}"
                        )
                        continue
                
                # Store validated config
                if requirement.section not in results["configs"]:
                    results["configs"][requirement.section] = {}
                results["configs"][requirement.section][requirement.key] = value
                
            except Exception as e:
                results["valid"] = False
                results["errors"].append(
                    f"Error validating {req_name}: {str(e)}"
                )
        
        self.validation_results = results
        return results
    
    def _load_from_streamlit_secrets(self) -> Dict[str, Any]:
        """Load configuration from Streamlit secrets"""
        configs = {}
        
        for section_name in ["postgres", "redis", "r2", "inference", "auth", "app"]:
            if hasattr(st.secrets, section_name):
                configs[section_name] = dict(st.secrets[section_name])
        
        return configs
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        configs = {
            "postgres": {
                "host": os.getenv("POSTGRES_HOST"),
                "port": os.getenv("POSTGRES_PORT", "5432"),
                "database": os.getenv("POSTGRES_DB", "postgres"),
                "user": os.getenv("POSTGRES_USER", "postgres"),
                "password": os.getenv("POSTGRES_PASSWORD")
            },
            "redis": {
                "url": os.getenv("REDIS_URL")
            },
            "r2": {
                "endpoint_url": os.getenv("R2_ENDPOINT_URL"),
                "aws_access_key_id": os.getenv("R2_ACCESS_KEY_ID"),
                "aws_secret_access_key": os.getenv("R2_SECRET_ACCESS_KEY"),
                "bucket_name": os.getenv("R2_BUCKET_NAME")
            },
            "inference": {
                "huggingface_token": os.getenv("HUGGINGFACE_TOKEN"),
                "whisper_api": os.getenv("WHISPER_API", "https://api-inference.huggingface.co/models/openai/whisper-large-v3"),
                "text_analysis_api": os.getenv("TEXT_ANALYSIS_API", "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"),
                "image_analysis_api": os.getenv("IMAGE_ANALYSIS_API", "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"),
                "translation_api": os.getenv("TRANSLATION_API", "https://api-inference.huggingface.co/models/facebook/nllb-200-distilled-600M")
            },
            "auth": {
                "secret_key": os.getenv("AUTH_SECRET_KEY", "dev-secret-key")
            },
            "app": {
                "environment": os.getenv("APP_ENVIRONMENT", "production")
            }
        }
        
        return configs
    
    def _get_config_value(self, configs: Dict, requirement: ConfigRequirement) -> Any:
        """Get configuration value from loaded configs"""
        if requirement.section in configs:
            return configs[requirement.section].get(requirement.key)
        return None
    
    def _validate_hostname(self, value: str) -> bool:
        """Validate hostname format"""
        return isinstance(value, str) and len(value) > 0 and "." in value
    
    def _validate_url(self, value: str) -> bool:
        """Validate URL format"""
        return isinstance(value, str) and (value.startswith("https://") or value.startswith("http://"))
    
    def _validate_redis_url(self, value: str) -> bool:
        """Validate Redis URL format"""
        return isinstance(value, str) and value.startswith("redis://")
    
    def _validate_hf_token(self, value: str) -> bool:
        """Validate HuggingFace token format"""
        return isinstance(value, str) and value.startswith("hf_") and len(value) > 10
    
    def get_config(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a specific configuration value
        
        Args:
            section: Configuration section name
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        if not self.validation_results:
            self.validate_all_configs()
        
        configs = self.validation_results.get("configs", {})
        return configs.get(section, {}).get(key, default)
    
    def is_valid(self) -> bool:
        """Check if all configurations are valid"""
        if not self.validation_results:
            self.validate_all_configs()
        
        return self.validation_results.get("valid", False)
    
    def get_validation_report(self) -> str:
        """Get a formatted validation report"""
        if not self.validation_results:
            self.validate_all_configs()
        
        results = self.validation_results
        report = []
        
        report.append("🔧 Configuration Validation Report")
        report.append("=" * 40)
        report.append(f"Status: {'✅ VALID' if results['valid'] else '❌ INVALID'}")
        report.append(f"Source: {results['source'].value if results['source'] else 'Unknown'}")
        report.append("")
        
        if results['errors']:
            report.append("❌ Errors:")
            for error in results['errors']:
                report.append(f"  • {error}")
            report.append("")
        
        if results['warnings']:
            report.append("⚠️ Warnings:")
            for warning in results['warnings']:
                report.append(f"  • {warning}")
            report.append("")
        
        # Show loaded configurations (without secrets)
        report.append("📋 Loaded Configurations:")
        for section, configs in results['configs'].items():
            report.append(f"  [{section}]")
            for key, value in configs.items():
                if 'password' in key.lower() or 'secret' in key.lower() or 'token' in key.lower():
                    masked_value = f"{str(value)[:8]}..." if value else "None"
                    report.append(f"    {key} = {masked_value}")
                else:
                    report.append(f"    {key} = {value}")
        
        return "\n".join(report)

# Global validator instance
_validator = None

def get_config_validator() -> ConfigValidator:
    """Get the global configuration validator instance"""
    global _validator
    if _validator is None:
        _validator = ConfigValidator()
    return _validator

def validate_deployment_config() -> Dict[str, Any]:
    """Convenience function to validate deployment configuration"""
    validator = get_config_validator()
    return validator.validate_all_configs()

def get_config(section: str, key: str, default: Any = None) -> Any:
    """Convenience function to get configuration value"""
    validator = get_config_validator()
    return validator.get_config(section, key, default)