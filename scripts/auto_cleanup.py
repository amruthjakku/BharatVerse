#!/usr/bin/env python3
"""
Auto-generated cleanup script
REVIEW CAREFULLY before running!
"""

import os
import shutil
from pathlib import Path

def backup_and_remove_files():
    """Backup and remove redundant files"""
    
    project_root = Path(__file__).parent.parent
    backup_dir = project_root / "cleanup_backup"
    backup_dir.mkdir(exist_ok=True)
    
    files_to_remove = [
        "utils/fallback_auth.py",
        "utils/fallback_memory.py",
        "utils/fallback_storage.py",
        "utils/config_validator.py",
    ]
    
    print("🗑️ Backing up and removing redundant files...")
    
    for file_path in files_to_remove:
        full_path = project_root / file_path
        if full_path.exists():
            # Create backup
            backup_path = backup_dir / file_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(full_path, backup_path)
            
            # Remove original
            full_path.unlink()
            print(f"  ✅ Removed: {file_path}")
        else:
            print(f"  ⚠️  Not found: {file_path}")
    
    print(f"📦 Backup created at: {backup_dir}")

if __name__ == "__main__":
    print("⚠️  WARNING: This will remove files!")
    print("Make sure you have tested the new architecture first.")
    response = input("Continue? (yes/no): ")
    
    if response.lower() == "yes":
        backup_and_remove_files()
    else:
        print("Cleanup cancelled.")
