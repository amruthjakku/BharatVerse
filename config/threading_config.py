"""
Threading Configuration for BharatVerse
Centralized configuration for multithreading settings
"""

import os
from typing import Dict, Any

class ThreadingConfig:
    """Configuration class for threading settings"""
    
    def __init__(self):
        """Initialize threading configuration from environment variables"""
        
        # Core threading settings
        self.MAX_WORKERS = int(os.getenv('MAX_THREAD_WORKERS', self._get_optimal_workers()))
        self.ASYNC_QUEUE_WORKERS = int(os.getenv('ASYNC_QUEUE_WORKERS', 4))
        
        # Task-specific worker limits
        self.AI_PROCESSING_WORKERS = int(os.getenv('AI_PROCESSING_WORKERS', min(4, self.MAX_WORKERS)))
        self.FILE_UPLOAD_WORKERS = int(os.getenv('FILE_UPLOAD_WORKERS', min(3, self.MAX_WORKERS)))
        self.DATABASE_WORKERS = int(os.getenv('DATABASE_WORKERS', min(5, self.MAX_WORKERS)))
        self.ANALYTICS_WORKERS = int(os.getenv('ANALYTICS_WORKERS', min(3, self.MAX_WORKERS)))
        
        # Timeout settings (in seconds)
        self.TASK_TIMEOUT = int(os.getenv('TASK_TIMEOUT', 300))  # 5 minutes
        self.AI_TASK_TIMEOUT = int(os.getenv('AI_TASK_TIMEOUT', 120))  # 2 minutes
        self.UPLOAD_TASK_TIMEOUT = int(os.getenv('UPLOAD_TASK_TIMEOUT', 180))  # 3 minutes
        self.DB_TASK_TIMEOUT = int(os.getenv('DB_TASK_TIMEOUT', 60))  # 1 minute
        
        # Batch processing settings
        self.BATCH_SIZE = int(os.getenv('BATCH_SIZE', 10))
        self.MAX_BATCH_WORKERS = int(os.getenv('MAX_BATCH_WORKERS', min(5, self.MAX_WORKERS)))
        
        # Performance settings
        self.ENABLE_TASK_MONITORING = os.getenv('ENABLE_TASK_MONITORING', 'true').lower() == 'true'
        self.ENABLE_PERFORMANCE_LOGGING = os.getenv('ENABLE_PERFORMANCE_LOGGING', 'true').lower() == 'true'
        self.METRICS_RETENTION_HOURS = int(os.getenv('METRICS_RETENTION_HOURS', 24))
        
        # Safety settings
        self.MAX_MEMORY_PER_TASK_MB = int(os.getenv('MAX_MEMORY_PER_TASK_MB', 100))
        self.ENABLE_MEMORY_MONITORING = os.getenv('ENABLE_MEMORY_MONITORING', 'true').lower() == 'true'
        self.AUTO_CLEANUP_FAILED_TASKS = os.getenv('AUTO_CLEANUP_FAILED_TASKS', 'true').lower() == 'true'
        
        # Development settings
        self.DEBUG_THREADING = os.getenv('DEBUG_THREADING', 'false').lower() == 'true'
        self.ENABLE_THREAD_PROFILING = os.getenv('ENABLE_THREAD_PROFILING', 'false').lower() == 'true'
    
    def _get_optimal_workers(self) -> int:
        """Calculate optimal number of workers based on system resources"""
        import os
        cpu_count = os.cpu_count() or 1
        
        # Conservative approach: CPU count + 4, but cap at 32
        optimal = min(32, cpu_count + 4)
        
        # Adjust based on available memory (rough estimate)
        try:
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            
            # Reduce workers if low memory
            if memory_gb < 2:
                optimal = min(optimal, 4)
            elif memory_gb < 4:
                optimal = min(optimal, 8)
            elif memory_gb < 8:
                optimal = min(optimal, 16)
        except ImportError:
            pass  # psutil not available, use CPU-based calculation
        
        return optimal
    
    def get_worker_config(self, task_type: str) -> Dict[str, Any]:
        """Get worker configuration for specific task type"""
        configs = {
            'ai_processing': {
                'max_workers': self.AI_PROCESSING_WORKERS,
                'timeout': self.AI_TASK_TIMEOUT,
                'memory_limit_mb': self.MAX_MEMORY_PER_TASK_MB * 2  # AI tasks need more memory
            },
            'file_upload': {
                'max_workers': self.FILE_UPLOAD_WORKERS,
                'timeout': self.UPLOAD_TASK_TIMEOUT,
                'memory_limit_mb': self.MAX_MEMORY_PER_TASK_MB
            },
            'database': {
                'max_workers': self.DATABASE_WORKERS,
                'timeout': self.DB_TASK_TIMEOUT,
                'memory_limit_mb': self.MAX_MEMORY_PER_TASK_MB // 2  # DB tasks are lightweight
            },
            'analytics': {
                'max_workers': self.ANALYTICS_WORKERS,
                'timeout': self.TASK_TIMEOUT,
                'memory_limit_mb': self.MAX_MEMORY_PER_TASK_MB
            },
            'general': {
                'max_workers': self.MAX_WORKERS,
                'timeout': self.TASK_TIMEOUT,
                'memory_limit_mb': self.MAX_MEMORY_PER_TASK_MB
            }
        }
        
        return configs.get(task_type, configs['general'])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'max_workers': self.MAX_WORKERS,
            'async_queue_workers': self.ASYNC_QUEUE_WORKERS,
            'ai_processing_workers': self.AI_PROCESSING_WORKERS,
            'file_upload_workers': self.FILE_UPLOAD_WORKERS,
            'database_workers': self.DATABASE_WORKERS,
            'analytics_workers': self.ANALYTICS_WORKERS,
            'task_timeout': self.TASK_TIMEOUT,
            'ai_task_timeout': self.AI_TASK_TIMEOUT,
            'upload_task_timeout': self.UPLOAD_TASK_TIMEOUT,
            'db_task_timeout': self.DB_TASK_TIMEOUT,
            'batch_size': self.BATCH_SIZE,
            'max_batch_workers': self.MAX_BATCH_WORKERS,
            'enable_task_monitoring': self.ENABLE_TASK_MONITORING,
            'enable_performance_logging': self.ENABLE_PERFORMANCE_LOGGING,
            'metrics_retention_hours': self.METRICS_RETENTION_HOURS,
            'max_memory_per_task_mb': self.MAX_MEMORY_PER_TASK_MB,
            'enable_memory_monitoring': self.ENABLE_MEMORY_MONITORING,
            'auto_cleanup_failed_tasks': self.AUTO_CLEANUP_FAILED_TASKS,
            'debug_threading': self.DEBUG_THREADING,
            'enable_thread_profiling': self.ENABLE_THREAD_PROFILING
        }
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        issues = []
        
        if self.MAX_WORKERS < 1:
            issues.append("MAX_WORKERS must be at least 1")
        
        if self.MAX_WORKERS > 100:
            issues.append("MAX_WORKERS should not exceed 100 for stability")
        
        if self.TASK_TIMEOUT < 10:
            issues.append("TASK_TIMEOUT should be at least 10 seconds")
        
        if self.BATCH_SIZE < 1:
            issues.append("BATCH_SIZE must be at least 1")
        
        if self.MAX_MEMORY_PER_TASK_MB < 10:
            issues.append("MAX_MEMORY_PER_TASK_MB should be at least 10MB")
        
        if issues:
            print("Threading configuration issues:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        
        return True

# Global configuration instance
_threading_config = None

def get_threading_config() -> ThreadingConfig:
    """Get the global threading configuration instance"""
    global _threading_config
    if _threading_config is None:
        _threading_config = ThreadingConfig()
        if not _threading_config.validate():
            print("Warning: Threading configuration has issues, using defaults")
    return _threading_config

# Environment-specific configurations
DEVELOPMENT_CONFIG = {
    'MAX_THREAD_WORKERS': '4',
    'AI_PROCESSING_WORKERS': '2',
    'FILE_UPLOAD_WORKERS': '2',
    'DATABASE_WORKERS': '3',
    'ANALYTICS_WORKERS': '2',
    'TASK_TIMEOUT': '120',
    'DEBUG_THREADING': 'true',
    'ENABLE_THREAD_PROFILING': 'true'
}

PRODUCTION_CONFIG = {
    'MAX_THREAD_WORKERS': '16',
    'AI_PROCESSING_WORKERS': '6',
    'FILE_UPLOAD_WORKERS': '4',
    'DATABASE_WORKERS': '8',
    'ANALYTICS_WORKERS': '4',
    'TASK_TIMEOUT': '300',
    'DEBUG_THREADING': 'false',
    'ENABLE_THREAD_PROFILING': 'false',
    'ENABLE_PERFORMANCE_LOGGING': 'true'
}

CLOUD_CONFIG = {
    'MAX_THREAD_WORKERS': '8',
    'AI_PROCESSING_WORKERS': '3',
    'FILE_UPLOAD_WORKERS': '2',
    'DATABASE_WORKERS': '4',
    'ANALYTICS_WORKERS': '2',
    'TASK_TIMEOUT': '180',
    'MAX_MEMORY_PER_TASK_MB': '50',  # Lower memory limits for cloud
    'DEBUG_THREADING': 'false',
    'ENABLE_PERFORMANCE_LOGGING': 'true'
}

def apply_environment_config(env: str = None):
    """Apply environment-specific configuration"""
    if env is None:
        env = os.getenv('APP_ENV', 'development')
    
    config_map = {
        'development': DEVELOPMENT_CONFIG,
        'production': PRODUCTION_CONFIG,
        'cloud': CLOUD_CONFIG,
        'streamlit': CLOUD_CONFIG  # Streamlit Cloud uses cloud config
    }
    
    config = config_map.get(env, DEVELOPMENT_CONFIG)
    
    # Apply configuration to environment
    for key, value in config.items():
        if key not in os.environ:  # Don't override existing env vars
            os.environ[key] = value
    
    print(f"Applied {env} threading configuration")

# Auto-apply configuration based on environment
if __name__ != "__main__":
    apply_environment_config()