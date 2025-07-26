#!/usr/bin/env python3
"""
Test MinIO Connection and Setup
"""
import boto3
from botocore.exceptions import ClientError
import datetime

def test_minio_connection():
    """Test MinIO connection and create bucket if needed"""
    
    print("🧪 Testing MinIO connection...")
    
    try:
        # Create MinIO client
        client = boto3.client(
            's3',
            endpoint_url='https://bharatverse-minio.onrender.com',
            aws_access_key_id='minioadmin',
            aws_secret_access_key='minioadmin',
            region_name='us-east-1'
        )
        
        # Test connection by listing buckets
        response = client.list_buckets()
        print("✅ MinIO connection successful!")
        
        # Check if bharatverse-bucket exists
        bucket_name = 'bharatverse-bucket'
        existing_buckets = [bucket['Name'] for bucket in response.get('Buckets', [])]
        
        print(f"📋 Found {len(existing_buckets)} existing buckets")
        
        if bucket_name in existing_buckets:
            print(f"✅ Bucket '{bucket_name}' already exists!")
        else:
            print(f"🪣 Creating bucket '{bucket_name}'...")
            try:
                client.create_bucket(Bucket=bucket_name)
                print(f"✅ Bucket '{bucket_name}' created successfully!")
            except ClientError as e:
                print(f"⚠️  Could not create bucket: {e}")
                return False
        
        # Test upload/download
        print("🔄 Testing file upload/download...")
        try:
            test_key = 'test/setup-verification.txt'
            test_content = f'BharatVerse MinIO setup verification - {datetime.datetime.now()}'.encode()
            
            # Upload test file
            client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=test_content,
                ContentType='text/plain'
            )
            
            # Download test file  
            response = client.get_object(Bucket=bucket_name, Key=test_key)
            downloaded_content = response['Body'].read()
            
            if downloaded_content == test_content:
                print("✅ File upload/download test successful!")
                # Clean up test file
                client.delete_object(Bucket=bucket_name, Key=test_key)
                print("🧹 Test file cleaned up")
                
                print("\n🎉 MinIO setup complete!")
                print("=" * 40)
                print("📍 Endpoint: https://bharatverse-minio.onrender.com")
                print("🪣 Bucket: bharatverse-bucket") 
                print("🔑 Access Key: minioadmin")
                print("🔑 Secret Key: minioadmin")
                print("🌍 Region: us-east-1")
                print("=" * 40)
                
                return True
            else:
                print("❌ File content mismatch in test")
                return False
                
        except ClientError as e:
            print(f"❌ Upload/download test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ MinIO connection failed: {e}")
        print("Please check:")
        print("  • MinIO service is running on Render")
        print("  • Endpoint URL is correct: https://bharatverse-minio.onrender.com")
        print("  • Credentials are correct: minioadmin / minioadmin")
        print("  • Network connection is stable")
        return False

if __name__ == "__main__":
    print("🪣 MinIO Connection Test")
    print("=" * 30)
    
    success = test_minio_connection()
    
    if success:
        print("\n✅ Your MinIO storage is ready to use!")
        print("You can now run the main application or continue with setup.")
    else:
        print("\n❌ MinIO setup needs attention.")
        print("Check your Render deployment and try again.")