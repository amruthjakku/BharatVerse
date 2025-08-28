# Core module exports with lazy initialization
from .service_manager import get_service_manager, get_service
from .error_handler import error_boundary, safe_import
from .module_loader import CommonModules, get_function

# Lazy imports to avoid initialization issues
def __getattr__(name):
    service_manager = get_service_manager()
    
    if name == 'db_manager':
        # Try to get database service from service manager
        db = service_manager.get_service('database')
        if db:
            return db
        # Fallback to supabase if main database is not available
        return service_manager.get_service('supabase')
    elif name == 'content_repo':
        # Return database service as content repository
        db = service_manager.get_service('database')
        if db:
            return db
        return service_manager.get_service('supabase')
    elif name == 'ai_manager':
        # Try to get AI service from service manager
        ai = service_manager.get_service('ai')
        if ai:
            return ai
        return service_manager.get_service('cloud_ai')
    elif name == 'app':
        # Try to import API service
        app_func = get_function('api_service', 'app')
        if app_func:
            return app_func
        from .api_service import app
        return app
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Helper functions for backward compatibility
def get_db_manager():
    """Get database manager from service manager"""
    service_manager = get_service_manager()
    db = service_manager.get_service('database')
    if db:
        return db
    return service_manager.get_service('supabase')

def get_content_repo():
    """Get content repository (same as database manager)"""
    return get_db_manager()

__all__ = ['db_manager', 'content_repo', 'ai_manager', 'app', 'get_service_manager', 'get_service', 'error_boundary', 'safe_import', 'get_db_manager', 'get_content_repo']
