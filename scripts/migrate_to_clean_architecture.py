#!/usr/bin/env python3
"""
Migration Script: Clean Architecture
Helps migrate from the old scattered logic to the new clean architecture
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Tuple

class ArchitectureMigrator:
    """Migrates code from old scattered patterns to clean architecture"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_old_architecture"
        self.migration_log = []
    
    def create_backup(self):
        """Create backup of current files before migration"""
        print("📦 Creating backup of current files...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        self.backup_dir.mkdir()
        
        # Backup key directories
        dirs_to_backup = ["pages", "streamlit_app", "utils"]
        
        for dir_name in dirs_to_backup:
            src_dir = self.project_root / dir_name
            if src_dir.exists():
                dst_dir = self.backup_dir / dir_name
                shutil.copytree(src_dir, dst_dir)
                print(f"  ✅ Backed up {dir_name}/")
        
        print(f"📦 Backup created at: {self.backup_dir}")
    
    def analyze_current_patterns(self) -> Dict[str, List[str]]:
        """Analyze current problematic patterns in the codebase"""
        print("🔍 Analyzing current problematic patterns...")
        
        patterns = {
            "available_flags": [],
            "try_except_imports": [],
            "scattered_configs": [],
            "redundant_fallbacks": []
        }
        
        # Find all Python files
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            if "backup" in str(file_path) or "__pycache__" in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for *_AVAILABLE patterns
                available_matches = re.findall(r'(\w+_AVAILABLE)\s*=', content)
                if available_matches:
                    patterns["available_flags"].extend([
                        f"{file_path.relative_to(self.project_root)}: {match}" 
                        for match in available_matches
                    ])
                
                # Look for try/except import patterns
                try_import_matches = re.findall(
                    r'try:\s*\n\s*(?:from|import)\s+([^\n]+)\s*\n.*?except\s+ImportError', 
                    content, 
                    re.DOTALL
                )
                if try_import_matches:
                    patterns["try_except_imports"].extend([
                        f"{file_path.relative_to(self.project_root)}: {match.strip()}" 
                        for match in try_import_matches
                    ])
                
                # Look for scattered config patterns
                config_matches = re.findall(r'os\.getenv\(["\']([^"\']+)["\']', content)
                if config_matches:
                    patterns["scattered_configs"].extend([
                        f"{file_path.relative_to(self.project_root)}: {match}" 
                        for match in config_matches
                    ])
                
            except Exception as e:
                print(f"  ⚠️ Error analyzing {file_path}: {e}")
        
        return patterns
    
    def generate_migration_report(self, patterns: Dict[str, List[str]]):
        """Generate a detailed migration report"""
        print("\n📊 Migration Analysis Report")
        print("=" * 50)
        
        total_issues = sum(len(issues) for issues in patterns.values())
        print(f"Total issues found: {total_issues}")
        
        for pattern_type, issues in patterns.items():
            if issues:
                print(f"\n{pattern_type.replace('_', ' ').title()}: {len(issues)} issues")
                for issue in issues[:5]:  # Show first 5 examples
                    print(f"  - {issue}")
                if len(issues) > 5:
                    print(f"  ... and {len(issues) - 5} more")
        
        # Save detailed report
        report_file = self.project_root / "migration_report.txt"
        with open(report_file, 'w') as f:
            f.write("BharatVerse Architecture Migration Report\n")
            f.write("=" * 50 + "\n\n")
            
            for pattern_type, issues in patterns.items():
                f.write(f"{pattern_type.replace('_', ' ').title()}:\n")
                for issue in issues:
                    f.write(f"  - {issue}\n")
                f.write("\n")
        
        print(f"\n📄 Detailed report saved to: {report_file}")
    
    def create_migration_templates(self):
        """Create migration templates for common patterns"""
        print("\n📝 Creating migration templates...")
        
        templates_dir = self.project_root / "migration_templates"
        templates_dir.mkdir(exist_ok=True)
        
        # Template for converting old pages
        page_template = '''"""
Migrated Page Template
Replace old scattered logic with clean architecture
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.page_template import create_page, get_page_config
from core.service_manager import get_service_manager
from core.config_manager import get_config_manager
from core.error_handler import error_boundary, handle_errors

@create_page(
    title="Your Page Title",
    icon="🎯",
    description="Your page description",
    required_services=["service1", "service2"],  # Replace with actual services
    optional_services=["service3"]  # Replace with actual services
)
def your_page():
    """Clean page implementation"""
    
    service_manager = get_service_manager()
    config_manager = get_config_manager()
    
    # Your page logic here
    st.write("Page content")

if __name__ == "__main__":
    your_page()
'''
        
        with open(templates_dir / "page_template.py", 'w') as f:
            f.write(page_template)
        
        # Template for converting modules
        module_template = '''"""
Migrated Module Template
Replace scattered imports and availability flags
"""

from core.service_manager import get_service_manager
from core.error_handler import handle_errors, error_boundary
from core.module_loader import load_module, get_function

class YourModule:
    """Clean module implementation"""
    
    def __init__(self):
        self.service_manager = get_service_manager()
    
    @handle_errors(show_error=True)
    def your_method(self):
        """Method with clean error handling"""
        
        # Get required service
        service = self.service_manager.get_service("your_service")
        if not service:
            raise RuntimeError("Required service not available")
        
        # Your logic here
        return "result"

# Factory function
def get_your_module():
    """Get module instance"""
    return YourModule()
'''
        
        with open(templates_dir / "module_template.py", 'w') as f:
            f.write(module_template)
        
        print(f"📝 Templates created in: {templates_dir}")
    
    def suggest_migration_steps(self, patterns: Dict[str, List[str]]):
        """Suggest specific migration steps"""
        print("\n🚀 Suggested Migration Steps")
        print("=" * 30)
        
        steps = [
            "1. 📦 Backup completed - files are safe",
            "2. 🏗️ New architecture components created:",
            "   - core/service_manager.py",
            "   - core/error_handler.py", 
            "   - core/config_manager.py",
            "   - core/module_loader.py",
            "   - core/page_template.py",
            "",
            "3. 🔄 Migration priorities:",
        ]
        
        if patterns["available_flags"]:
            steps.append(f"   - Replace {len(patterns['available_flags'])} *_AVAILABLE flags with service_manager.is_available()")
        
        if patterns["try_except_imports"]:
            steps.append(f"   - Replace {len(patterns['try_except_imports'])} try/except imports with module_loader")
        
        if patterns["scattered_configs"]:
            steps.append(f"   - Centralize {len(patterns['scattered_configs'])} config values in config_manager")
        
        steps.extend([
            "",
            "4. 📄 Example migrations:",
            "   - pages/01_🎤_Audio_Capture_Clean.py (clean example created)",
            "   - Use migration_templates/ for guidance",
            "",
            "5. ✅ Testing:",
            "   - Test each migrated component",
            "   - Verify service availability",
            "   - Check error handling",
            "",
            "6. 🧹 Cleanup:",
            "   - Remove old *_AVAILABLE variables",
            "   - Remove scattered try/except blocks",
            "   - Remove redundant fallback files",
        ])
        
        for step in steps:
            print(step)
    
    def run_migration_analysis(self):
        """Run complete migration analysis"""
        print("🚀 Starting BharatVerse Architecture Migration")
        print("=" * 50)
        
        # Create backup
        self.create_backup()
        
        # Analyze patterns
        patterns = self.analyze_current_patterns()
        
        # Generate report
        self.generate_migration_report(patterns)
        
        # Create templates
        self.create_migration_templates()
        
        # Suggest steps
        self.suggest_migration_steps(patterns)
        
        print("\n✅ Migration analysis complete!")
        print("\n📋 Next steps:")
        print("1. Review the migration report")
        print("2. Use the templates to migrate your pages")
        print("3. Test each component after migration")
        print("4. Remove old patterns once migration is complete")

def main():
    """Main migration function"""
    import sys
    
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
    
    migrator = ArchitectureMigrator(project_root)
    migrator.run_migration_analysis()

if __name__ == "__main__":
    main()