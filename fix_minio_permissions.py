#!/usr/bin/env python3
"""
Fix MinIO Permissions and Setup
"""
import boto3
from botocore.exceptions import ClientError
import json

def fix_minio_permissions():
    """Fix MinIO permissions for the bucket"""
    
    print("🔧 Fixing MinIO bucket permissions...")
    
    try:
        # Create MinIO client
        client = boto3.client(
            's3',
            endpoint_url='https://bharatverse-minio.onrender.com',
            aws_access_key_id='minioadmin',
            aws_secret_access_key='minioadmin',
            region_name='us-east-1'
        )
        
        bucket_name = 'bharatverse-bucket'
        
        # Check if bucket exists
        try:
            client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' exists")
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"🪣 Creating bucket '{bucket_name}'...")
                client.create_bucket(Bucket=bucket_name)
                print(f"✅ Bucket '{bucket_name}' created")
            else:
                print(f"❌ Error checking bucket: {e}")
                return False
        
        # Try to set a more permissive bucket policy
        print("🔒 Setting bucket policy...")
        
        # Policy that allows read/write access
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadWrite",
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject"
                    ],
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                },
                {
                    "Sid": "PublicListBucket",
                    "Effect": "Allow", 
                    "Principal": {"AWS": "*"},
                    "Action": "s3:ListBucket",
                    "Resource": f"arn:aws:s3:::{bucket_name}"
                }
            ]
        }
        
        try:
            client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            print("✅ Bucket policy set successfully")
        except ClientError as e:
            print(f"⚠️  Could not set bucket policy: {e}")
            print("This might be normal - MinIO may not support bucket policies")
        
        # Test with a simple upload
        print("🧪 Testing simple upload...")
        try:
            test_key = 'test/simple-test.txt'
            test_content = b'Simple test file'
            
            # Try different approaches
            approaches = [
                # Approach 1: Simple put_object
                lambda: client.put_object(
                    Bucket=bucket_name,
                    Key=test_key,
                    Body=test_content
                ),
                # Approach 2: With explicit content type
                lambda: client.put_object(
                    Bucket=bucket_name,
                    Key=test_key,
                    Body=test_content,
                    ContentType='text/plain'
                ),
                # Approach 3: With ACL
                lambda: client.put_object(
                    Bucket=bucket_name,
                    Key=test_key,
                    Body=test_content,
                    ACL='public-read-write'
                )
            ]
            
            success = False
            for i, approach in enumerate(approaches, 1):
                try:
                    print(f"   Trying approach {i}...")
                    approach()
                    print(f"   ✅ Approach {i} successful!")
                    success = True
                    break
                except ClientError as e:
                    print(f"   ❌ Approach {i} failed: {e}")
                    continue
            
            if success:
                # Test download
                response = client.get_object(Bucket=bucket_name, Key=test_key)
                downloaded = response['Body'].read()
                
                if downloaded == test_content:
                    print("✅ Upload/download test successful!")
                    # Clean up
                    client.delete_object(Bucket=bucket_name, Key=test_key)
                    print("🧹 Test file cleaned up")
                    return True
                else:
                    print("❌ Downloaded content doesn't match")
                    return False
            else:
                print("❌ All upload approaches failed")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 MinIO Permission Fix")
    print("=" * 30)
    
    success = fix_minio_permissions()
    
    if success:
        print("\n🎉 MinIO permissions fixed!")
        print("Your MinIO storage should now work properly.")
    else:
        print("\n❌ Could not fix permissions automatically.")
        print("You may need to configure MinIO manually via the web console.")