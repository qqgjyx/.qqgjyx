#!/usr/bin/env python3
"""
Automated deployment script for qqgjyx.

Usage:
    python deploy.py [--version VERSION] [--message MESSAGE] [--skip-tests] [--skip-upload]
    
Examples:
    python deploy.py --version 0.1.3 --message "Add new feature"
    python deploy.py --skip-tests  # Skip running tests
    python deploy.py --skip-upload  # Skip PyPI upload
"""

import argparse
import subprocess
import sys
import os
import re
from pathlib import Path


def run_command(cmd, check=True, capture_output=True):
    """Run a shell command and return result."""
    print(f"🔄 Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=check, 
            capture_output=capture_output,
            text=True
        )
        if capture_output and result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def get_current_version():
    """Get current version from __init__.py."""
    init_file = Path("src/qqgjyx/__init__.py")
    with open(init_file) as f:
        content = f.read()
        match = re.search(r'__version__ = "([^"]+)"', content)
        if match:
            return match.group(1)
    raise ValueError("Could not find version in __init__.py")


def update_version(new_version):
    """Update version in both __init__.py and pyproject.toml."""
    print(f"📝 Updating version to {new_version}")
    
    # Update __init__.py
    init_file = Path("src/qqgjyx/__init__.py")
    with open(init_file) as f:
        content = f.read()
    content = re.sub(r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', content)
    with open(init_file, 'w') as f:
        f.write(content)
    
    # Update pyproject.toml
    pyproject_file = Path("pyproject.toml")
    with open(pyproject_file) as f:
        content = f.read()
    content = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content)
    with open(pyproject_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Version updated to {new_version}")


def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    
    # Install package in editable mode
    run_command("conda run -n pkg-dev python -m pip install -e .")
    
    # Run tests
    result = run_command("conda run -n pkg-dev python -m pytest test/ -v")
    
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed!")
        sys.exit(1)


def build_package():
    """Build the package."""
    print("📦 Building package...")
    
    # Clean previous builds
    run_command("rm -rf dist build")
    
    # Build
    result = run_command("conda run -n pkg-dev python -m build")
    
    if result.returncode == 0:
        print("✅ Package built successfully!")
    else:
        print("❌ Build failed!")
        sys.exit(1)


def validate_package():
    """Validate the built package."""
    print("🔍 Validating package...")
    
    result = run_command("conda run -n pkg-dev twine check dist/*")
    
    if result.returncode == 0:
        print("✅ Package validation passed!")
    else:
        print("❌ Package validation failed!")
        sys.exit(1)


def upload_package():
    """Upload package to PyPI."""
    print("🚀 Uploading to PyPI...")
    
    result = run_command("conda run -n pkg-dev twine upload dist/*")
    
    if result.returncode == 0:
        print("✅ Package uploaded successfully!")
    else:
        print("❌ Upload failed!")
        sys.exit(1)


def git_commit_and_tag(version, message):
    """Commit changes and create git tag."""
    print("📝 Committing changes...")
    
    # Add all changes
    run_command("git add -A")
    
    # Commit
    commit_msg = f"Release {version}: {message}" if message else f"Release {version}"
    run_command(f'git commit -m "{commit_msg}"')
    
    # Create tag
    run_command(f'git tag -a v{version} -m "qqgjyx {version}"')
    
    # Push
    run_command("git push")
    run_command("git push --tags")
    
    print(f"✅ Git commit and tag v{version} created!")


def check_git_status():
    """Check git status and warn about uncommitted changes."""
    result = run_command("git status --porcelain", check=False)
    if result.stdout.strip():
        print("⚠️  Warning: You have uncommitted changes:")
        print(result.stdout)
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Deploy qqgjyx package")
    parser.add_argument("--version", help="New version number (e.g., 0.1.3)")
    parser.add_argument("--message", help="Commit message")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-upload", action="store_true", help="Skip PyPI upload")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without executing")
    
    args = parser.parse_args()
    
    print("🚀 qqgjyx Deployment Script")
    print("=" * 40)
    
    # Check git status
    check_git_status()
    
    # Get current version
    current_version = get_current_version()
    print(f"📋 Current version: {current_version}")
    
    # Determine new version
    if args.version:
        new_version = args.version
    else:
        # Auto-increment patch version
        parts = current_version.split('.')
        parts[-1] = str(int(parts[-1]) + 1)
        new_version = '.'.join(parts)
    
    print(f"🎯 Target version: {new_version}")
    
    if args.dry_run:
        print("\n🔍 DRY RUN - Would execute:")
        print(f"  1. Update version to {new_version}")
        print("  2. Run tests" + (" (SKIPPED)" if args.skip_tests else ""))
        print("  3. Build package")
        print("  4. Validate package")
        print("  5. Upload to PyPI" + (" (SKIPPED)" if args.skip_upload else ""))
        print("  6. Commit and tag")
        return
    
    # Update version
    update_version(new_version)
    
    # Run tests
    if not args.skip_tests:
        run_tests()
    else:
        print("⏭️  Skipping tests")
    
    # Build package
    build_package()
    
    # Validate package
    validate_package()
    
    # Upload package
    if not args.skip_upload:
        upload_package()
    else:
        print("⏭️  Skipping PyPI upload")
    
    # Git operations
    git_commit_and_tag(new_version, args.message)
    
    print("\n🎉 Deployment completed successfully!")
    print(f"📦 Package: qqgjyx {new_version}")
    print(f"🔗 PyPI: https://pypi.org/project/qqgjyx/{new_version}/")
    print(f"🏷️  Tag: v{new_version}")


if __name__ == "__main__":
    main()
