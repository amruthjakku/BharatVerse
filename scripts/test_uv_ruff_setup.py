#!/usr/bin/env python3
"""
BharatVerse - Test uv and ruff Setup
This script tests that the migration to uv and ruff was successful.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description="", capture_output=True):
    """Run a command and return success status"""
    print(f"🔄 Testing: {description}")
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            capture_output=capture_output, 
            text=True
        )
        print(f"✅ {description} - Success")
        if not capture_output and result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        if capture_output and e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return False


def test_uv_installation():
    """Test if uv is installed and working"""
    print("\n📦 Testing uv installation...")
    
    if not run_command("uv --version", "uv version check"):
        return False
    
    if not run_command("uv pip --help", "uv pip help"):
        return False
    
    return True


def test_ruff_installation():
    """Test if ruff is installed and working"""
    print("\n🔧 Testing ruff installation...")
    
    if not run_command("uv run ruff --version", "ruff version check"):
        return False
    
    if not run_command("uv run ruff check --help", "ruff check help"):
        return False
    
    if not run_command("uv run ruff format --help", "ruff format help"):
        return False
    
    return True


def test_project_structure():
    """Test if project structure is correct"""
    print("\n📁 Testing project structure...")
    
    required_files = [
        "pyproject.toml",
        "UV_RUFF_GUIDE.md",
        ".pre-commit-config.yaml",
        "Makefile"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Missing required file: {file_path}")
            return False
        else:
            print(f"✅ Found: {file_path}")
    
    return True


def test_pyproject_toml():
    """Test if pyproject.toml has correct structure"""
    print("\n⚙️ Testing pyproject.toml configuration...")
    
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            print("⚠️ Cannot test pyproject.toml - no TOML library available")
            return True
    
    try:
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)
        
        # Check for required sections
        required_sections = [
            "project",
            "tool.ruff",
            "tool.mypy",
            "tool.pytest.ini_options"
        ]
        
        for section in required_sections:
            keys = section.split(".")
            current = config
            for key in keys:
                if key not in current:
                    print(f"❌ Missing section: {section}")
                    return False
                current = current[key]
            print(f"✅ Found section: {section}")
        
        # Check if dependencies are defined
        if "dependencies" not in config["project"]:
            print("❌ Missing project dependencies")
            return False
        
        print(f"✅ Found {len(config['project']['dependencies'])} core dependencies")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading pyproject.toml: {e}")
        return False


def test_make_commands():
    """Test if make commands work"""
    print("\n🔨 Testing make commands...")
    
    make_commands = [
        ("make help", "make help command"),
        ("make lint", "make lint command"),
        ("make format", "make format command"),
    ]
    
    for cmd, desc in make_commands:
        if not run_command(cmd, desc):
            return False
    
    return True


def test_ruff_functionality():
    """Test if ruff can actually check and format code"""
    print("\n🧪 Testing ruff functionality...")
    
    # Create a test file with intentional issues
    test_file = Path("test_ruff_temp.py")
    test_content = '''import os,sys
def bad_function( x,y ):
    if x==1:
        print("hello world")
    return x+y
'''
    
    try:
        test_file.write_text(test_content)
        
        # Test ruff check
        if not run_command("uv run ruff check test_ruff_temp.py", "ruff check on test file", capture_output=False):
            print("⚠️ ruff check found issues (expected)")
        
        # Test ruff format
        if not run_command("uv run ruff format test_ruff_temp.py", "ruff format on test file"):
            return False
        
        # Check if file was formatted
        formatted_content = test_file.read_text()
        if formatted_content != test_content:
            print("✅ ruff format successfully modified the file")
        else:
            print("⚠️ ruff format didn't change the file")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ruff functionality: {e}")
        return False
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()


def test_dependency_installation():
    """Test if dependencies can be installed"""
    print("\n📦 Testing dependency installation...")
    
    # Test core installation
    if not run_command("uv pip install -e . --dry-run", "core dependencies dry run"):
        return False
    
    # Test dev installation
    if not run_command("uv pip install -e '.[dev]' --dry-run", "dev dependencies dry run"):
        return False
    
    return True


def show_summary(results):
    """Show test summary"""
    print("\n" + "="*60)
    print("🎯 BharatVerse uv + ruff Setup Test Results")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed")
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! uv and ruff setup is working correctly.")
        print("\n🚀 You can now use:")
        print("  • uv pip install -e . (install dependencies)")
        print("  • uv run ruff check . (check code)")
        print("  • uv run ruff format . (format code)")
        print("  • make check (run all checks)")
        print("  • make fix (auto-fix issues)")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} tests failed. Please check the issues above.")
        print("\n🔧 Troubleshooting:")
        print("  • Run: python scripts/migrate_to_uv_ruff.py")
        print("  • Check: UV_RUFF_GUIDE.md")
        print("  • Ensure uv is installed: curl -LsSf https://astral.sh/uv/install.sh | sh")


def main():
    """Main test function"""
    print("🇮🇳 BharatVerse - uv & ruff Setup Test")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Please run this script from the project root.")
        sys.exit(1)
    
    print(f"📁 Working directory: {Path.cwd()}")
    
    # Run all tests
    tests = {
        "uv Installation": test_uv_installation,
        "ruff Installation": test_ruff_installation,
        "Project Structure": test_project_structure,
        "pyproject.toml Configuration": test_pyproject_toml,
        "Make Commands": test_make_commands,
        "ruff Functionality": test_ruff_functionality,
        "Dependency Installation": test_dependency_installation,
    }
    
    results = {}
    
    for test_name, test_func in tests.items():
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} - Exception: {e}")
            results[test_name] = False
    
    # Show summary
    show_summary(results)
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()