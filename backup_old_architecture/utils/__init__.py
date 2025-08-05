# Utils package for BharatVerse
# Contains performance optimization and utility modules

# Safe imports to avoid circular dependencies
def get_performance_optimizer():
    """Lazy import to avoid circular dependencies"""
    try:
        from .performance_optimizer import get_performance_optimizer as _get_optimizer
        return _get_optimizer()
    except ImportError as e:
        import logging
        logging.warning(f"Performance optimizer not available: {e}")
        return None

def get_cache_manager():
    """Lazy import for cache manager"""
    try:
        from .redis_cache import get_cache_manager as _get_cache
        return _get_cache()
    except ImportError as e:
        import logging
        logging.warning(f"Cache manager not available: {e}")
        return None

# Safe memory manager import
def get_memory_manager():
    """Lazy import for memory manager"""
    try:
        from .memory_manager import get_memory_manager as _get_memory
        return _get_memory()
    except ImportError:
        try:
            from .fallback_memory import get_fallback_memory_manager
            return get_fallback_memory_manager()
        except ImportError as e:
            import logging
            logging.warning(f"Memory manager not available: {e}")
            return None

__all__ = [
    'get_performance_optimizer',
    'get_memory_manager', 
    'get_cache_manager'
]