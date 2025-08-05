#!/usr/bin/env python3
"""
BharatVerse - Migration Script to uv and ruff
This script helps migrate from the old toolchain (poetry, black, isort, flake8, pylint) to uv and ruff.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return success status"""
    print(f"🔄 {description}")
    print(f"   Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"   Error: {e.stderr}")
        return False


def check_uv_installed():
    """Check if uv is installed"""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("✅ uv is already installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ uv is not installed")
        return False


def install_uv():
    """Install uv package manager"""
    print("📦 Installing uv...")
    
    # Try different installation methods
    install_commands = [
        "curl -LsSf https://astral.sh/uv/install.sh | sh",
        "pip install uv",
        "pipx install uv"
    ]
    
    for cmd in install_commands:
        print(f"   Trying: {cmd}")
        if run_command(cmd, "Installing uv"):
            # Reload PATH
            os.environ["PATH"] = f"{os.path.expanduser('~/.cargo/bin')}:{os.environ.get('PATH', '')}"
            return True
    
    print("❌ Failed to install uv. Please install manually:")
    print("   Visit: https://docs.astral.sh/uv/getting-started/installation/")
    return False


def remove_old_dependencies():
    """Remove old development dependencies"""
    print("🧹 Cleaning up old dependencies...")
    
    old_packages = [
        "black", "isort", "flake8", "pylint", "poetry"
    ]
    
    for package in old_packages:
        run_command(f"pip uninstall -y {package}", f"Removing {package}")


def install_new_dependencies():
    """Install dependencies with uv"""
    print("📦 Installing dependencies with uv...")
    
    # Install core dependencies
    if not run_command("uv pip install -e .", "Installing core dependencies"):
        return False
    
    # Install development dependencies
    if not run_command("uv pip install -e '.[dev]'", "Installing development dependencies"):
        return False
    
    return True


def setup_pre_commit():
    """Setup pre-commit hooks"""
    print("🔗 Setting up pre-commit hooks...")
    
    if not run_command("uv pip install pre-commit", "Installing pre-commit"):
        return False
    
    if not run_command("pre-commit install", "Installing pre-commit hooks"):
        return False
    
    return True


def run_initial_checks():
    """Run initial code quality checks"""
    print("🔍 Running initial code quality checks...")
    
    # Format code
    run_command("uv run ruff format .", "Formatting code with ruff")
    
    # Fix linting issues
    run_command("uv run ruff check --fix .", "Fixing linting issues")
    
    # Run final check
    run_command("uv run ruff check .", "Final linting check")


def show_migration_summary():
    """Show migration summary and next steps"""
    print("\n" + "="*60)
    print("🎉 Migration to uv and ruff completed!")
    print("="*60)
    
    print("\n📋 What changed:")
    print("• Dependency management: poetry → uv")
    print("• Code formatting: black → ruff format")
    print("• Import sorting: isort → ruff (I rules)")
    print("• Linting: flake8 + pylint → ruff check")
    print("• All-in-one: Multiple tools → Single ruff tool")
    
    print("\n🚀 New commands:")
    print("• Install deps: uv pip install -e .")
    print("• Format code: uv run ruff format .")
    print("• Check code: uv run ruff check .")
    print("• Fix issues: uv run ruff check --fix .")
    print("• Run tests: uv run pytest tests/")
    print("• All checks: make check")
    
    print("\n📚 Resources:")
    print("• Read UV_RUFF_GUIDE.md for detailed usage")
    print("• Use 'make help' to see all available commands")
    print("• Pre-commit hooks are now active")
    
    print("\n✨ Benefits:")
    print("• 10-100x faster than old tools")
    print("• Single tool for all code quality")
    print("• Better dependency resolution")
    print("• Modern Python toolchain")


def main():
    """Main migration process"""
    print("🇮🇳 BharatVerse - Migration to uv and ruff")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Check current directory
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Step 1: Install uv if not present
    if not check_uv_installed():
        if not install_uv():
            sys.exit(1)
    
    # Step 2: Remove old dependencies (optional)
    response = input("\n🗑️  Remove old tools (black, isort, flake8, pylint, poetry)? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        remove_old_dependencies()
    
    # Step 3: Install new dependencies
    if not install_new_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Step 4: Setup pre-commit
    response = input("\n🔗 Setup pre-commit hooks? (Y/n): ").strip().lower()
    if response not in ['n', 'no']:
        setup_pre_commit()
    
    # Step 5: Run initial checks
    response = input("\n🔍 Run initial code formatting and checks? (Y/n): ").strip().lower()
    if response not in ['n', 'no']:
        run_initial_checks()
    
    # Step 6: Show summary
    show_migration_summary()
    
    print("\n🎯 Next steps:")
    print("1. Review the changes made by ruff")
    print("2. Commit the formatted code")
    print("3. Update your IDE to use ruff")
    print("4. Read UV_RUFF_GUIDE.md for detailed usage")
    
    print("\n✅ Migration completed successfully!")


if __name__ == "__main__":
    main()