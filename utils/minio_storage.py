"""
MinIO Storage Module for BharatVerse Cloud Deployment
Handles file uploads, downloads, and management using MinIO object storage on Render

Module: minio_storage.py (formerly r2_storage.py)
Purpose: Direct interface to MinIO object storage hosted on Render
- Manages file uploads (audio, images, documents)
- Handles secure file downloads with signed URLs  
- Provides file organization and metadata management
- Compatible with AWS S3 API for easy integration
- Auto-creates buckets and handles connection management
"""
import streamlit as st
import io
from typing import Optional, List, Dict, Any
import logging
import os

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None
    ClientError = Exception

try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    Minio = None
    S3Error = Exception

# Optional .env support
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    pass  # python-dotenv is optional

logger = logging.getLogger(__name__)

class MinIOStorageManager:
    """Manages MinIO object storage operations hosted on Render"""
    
    def __init__(self):
        """Initialize MinIO client using Streamlit secrets"""
        self.available = False
        self.client = None
        self.bucket_name = None
        self.endpoint_url = None
        
        if not BOTO3_AVAILABLE:
            logger.warning("boto3 not available - MinIO storage disabled")
            return
            
        try:
            # Try both minio and r2 sections for backward compatibility
            config = st.secrets.get("minio", st.secrets.get("r2", {}))
            
            if not config:
                logger.info("No MinIO/S3 configuration found - storage disabled")
                return
            
            self.client = boto3.client(
                's3',
                endpoint_url=config.get("endpoint_url", ""),
                aws_access_key_id=config.get("aws_access_key_id", "minioadmin"),
                aws_secret_access_key=config.get("aws_secret_access_key", "minioadmin"), 
                region_name=config.get("region_name", "us-east-1")
            )
            self.bucket_name = config.get("bucket_name", "bharatverse-bucket")
            self.endpoint_url = config.get("endpoint_url", "")
            self.available = True
            
            # Ensure bucket exists
            self._ensure_bucket_exists()
            
            logger.info("MinIO Storage Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            self.client = None
            
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        if not self.client:
            return
            
        try:
            # Check if bucket exists
            self.client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket {self.bucket_name} exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    self.client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Created bucket: {self.bucket_name}")
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket {self.bucket_name}: {create_error}")
            else:
                logger.error(f"Error checking bucket {self.bucket_name}: {e}")
            
    def upload_file(self, file_obj, file_key: str, content_type: str = None) -> Optional[str]:
        """
        Upload a file to MinIO storage
        
        Args:
            file_obj: File object to upload
            file_key: Key/path for the file in MinIO
            content_type: MIME type of the file
            
        Returns:
            Public URL of uploaded file or None if failed
        """
        if not self.available or not self.client:
            logger.error("MinIO client not initialized")
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
            
            # Return public URL - construct from endpoint
            public_url = f"{self.endpoint_url}/{self.bucket_name}/{file_key}" if self.endpoint_url else None
            logger.info(f"Successfully uploaded file: {file_key}")
            return public_url
            
        except ClientError as e:
            logger.error(f"Failed to upload file {file_key}: {e}")
            return None
            
    def upload_bytes(self, data: bytes, file_key: str, content_type: str = None) -> Optional[str]:
        """Upload bytes data to MinIO"""
        file_obj = io.BytesIO(data)
        return self.upload_file(file_obj, file_key, content_type)
        
    def download_file(self, file_key: str) -> Optional[bytes]:
        """
        Download a file from MinIO storage
        
        Args:
            file_key: Key/path of the file in MinIO
            
        Returns:
            File content as bytes or None if failed
        """
        if not self.client:
            logger.error("MinIO client not initialized")
            return None
            
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=file_key)
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"Failed to download file {file_key}: {e}")
            return None
            
    def delete_file(self, file_key: str) -> bool:
        """
        Delete a file from MinIO storage
        
        Args:
            file_key: Key/path of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("MinIO client not initialized")
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
        List files in MinIO storage
        
        Args:
            prefix: Filter files by prefix
            max_keys: Maximum number of files to return
            
        Returns:
            List of file information dictionaries
        """
        if not self.client:
            logger.error("MinIO client not initialized")
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
                    'url': f"{self.endpoint_url}/{self.bucket_name}/{obj['Key']}" if self.endpoint_url else None
                })
            
            return files
        except ClientError as e:
            logger.error(f"Failed to list files with prefix {prefix}: {e}")
            return []
            
    def get_file_url(self, file_key: str) -> Optional[str]:
        """Get public URL for a file"""
        if self.endpoint_url:
            return f"{self.endpoint_url}/{self.bucket_name}/{file_key}"
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
            logger.error("MinIO client not initialized")
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
def get_storage_manager() -> MinIOStorageManager:
    """Get cached storage manager instance"""
    return MinIOStorageManager()

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