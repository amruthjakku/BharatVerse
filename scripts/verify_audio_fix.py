#!/usr/bin/env python3
"""
Quick verification script for audio deployment fix
"""

import os
from pathlib import Path

def verify_audio_deployment_fix():
    """Verify that all audio deployment fixes are in place"""
    print("🔍 Verifying Audio Deployment Fix...")
    print("=" * 50)
    
    issues = []
    fixes = []
    
    # Check 1: packages.txt in root directory
    packages_txt_path = Path("packages.txt")
    if packages_txt_path.exists():
        fixes.append("✅ packages.txt exists in root directory")
        
        # Check content
        content = packages_txt_path.read_text().strip()
        required_packages = [
            "portaudio19-dev",
            "python3-pyaudio",
            "ffmpeg",
            "libsndfile1"
        ]
        
        missing_packages = []
        for pkg in required_packages:
            if pkg not in content:
                missing_packages.append(pkg)
        
        if missing_packages:
            issues.append(f"❌ Missing packages in packages.txt: {', '.join(missing_packages)}")
        else:
            fixes.append("✅ packages.txt contains all required packages")
    else:
        issues.append("❌ packages.txt not found in root directory")
    
    # Check 2: requirements.txt has audio dependencies
    requirements_path = Path("requirements.txt")
    if requirements_path.exists():
        content = requirements_path.read_text()
        audio_deps = ["sounddevice", "soundfile", "PyAudio"]
        
        missing_deps = []
        for dep in audio_deps:
            if dep not in content:
                missing_deps.append(dep)
        
        if missing_deps:
            issues.append(f"❌ Missing audio dependencies in requirements.txt: {', '.join(missing_deps)}")
        else:
            fixes.append("✅ requirements.txt contains all audio dependencies")
    else:
        issues.append("❌ requirements.txt not found")
    
    # Check 3: Old packages.txt in config directory (should be removed or ignored)
    old_packages_path = Path("config/packages.txt")
    if old_packages_path.exists():
        issues.append("⚠️ Old packages.txt still exists in config/ directory (this will be ignored by Streamlit Cloud)")
    
    # Check 4: Audio module exists and has been updated
    audio_module_path = Path("streamlit_app/audio_module.py")
    if audio_module_path.exists():
        content = audio_module_path.read_text()
        if "AUDIO_BACKEND" in content and "AUDIO_IMPORT_ERROR" in content:
            fixes.append("✅ Audio module has enhanced error handling")
        else:
            issues.append("❌ Audio module may not have the latest improvements")
    else:
        issues.append("❌ Audio module not found")
    
    # Print results
    print("\n🎯 Fixes Applied:")
    for fix in fixes:
        print(f"  {fix}")
    
    if issues:
        print("\n⚠️ Issues Found:")
        for issue in issues:
            print(f"  {issue}")
    
    # Overall status
    print("\n" + "=" * 50)
    if not issues:
        print("🎉 All audio deployment fixes are in place!")
        print("📤 Ready to deploy to Streamlit Cloud")
        print("\n📋 Next Steps:")
        print("1. Push changes to your repository")
        print("2. Redeploy your Streamlit Cloud app")
        print("3. Test audio functionality after deployment")
    else:
        print("⚠️ Some issues need to be addressed before deployment")
        print("Please fix the issues listed above")
    
    return len(issues) == 0

if __name__ == "__main__":
    verify_audio_deployment_fix()