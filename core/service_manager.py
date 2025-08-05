"""
Centralized Service Manager for BharatVerse
Replaces the scattered *_AVAILABLE flags with a clean service registry
"""

import logging
from typing import Dict, Any, Optional, Type
from dataclasses import dataclass
from enum import Enum
from .module_loader import CommonModules, load_module, get_function, get_class

logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ERROR = "error"

@dataclass
class ServiceInfo:
    name: str
    status: ServiceStatus
    instance: Optional[Any] = None
    error_message: Optional[str] = None
    fallback_available: bool = False

class ServiceManager:
    """Centralized service management"""
    
    def __init__(self):
        self._services: Dict[str, ServiceInfo] = {}
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all services with proper error handling"""
        
        # Database services
        self._register_service("database", self._init_database)
        self._register_service("supabase", self._init_supabase)
        
        # Storage services
        self._register_service("storage", self._init_storage)
        self._register_service("minio", self._init_minio)
        
        # AI services
        self._register_service("ai", self._init_ai)
        self._register_service("cloud_ai", self._init_cloud_ai)
        
        # Cache services
        self._register_service("cache", self._init_cache)
        self._register_service("redis", self._init_redis)
        
        # Auth services
        self._register_service("auth", self._init_auth)
        
        # Audio services
        self._register_service("audio", self._init_audio)
        
        # Memory management
        self._register_service("memory", self._init_memory)
    
    def _register_service(self, name: str, init_func):
        """Register a service with its initialization function"""
        try:
            instance = init_func()
            self._services[name] = ServiceInfo(
                name=name,
                status=ServiceStatus.AVAILABLE,
                instance=instance
            )
            logger.info(f"Service '{name}' initialized successfully")
        except Exception as e:
            self._services[name] = ServiceInfo(
                name=name,
                status=ServiceStatus.ERROR,
                error_message=str(e)
            )
            logger.warning(f"Service '{name}' failed to initialize: {e}")
    
    def get_service(self, name: str) -> Optional[Any]:
        """Get a service instance if available"""
        service_info = self._services.get(name)
        if service_info and service_info.status == ServiceStatus.AVAILABLE:
            return service_info.instance
        return None
    
    def is_available(self, name: str) -> bool:
        """Check if a service is available"""
        service_info = self._services.get(name)
        return service_info and service_info.status == ServiceStatus.AVAILABLE
    
    def get_status(self, name: str) -> ServiceStatus:
        """Get service status"""
        service_info = self._services.get(name)
        return service_info.status if service_info else ServiceStatus.UNAVAILABLE
    
    def get_error(self, name: str) -> Optional[str]:
        """Get service error message"""
        service_info = self._services.get(name)
        return service_info.error_message if service_info else None
    
    def list_services(self) -> Dict[str, ServiceStatus]:
        """List all services and their status"""
        return {name: info.status for name, info in self._services.items()}
    
    # Service initialization methods
    def _init_database(self):
        """Initialize database service"""
        backend = CommonModules.load_database_backend()
        if backend["backend"] != "none":
            return backend["manager"]
        raise ImportError("No database backend available")
    
    def _init_supabase(self):
        """Initialize Supabase service"""
        get_manager = get_function("utils.supabase_db", "get_database_manager")
        if get_manager:
            return get_manager()
        raise ImportError("Supabase not available")
    
    def _init_storage(self):
        """Initialize storage service"""
        backend = CommonModules.load_storage_backend()
        if backend["backend"] != "none":
            return backend["manager"]
        raise ImportError("No storage backend available")
    
    def _init_minio(self):
        """Initialize MinIO service"""
        get_manager = get_function("utils.minio_storage", "get_storage_manager")
        if get_manager:
            return get_manager()
        raise ImportError("MinIO not available")
    
    def _init_ai(self):
        """Initialize AI service"""
        backend = CommonModules.load_ai_backend()
        if backend["backend"] != "none":
            return backend["manager"]
        raise ImportError("No AI backend available")
    
    def _init_cloud_ai(self):
        """Initialize Cloud AI service"""
        get_manager = get_function("core.cloud_ai_manager", "get_cloud_ai_manager")
        if get_manager:
            return get_manager()
        raise ImportError("Cloud AI not available")
    
    def _init_cache(self):
        """Initialize cache service"""
        get_manager = get_function("utils.redis_cache", "get_cache_manager")
        if get_manager:
            return get_manager()
        # Return a simple dict-based cache as fallback
        return {}
    
    def _init_redis(self):
        """Initialize Redis service"""
        get_manager = get_function("utils.redis_cache", "get_cache_manager")
        if get_manager:
            return get_manager()
        raise ImportError("Redis not available")
    
    def _init_auth(self):
        """Initialize authentication service"""
        get_manager = get_function("streamlit_app.utils.auth", "get_auth_manager")
        if get_manager:
            return get_manager()
        raise ImportError("Authentication not available")
    
    def _init_audio(self):
        """Initialize audio service"""
        backend = CommonModules.load_audio_backend()
        return backend  # Always return something, even if backend is "none"
    
    def _init_memory(self):
        """Initialize memory management service"""
        get_manager = get_function("utils.memory_manager", "get_memory_manager")
        if get_manager:
            return get_manager()
        
        # Try fallback
        get_fallback = get_function("utils.fallback_memory", "get_fallback_memory_manager")
        if get_fallback:
            return get_fallback()
        
        raise ImportError("No memory manager available")

# Global service manager instance
_service_manager = None

def get_service_manager() -> ServiceManager:
    """Get the global service manager instance"""
    global _service_manager
    if _service_manager is None:
        _service_manager = ServiceManager()
    return _service_manager

# Convenience functions
def get_service(name: str) -> Optional[Any]:
    """Get a service instance"""
    return get_service_manager().get_service(name)

def is_service_available(name: str) -> bool:
    """Check if a service is available"""
    return get_service_manager().is_available(name)

def require_service(name: str, error_message: str = None):
    """Require a service to be available, raise exception if not"""
    if not is_service_available(name):
        error_msg = error_message or f"Service '{name}' is required but not available"
        service_manager = get_service_manager()
        service_error = service_manager.get_error(name)
        if service_error:
            error_msg += f": {service_error}"
        raise RuntimeError(error_msg)
    return get_service(name)