#!/usr/bin/env python3
"""
Quick Launch Script for BharatVerse
Simple one-click launcher for the cultural heritage platform
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Quick launch function"""
    print("🌍 BharatVerse - Quick Launch")
    print("=" * 30)
    print("🚀 Starting cultural heritage platform...")
    print("⚡ Maximum performance mode active")
    print()
    
    # Import and run the full launcher
    try:
        from scripts.run_app import BharatVerseRunner
        runner = BharatVerseRunner()
        runner.run()
    except ImportError:
        # Fallback to direct streamlit run
        print("📦 Using direct Streamlit launch...")
        os.chdir(project_root)
        os.system("streamlit run Home.py")

if __name__ == "__main__":
    main()