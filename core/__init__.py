# Core module exports with lazy initialization
from .database import get_db_manager, get_content_repo

# Lazy imports to avoid initialization issues
def __getattr__(name):
    if name == 'db_manager':
        return get_db_manager()
    elif name == 'content_repo':
        return get_content_repo()
    elif name == 'ai_manager':
        from .ai_models import ai_manager
        return ai_manager
    elif name == 'app':
        from .api_service import app
        return app
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = ['db_manager', 'content_repo', 'ai_manager', 'app']
