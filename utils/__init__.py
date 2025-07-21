# Utils package for BharatVerse
# Contains performance optimization and utility modules

from .performance_optimizer import get_performance_optimizer
from .redis_cache import get_cache_manager

# Safe memory manager import
try:
    from .memory_manager import get_memory_manager
    MEMORY_MANAGER_AVAILABLE = True
except ImportError:
    from .fallback_memory import get_fallback_memory_manager as get_memory_manager
    MEMORY_MANAGER_AVAILABLE = False

__all__ = [
    'get_performance_optimizer',
    'get_memory_manager', 
    'get_cache_manager'
]