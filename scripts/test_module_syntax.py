#!/usr/bin/env python3
"""
Test script to check for syntax errors in modules
"""

import sys
from pathlib import Path
import ast

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def check_syntax(file_path):
    """Check if a Python file has syntax errors"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the AST to check for syntax errors
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error reading file: {e}"

def test_modules():
    print("🧪 Testing module syntax...")
    
    modules_to_test = [
        "streamlit_app/text_module.py",
        "streamlit_app/image_module.py", 
        "streamlit_app/utils/database.py",
        "pages/02_📝_Text_Stories.py",
        "pages/03_📸_Visual_Heritage.py",
        "pages/07_🗄️_Database_Admin.py"
    ]
    
    for module in modules_to_test:
        file_path = project_root / module
        if file_path.exists():
            is_valid, error = check_syntax(file_path)
            if is_valid:
                print(f"✅ {module}")
            else:
                print(f"❌ {module}: {error}")
        else:
            print(f"⚠️  {module}: File not found")
    
    print("\n✅ Syntax check completed!")

if __name__ == "__main__":
    test_modules()