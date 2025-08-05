"""
Clean Module Loader for BharatVerse
Replaces scattered import logic with a centralized module loading system
"""

import importlib
import logging
from typing import Optional, Any, Dict, Callable
from functools import wraps

logger = logging.getLogger(__name__)

class ModuleLoader:
    """Centralized module loading with fallback support"""
    
    def __init__(self):
        self._loaded_modules: Dict[str, Any] = {}
        self._failed_modules: Dict[str, str] = {}
    
    def load_module(self, module_name: str, fallback_module: str = None) -> Optional[Any]:
        """
        Load a module with optional fallback
        
        Args:
            module_name: Primary module to load
            fallback_module: Fallback module if primary fails
            
        Returns:
            Loaded module or None if both fail
        """
        # Check if already loaded
        if module_name in self._loaded_modules:
            return self._loaded_modules[module_name]
        
        # Check if already failed
        if module_name in self._failed_modules:
            logger.debug(f"Module {module_name} previously failed: {self._failed_modules[module_name]}")
            return None
        
        # Try to load primary module
        try:
            module = importlib.import_module(module_name)
            self._loaded_modules[module_name] = module
            logger.info(f"Successfully loaded module: {module_name}")
            return module
        except ImportError as e:
            logger.warning(f"Failed to load module {module_name}: {e}")
            self._failed_modules[module_name] = str(e)
        
        # Try fallback if provided
        if fallback_module:
            try:
                module = importlib.import_module(fallback_module)
                self._loaded_modules[module_name] = module  # Cache under primary name
                logger.info(f"Successfully loaded fallback module {fallback_module} for {module_name}")
                return module
            except ImportError as e:
                logger.warning(f"Failed to load fallback module {fallback_module}: {e}")
                self._failed_modules[module_name] += f", fallback: {e}"
        
        return None
    
    def get_function(self, module_name: str, function_name: str, fallback_module: str = None) -> Optional[Callable]:
        """
        Get a specific function from a module
        
        Args:
            module_name: Module containing the function
            function_name: Name of the function
            fallback_module: Fallback module if primary fails
            
        Returns:
            Function or None if not found
        """
        module = self.load_module(module_name, fallback_module)
        if module and hasattr(module, function_name):
            return getattr(module, function_name)
        return None
    
    def get_class(self, module_name: str, class_name: str, fallback_module: str = None) -> Optional[type]:
        """
        Get a specific class from a module
        
        Args:
            module_name: Module containing the class
            class_name: Name of the class
            fallback_module: Fallback module if primary fails
            
        Returns:
            Class or None if not found
        """
        module = self.load_module(module_name, fallback_module)
        if module and hasattr(module, class_name):
            return getattr(module, class_name)
        return None
    
    def is_module_available(self, module_name: str) -> bool:
        """Check if a module is available"""
        return module_name in self._loaded_modules or self._try_import(module_name)
    
    def _try_import(self, module_name: str) -> bool:
        """Try to import a module without caching"""
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False
    
    def get_failed_modules(self) -> Dict[str, str]:
        """Get list of failed module imports"""
        return self._failed_modules.copy()
    
    def clear_cache(self):
        """Clear the module cache"""
        self._loaded_modules.clear()
        self._failed_modules.clear()

# Global module loader instance
_module_loader = ModuleLoader()

def get_module_loader() -> ModuleLoader:
    """Get the global module loader instance"""
    return _module_loader

# Convenience functions
def load_module(module_name: str, fallback_module: str = None) -> Optional[Any]:
    """Load a module with optional fallback"""
    return _module_loader.load_module(module_name, fallback_module)

def get_function(module_name: str, function_name: str, fallback_module: str = None) -> Optional[Callable]:
    """Get a function from a module"""
    return _module_loader.get_function(module_name, function_name, fallback_module)

def get_class(module_name: str, class_name: str, fallback_module: str = None) -> Optional[type]:
    """Get a class from a module"""
    return _module_loader.get_class(module_name, class_name, fallback_module)

def is_module_available(module_name: str) -> bool:
    """Check if a module is available"""
    return _module_loader.is_module_available(module_name)

def require_module(module_name: str, error_message: str = None):
    """Require a module to be available, raise exception if not"""
    module = load_module(module_name)
    if module is None:
        error_msg = error_message or f"Required module '{module_name}' is not available"
        failed_modules = _module_loader.get_failed_modules()
        if module_name in failed_modules:
            error_msg += f": {failed_modules[module_name]}"
        raise ImportError(error_msg)
    return module

# Decorator for functions that require specific modules
def requires_module(module_name: str, fallback_module: str = None):
    """Decorator to ensure a module is available before function execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            module = load_module(module_name, fallback_module)
            if module is None:
                raise ImportError(f"Function {func.__name__} requires module {module_name}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Common module patterns
class CommonModules:
    """Common module loading patterns"""
    
    @staticmethod
    def load_audio_backend():
        """Load audio backend with fallbacks"""
        # Try sounddevice first
        sounddevice = load_module("sounddevice")
        soundfile = load_module("soundfile")
        
        if sounddevice and soundfile:
            return {"backend": "sounddevice", "sd": sounddevice, "sf": soundfile}
        
        # Try PyAudio as fallback
        pyaudio = load_module("pyaudio")
        if pyaudio:
            return {"backend": "pyaudio", "pyaudio": pyaudio}
        
        # No audio backend available
        return {"backend": "none"}
    
    @staticmethod
    def load_ai_backend():
        """Load AI backend with fallbacks"""
        # Try enhanced AI first
        ai_models = load_module("core.ai_models")
        if ai_models and hasattr(ai_models, "ai_manager"):
            return {"backend": "enhanced", "manager": ai_models.ai_manager}
        
        # Try cloud AI as fallback
        cloud_ai = load_module("core.cloud_ai_manager")
        if cloud_ai:
            get_manager = get_function("core.cloud_ai_manager", "get_cloud_ai_manager")
            if get_manager:
                return {"backend": "cloud", "manager": get_manager()}
        
        # No AI backend available
        return {"backend": "none"}
    
    @staticmethod
    def load_storage_backend():
        """Load storage backend with fallbacks"""
        # Try MinIO first
        minio_storage = load_module("utils.minio_storage")
        if minio_storage:
            get_manager = get_function("utils.minio_storage", "get_storage_manager")
            if get_manager:
                return {"backend": "minio", "manager": get_manager()}
        
        # Try fallback storage
        fallback_storage = load_module("utils.fallback_storage")
        if fallback_storage:
            get_manager = get_function("utils.fallback_storage", "get_fallback_storage_manager")
            if get_manager:
                return {"backend": "fallback", "manager": get_manager()}
        
        # No storage backend available
        return {"backend": "none"}
    
    @staticmethod
    def load_database_backend():
        """Load database backend with fallbacks"""
        # Try Supabase first
        supabase_db = load_module("utils.supabase_db")
        if supabase_db:
            get_manager = get_function("utils.supabase_db", "get_database_manager")
            if get_manager:
                return {"backend": "supabase", "manager": get_manager()}
        
        # Try core database as fallback
        core_db = load_module("core.database")
        if core_db:
            db_manager_class = get_class("core.database", "DatabaseManager")
            if db_manager_class:
                return {"backend": "core", "manager": db_manager_class()}
        
        # No database backend available
        return {"backend": "none"}