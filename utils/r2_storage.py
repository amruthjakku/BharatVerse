"""
Cloudflare R2 Storage Module for BharatVerse Cloud Deployment
Handles file uploads, downloads, and management using Cloudflare R2 object storage

Module: r2_storage.py
Purpose: Direct interface to Cloudflare R2 object storage
- Manages file uploads (audio, images, documents)
- Handles secure file downloads with signed URLs  
- Provides file organization and metadata management
- Compatible with AWS S3 API for easy integration
"""
import streamlit as st
import boto3
from botocore.exceptions import ClientError
import io
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class R2StorageManager:
    """Manages Cloudflare R2 object storage operations"""
    
    def __init__(self):
        """Initialize R2 client using Streamlit secrets"""
        try:
            self.client = boto3.client(
                's3',
                endpoint_url=st.secrets.get("r2", {}).get("endpoint_url", ""),
                aws_access_key_id=st.secrets.get("r2", {}).get("aws_access_key_id", ""),
                aws_secret_access_key=st.secrets.get("r2", {}).get("aws_secret_access_key", ""),
                region_name=st.secrets.get("r2", {}).get("region", "auto")
            )
            self.bucket_name = st.secrets.get("r2", {}).get("bucket_name", "bharatverse-files")
            self.base_url = st.secrets.get("r2", {}).get("public_url", "")
            logger.info("R2 Storage Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize R2 client: {e}")
            self.client = None
            
    def upload_file(self, file_obj, file_key: str, content_type: str = None) -> Optional[str]:
        """
        Upload a file to R2 storage
        
        Args:
            file_obj: File object to upload
            file_key: Key/path for the file in R2
            content_type: MIME type of the file
            
        Returns:
            Public URL of uploaded file or None if failed
        """
        if not self.client:
            logger.error("R2 client not initialized")
            return None
            
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
                
            # Upload the file
            self.client.upload_fileobj(
                file_obj, 
                self.bucket_name, 
                file_key,
                ExtraArgs=extra_args
            )
            
            # Return public URL
            public_url = f"{self.base_url}/{file_key}" if self.base_url else None
            logger.info(f"Successfully uploaded file: {file_key}")
            return public_url
            
        except ClientError as e:
            logger.error(f"Failed to upload file {file_key}: {e}")
            return None
            
    def upload_bytes(self, data: bytes, file_key: str, content_type: str = None) -> Optional[str]:
        """Upload bytes data to R2"""
        file_obj = io.BytesIO(data)
        return self.upload_file(file_obj, file_key, content_type)
        
    def download_file(self, file_key: str) -> Optional[bytes]:
        """
        Download a file from R2 storage
        
        Args:
            file_key: Key/path of the file in R2
            
        Returns:
            File content as bytes or None if failed
        """
        if not self.client:
            logger.error("R2 client not initialized")
            return None
            
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=file_key)
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"Failed to download file {file_key}: {e}")
            return None
            
    def delete_file(self, file_key: str) -> bool:
        """
        Delete a file from R2 storage
        
        Args:
            file_key: Key/path of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("R2 client not initialized")
            return False
            
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=file_key)
            logger.info(f"Successfully deleted file: {file_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file {file_key}: {e}")
            return False
            
    def list_files(self, prefix: str = "", max_keys: int = 1000) -> List[Dict[str, Any]]:
        """
        List files in R2 storage
        
        Args:
            prefix: Filter files by prefix
            max_keys: Maximum number of files to return
            
        Returns:
            List of file information dictionaries
        """
        if not self.client:
            logger.error("R2 client not initialized")
            return []
            
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'url': f"{self.base_url}/{obj['Key']}" if self.base_url else None
                })
            
            return files
        except ClientError as e:
            logger.error(f"Failed to list files with prefix {prefix}: {e}")
            return []
            
    def get_file_url(self, file_key: str) -> Optional[str]:
        """Get public URL for a file"""
        if self.base_url:
            return f"{self.base_url}/{file_key}"
        return None
        
    def generate_presigned_url(self, file_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for temporary access
        
        Args:
            file_key: Key/path of the file
            expiration: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Presigned URL or None if failed
        """
        if not self.client:
            logger.error("R2 client not initialized")
            return None
            
        try:
            response = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {file_key}: {e}")
            return None

# Global storage manager instance
@st.cache_resource
def get_storage_manager() -> R2StorageManager:
    """Get cached storage manager instance"""
    return R2StorageManager()

# Convenience functions
def upload_file(file_obj, file_key: str, content_type: str = None) -> Optional[str]:
    """Upload file using global storage manager"""
    storage = get_storage_manager()
    return storage.upload_file(file_obj, file_key, content_type)

def download_file(file_key: str) -> Optional[bytes]:
    """Download file using global storage manager"""
    storage = get_storage_manager()
    return storage.download_file(file_key)

def delete_file(file_key: str) -> bool:
    """Delete file using global storage manager"""
    storage = get_storage_manager()
    return storage.delete_file(file_key)

def list_files(prefix: str = "", max_keys: int = 1000) -> List[Dict[str, Any]]:
    """List files using global storage manager"""
    storage = get_storage_manager()
    return storage.list_files(prefix, max_keys)