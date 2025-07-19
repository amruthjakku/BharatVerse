#!/usr/bin/env python3
"""
MinIO Console Access Helper
"""
import requests
import webbrowser

def try_minio_console():
    """Try to access MinIO console"""
    
    base_url = "https://bharatverse-minio.onrender.com"
    console_paths = [
        "/",
        "/minio",
        "/console", 
        "/ui",
        ":9001"
    ]
    
    print("🌐 Trying to access MinIO console...")
    print("=" * 40)
    
    for path in console_paths:
        if path.startswith(":"):
            # Different port
            url = base_url.replace(":443", path)
        else:
            url = f"{base_url}{path}"
            
        print(f"🔍 Trying: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text.lower()
                if any(keyword in content for keyword in ["minio", "console", "login", "access"]):
                    print(f"   ✅ Found MinIO interface!")
                    print(f"   🌐 Opening: {url}")
                    webbrowser.open(url)
                    return url
                else:
                    print(f"   ⚠️  HTTP 200 but no MinIO content detected")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n💡 Manual Console Access:")
    print("=" * 40)
    print("1. Go to your Render dashboard")
    print("2. Open your bharatverse-minio service")
    print("3. Check the logs for console URL")
    print("4. Look for a line like: 'MinIO Console is available at http://...'")
    
    return None

if __name__ == "__main__":
    print("🖥️  MinIO Console Access")
    print("=" * 30)
    
    console_url = try_minio_console()
    
    if console_url:
        print(f"\n🎉 Console found: {console_url}")
        print("Login with:")
        print("  Username: minioadmin")
        print("  Password: minioadmin")
    else:
        print("\n❌ Could not auto-detect console.")
        print("Check your Render service logs manually.")