"""
Smart Storage Manager for BharatVerse
Automatically chooses between MinIO and local storage
"""
import streamlit as st
import logging
from typing import Optional, List, Dict, Any
import io
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class SmartStorageManager:
    """Smart storage that falls back gracefully"""
    
    def __init__(self):
        """Initialize with the best available storage"""
        self.primary_storage = None
        self.fallback_storage = None
        self._setup_storage()
    
    def _setup_storage(self):
        """Set up primary and fallback storage"""
        
        # Try MinIO first
        try:
            from utils.minio_storage import MinIOStorageManager
            minio = MinIOStorageManager()
            
            # Quick test
            if minio.client:
                try:
                    minio.client.list_buckets()
                    self.primary_storage = minio
                    logger.info("✅ Using MinIO as primary storage")
                except Exception as e:
                    logger.warning(f"MinIO connection failed: {e}")
        except Exception as e:
            logger.warning(f"MinIO import failed: {e}")
        
        # Set up local fallback
        self._setup_local_fallback()
        
        if not self.primary_storage:
            logger.info("🏠 Using local storage (MinIO not available)")
    
    def _setup_local_fallback(self):
        """Set up local storage fallback"""
        try:
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)
            self.fallback_storage = LocalStorage(upload_dir)
            logger.info("📁 Local fallback storage ready")
        except Exception as e:
            logger.error(f"Could not set up local storage: {e}")
    
    def _get_active_storage(self):
        """Get the active storage (primary or fallback)"""
        if self.primary_storage:
            return self.primary_storage
        elif self.fallback_storage:
            return self.fallback_storage
        else:
            raise Exception("No storage available")
    
    def upload_file(self, file_obj, file_key: str, content_type: str = None) -> Optional[str]:
        """Upload file using available storage"""
        try:
            storage = self._get_active_storage()
            return storage.upload_file(file_obj, file_key, content_type)
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return None
    
    def upload_bytes(self, data: bytes, file_key: str, content_type: str = None) -> Optional[str]:
        """Upload bytes using available storage"""
        try:
            storage = self._get_active_storage()
            if hasattr(storage, 'upload_bytes'):
                return storage.upload_bytes(data, file_key, content_type)
            else:
                file_obj = io.BytesIO(data)
                return storage.upload_file(file_obj, file_key, content_type)
        except Exception as e:
            logger.error(f"Upload bytes failed: {e}")
            return None
    
    def download_file(self, file_key: str) -> Optional[bytes]:
        """Download file using available storage"""
        try:
            storage = self._get_active_storage()
            return storage.download_file(file_key)
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None
    
    def delete_file(self, file_key: str) -> bool:
        """Delete file using available storage"""
        try:
            storage = self._get_active_storage()
            return storage.delete_file(file_key)
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False
    
    def list_files(self, prefix: str = "", max_keys: int = 1000) -> List[Dict[str, Any]]:
        """List files using available storage"""
        try:
            storage = self._get_active_storage()
            return storage.list_files(prefix, max_keys)
        except Exception as e:
            logger.error(f"List failed: {e}")
            return []
    
    def get_storage_type(self) -> str:
        """Get current storage type"""
        if self.primary_storage:
            return "MinIO"
        elif self.fallback_storage:
            return "Local"
        else:
            return "None"


class LocalStorage:
    """Simple local file storage"""
    
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.bucket_name = "local-bucket"
    
    def upload_file(self, file_obj, file_key: str, content_type: str = None) -> Optional[str]:
        """Save file locally"""
        try:
            file_path = self.storage_dir / file_key
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Handle different file object types
            if hasattr(file_obj, 'read'):
                content = file_obj.read()
                if hasattr(file_obj, 'seek'):
                    file_obj.seek(0)  # Reset for potential reuse
            else:
                content = file_obj
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            return f"local://{file_key}"
            
        except Exception as e:
            logger.error(f"Local upload failed: {e}")
            return None
    
    def download_file(self, file_key: str) -> Optional[bytes]:
        """Read file locally"""
        try:
            file_path = self.storage_dir / file_key
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    return f.read()
            return None
        except Exception as e:
            logger.error(f"Local download failed: {e}")
            return None
    
    def delete_file(self, file_key: str) -> bool:
        """Delete local file"""
        try:
            file_path = self.storage_dir / file_key
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Local delete failed: {e}")
            return False
    
    def list_files(self, prefix: str = "", max_keys: int = 1000) -> List[Dict[str, Any]]:
        """List local files"""
        try:
            files = []
            search_dir = self.storage_dir / prefix if prefix else self.storage_dir
            
            if search_dir.exists():
                for file_path in search_dir.rglob("*"):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(self.storage_dir)
                        stat = file_path.stat()
                        files.append({
                            'key': str(rel_path),
                            'size': stat.st_size,
                            'last_modified': stat.st_mtime,
                            'url': f"local://{rel_path}"
                        })
            
            return files[:max_keys]
        except Exception as e:
            logger.error(f"Local list failed: {e}")
            return []


# Global instance
@st.cache_resource
def get_storage_manager() -> SmartStorageManager:
    """Get cached smart storage manager"""
    return SmartStorageManager()


# Convenience functions for backward compatibility
def upload_file(file_obj, file_key: str, content_type: str = None) -> Optional[str]:
    """Upload file using smart storage"""
    storage = get_storage_manager()
    return storage.upload_file(file_obj, file_key, content_type)

def download_file(file_key: str) -> Optional[bytes]:
    """Download file using smart storage"""
    storage = get_storage_manager()
    return storage.download_file(file_key)

def delete_file(file_key: str) -> bool:
    """Delete file using smart storage"""
    storage = get_storage_manager()
    return storage.delete_file(file_key)

def list_files(prefix: str = "", max_keys: int = 1000) -> List[Dict[str, Any]]:
    """List files using smart storage"""
    storage = get_storage_manager()
    return storage.list_files(prefix, max_keys)