"""
Fallback Storage Manager for BharatVerse
Provides basic file handling when external storage is not available
"""
import streamlit as st
import io
from typing import Optional, List, Dict, Any
import logging
import os
import tempfile
import base64

logger = logging.getLogger(__name__)

class FallbackStorageManager:
    """Fallback storage manager using session state and temporary files"""
    
    def __init__(self):
        """Initialize fallback storage"""
        self.available = True
        if 'fallback_storage' not in st.session_state:
            st.session_state.fallback_storage = {}
        logger.info("Fallback Storage Manager initialized")
    
    def upload_file(self, file_obj, file_key: str, content_type: str = None) -> Optional[str]:
        """
        Store file in session state (temporary storage)
        
        Args:
            file_obj: File object to store
            file_key: Key/path for the file
            content_type: MIME type of the file
            
        Returns:
            Temporary reference or None if failed
        """
        try:
            # Read file content
            if hasattr(file_obj, 'read'):
                file_content = file_obj.read()
            else:
                file_content = file_obj
            
            # Store in session state (base64 encoded for JSON serialization)
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            
            st.session_state.fallback_storage[file_key] = {
                'content': encoded_content,
                'content_type': content_type or 'application/octet-stream',
                'size': len(file_content)
            }
            
            logger.info(f"File stored in fallback storage: {file_key}")
            return f"fallback://{file_key}"
            
        except Exception as e:
            logger.error(f"Failed to store file {file_key}: {e}")
            return None
    
    def download_file(self, file_key: str) -> Optional[bytes]:
        """
        Retrieve file from session state
        
        Args:
            file_key: Key/path of the file
            
        Returns:
            File content as bytes or None if not found
        """
        try:
            if file_key in st.session_state.fallback_storage:
                encoded_content = st.session_state.fallback_storage[file_key]['content']
                return base64.b64decode(encoded_content)
            else:
                logger.warning(f"File not found in fallback storage: {file_key}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve file {file_key}: {e}")
            return None
    
    def delete_file(self, file_key: str) -> bool:
        """
        Delete file from session state
        
        Args:
            file_key: Key/path of the file to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if file_key in st.session_state.fallback_storage:
                del st.session_state.fallback_storage[file_key]
                logger.info(f"File deleted from fallback storage: {file_key}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_key}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete file {file_key}: {e}")
            return False
    
    def list_files(self, prefix: str = "", max_keys: int = 1000) -> List[Dict[str, Any]]:
        """
        List files in session state storage
        
        Args:
            prefix: Filter files by prefix
            max_keys: Maximum number of files to return
            
        Returns:
            List of file information dictionaries
        """
        try:
            files = []
            count = 0
            
            for file_key, file_info in st.session_state.fallback_storage.items():
                if count >= max_keys:
                    break
                    
                if file_key.startswith(prefix):
                    files.append({
                        'Key': file_key,
                        'Size': file_info.get('size', 0),
                        'ContentType': file_info.get('content_type', 'application/octet-stream'),
                        'LastModified': 'N/A',  # Not tracked in fallback
                        'StorageClass': 'FALLBACK'
                    })
                    count += 1
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    def get_file_url(self, file_key: str) -> Optional[str]:
        """
        Get a temporary URL for the file (fallback doesn't support direct URLs)
        
        Args:
            file_key: Key/path of the file
            
        Returns:
            Fallback reference or None if not found
        """
        if file_key in st.session_state.fallback_storage:
            return f"fallback://{file_key}"
        return None
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            total_files = len(st.session_state.fallback_storage)
            total_size = sum(
                file_info.get('size', 0) 
                for file_info in st.session_state.fallback_storage.values()
            )
            
            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'storage_type': 'fallback',
                'available': True
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {
                'total_files': 0,
                'total_size_bytes': 0,
                'storage_type': 'fallback',
                'available': False
            }

# Global fallback storage manager instance
@st.cache_resource
def get_fallback_storage_manager() -> FallbackStorageManager:
    """Get cached fallback storage manager instance"""
    return FallbackStorageManager()

# Convenience functions
def upload_file_fallback(file_obj, file_key: str, content_type: str = None) -> Optional[str]:
    """Upload file using fallback storage manager"""
    manager = get_fallback_storage_manager()
    return manager.upload_file(file_obj, file_key, content_type)

def download_file_fallback(file_key: str) -> Optional[bytes]:
    """Download file using fallback storage manager"""
    manager = get_fallback_storage_manager()
    return manager.download_file(file_key)

def delete_file_fallback(file_key: str) -> bool:
    """Delete file using fallback storage manager"""
    manager = get_fallback_storage_manager()
    return manager.delete_file(file_key)

def list_files_fallback(prefix: str = "", max_keys: int = 1000) -> List[Dict[str, Any]]:
    """List files using fallback storage manager"""
    manager = get_fallback_storage_manager()
    return manager.list_files(prefix, max_keys)