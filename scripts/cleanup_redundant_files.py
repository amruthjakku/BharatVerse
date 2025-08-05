#!/usr/bin/env python3
"""
Cleanup Redundant Files
Identifies and optionally removes redundant fallback files and useless patterns
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Set

class RedundantFilesCleaner:
    """Identifies and cleans up redundant files and patterns"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.redundant_files = []
        self.useless_patterns = []
        
    def identify_redundant_fallback_files(self) -> List[Path]:
        """Identify redundant fallback files that are no longer needed"""
        
        redundant_files = []
        
        # Files that are now redundant with the new architecture
        potentially_redundant = [
            "utils/fallback_auth.py",
            "utils/fallback_memory.py", 
            "utils/fallback_storage.py",
            "utils/config_validator.py",  # Replaced by config_manager
        ]
        
        for file_path in potentially_redundant:
            full_path = self.project_root / file_path
            if full_path.exists():
                redundant_files.append(full_path)
        
        return redundant_files
    
    def identify_useless_patterns_in_files(self) -> Dict[str, List[str]]:
        """Identify useless patterns in files"""
        
        useless_patterns = {}
        
        # Find all Python files
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            if "backup" in str(file_path) or "__pycache__" in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                patterns_found = []
                
                # Look for empty except blocks
                if "except:" in content or "except ImportError:" in content:
                    if "pass" in content:
                        patterns_found.append("Empty except blocks")
                
                # Look for unused *_AVAILABLE variables
                import re
                available_vars = re.findall(r'(\w+_AVAILABLE)\s*=', content)
                for var in available_vars:
                    # Check if it's actually used meaningfully
                    usage_count = content.count(var)
                    if usage_count <= 2:  # Only declaration and one trivial use
                        patterns_found.append(f"Unused variable: {var}")
                
                # Look for redundant try/except import patterns
                try_import_count = content.count("try:") + content.count("except ImportError:")
                if try_import_count > 10:  # Arbitrary threshold
                    patterns_found.append("Excessive try/except imports")
                
                if patterns_found:
                    useless_patterns[str(file_path.relative_to(self.project_root))] = patterns_found
                    
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
        
        return useless_patterns
    
    def generate_cleanup_report(self):
        """Generate a cleanup report"""
        
        print("🧹 BharatVerse Cleanup Analysis")
        print("=" * 40)
        
        # Identify redundant files
        redundant_files = self.identify_redundant_fallback_files()
        
        print(f"\n📁 Redundant Files Found: {len(redundant_files)}")
        for file_path in redundant_files:
            print(f"  - {file_path.relative_to(self.project_root)}")
        
        # Identify useless patterns
        useless_patterns = self.identify_useless_patterns_in_files()
        
        print(f"\n🔍 Files with Useless Patterns: {len(useless_patterns)}")
        for file_path, patterns in list(useless_patterns.items())[:10]:  # Show first 10
            print(f"  - {file_path}: {', '.join(patterns)}")
        
        if len(useless_patterns) > 10:
            print(f"  ... and {len(useless_patterns) - 10} more files")
        
        return redundant_files, useless_patterns
    
    def suggest_cleanup_actions(self, redundant_files: List[Path], useless_patterns: Dict[str, List[str]]):
        """Suggest cleanup actions"""
        
        print("\n🚀 Suggested Cleanup Actions")
        print("=" * 30)
        
        if redundant_files:
            print("\n1. 🗑️ Remove Redundant Files:")
            print("   These files are replaced by the new architecture:")
            for file_path in redundant_files:
                print(f"   - {file_path.relative_to(self.project_root)}")
            print("   ⚠️  Make sure to test thoroughly before deletion!")
        
        if useless_patterns:
            print(f"\n2. 🔧 Fix Useless Patterns:")
            print(f"   Found {len(useless_patterns)} files with problematic patterns")
            print("   - Replace *_AVAILABLE flags with service_manager.is_available()")
            print("   - Remove empty except blocks")
            print("   - Consolidate try/except imports using module_loader")
        
        print("\n3. 📝 Migration Priority:")
        print("   - High: Pages with many *_AVAILABLE flags")
        print("   - Medium: Utility modules with try/except patterns")
        print("   - Low: Fallback files (remove after migration)")
        
        print("\n4. ✅ Verification Steps:")
        print("   - Test each component after cleanup")
        print("   - Verify service availability")
        print("   - Check error handling works correctly")
    
    def create_cleanup_script(self, redundant_files: List[Path]):
        """Create a script to safely remove redundant files"""
        
        script_content = '''#!/usr/bin/env python3
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
'''
        
        for file_path in redundant_files:
            rel_path = file_path.relative_to(self.project_root)
            script_content += f'        "{rel_path}",\n'
        
        script_content += '''    ]
    
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
'''
        
        script_path = self.project_root / "scripts" / "auto_cleanup.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        print(f"\n📜 Cleanup script created: {script_path}")
        print("   Review the script before running!")
    
    def run_analysis(self):
        """Run complete cleanup analysis"""
        
        redundant_files, useless_patterns = self.generate_cleanup_report()
        self.suggest_cleanup_actions(redundant_files, useless_patterns)
        
        if redundant_files:
            self.create_cleanup_script(redundant_files)
        
        # Save detailed report
        report_path = self.project_root / "cleanup_report.txt"
        with open(report_path, 'w') as f:
            f.write("BharatVerse Cleanup Report\n")
            f.write("=" * 30 + "\n\n")
            
            f.write("Redundant Files:\n")
            for file_path in redundant_files:
                f.write(f"  - {file_path.relative_to(self.project_root)}\n")
            
            f.write("\nFiles with Useless Patterns:\n")
            for file_path, patterns in useless_patterns.items():
                f.write(f"  - {file_path}: {', '.join(patterns)}\n")
        
        print(f"\n📄 Detailed report saved: {report_path}")

def main():
    """Main cleanup function"""
    import sys
    
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
    
    cleaner = RedundantFilesCleaner(project_root)
    cleaner.run_analysis()

if __name__ == "__main__":
    main()