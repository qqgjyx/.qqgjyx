#!/usr/bin/env python3
"""
Automated deployment script for qqgjyx.

Usage:
    python deploy.py [--version VERSION] [--message MESSAGE] [--skip-tests] [--skip-upload] [--all-tests] [--dry-run]
    
Examples:
    python deploy.py --version 0.1.3 --message "Add new feature"
    python deploy.py --skip-tests  # Skip running tests
    python deploy.py --skip-upload  # Skip PyPI upload
    python deploy.py --all-tests  # Run full suite (may require optional deps)
"""

import argparse
import subprocess
import sys
import re
from pathlib import Path


def run_command(cmd, check=True, capture_output=True):
    print(f"🔄 Running: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=capture_output,
            text=True,
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
    init_file = Path("src/qqgjyx/__init__.py")
    with open(init_file) as f:
        content = f.read()
        match = re.search(r'__version__ = "([^"]+)"', content)
        if match:
            return match.group(1)
    raise ValueError("Could not find version in __init__.py")


def update_version(new_version: str) -> None:
    print(f"📝 Updating version to {new_version}")

    init_file = Path("src/qqgjyx/__init__.py")
    init_text = init_file.read_text()
    init_text = re.sub(r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', init_text)
    init_file.write_text(init_text)

    pyproject_file = Path("pyproject.toml")
    py_text = pyproject_file.read_text()
    py_text = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', py_text)
    pyproject_file.write_text(py_text)

    print(f"✅ Version updated to {new_version}")


def run_tests(run_all: bool = False) -> None:
    print("🧪 Running tests...")
    # Install editable
    run_command("conda run -n pkg-dev python -m pip install -e .")
    # Prefer lightweight tests by default
    test_target = "test/" if run_all else "test/test_basic.py"
    result = run_command(f"conda run -n pkg-dev python -m pytest {test_target} -v")
    if result.returncode == 0:
        print("✅ Tests passed!")
    else:
        print("❌ Tests failed!")
        sys.exit(1)


def build_package() -> None:
    print("📦 Building package...")
    run_command("rm -rf dist build")
    result = run_command("conda run -n pkg-dev python -m build")
    if result.returncode == 0:
        print("✅ Package built successfully!")
    else:
        print("❌ Build failed!")
        sys.exit(1)


def validate_package() -> None:
    print("🔍 Validating package...")
    result = run_command("conda run -n pkg-dev twine check dist/*")
    if result.returncode == 0:
        print("✅ Package validation passed!")
    else:
        print("❌ Package validation failed!")
        sys.exit(1)


def upload_package() -> None:
    print("🚀 Uploading to PyPI...")
    result = run_command("conda run -n pkg-dev twine upload dist/*")
    if result.returncode == 0:
        print("✅ Package uploaded successfully!")
    else:
        print("❌ Upload failed!")
        sys.exit(1)


def git_commit_and_tag(version: str, message: str | None) -> None:
    print("📝 Committing changes...")
    run_command("git add -A")
    commit_msg = f"Release {version}: {message}" if message else f"Release {version}"
    run_command(f'git commit -m "{commit_msg}"')
    run_command(f'git tag -a v{version} -m "qqgjyx {version}"')
    run_command("git push")
    run_command("git push --tags")
    print(f"✅ Git commit and tag v{version} created!")


def check_git_status() -> None:
    result = run_command("git status --porcelain", check=False)
    if result.stdout.strip():
        print("⚠️  Warning: You have uncommitted changes:")
        print(result.stdout)
        response = input("Continue anyway? (y/N): ")
        if response.lower() != "y":
            sys.exit(0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy qqgjyx package")
    parser.add_argument("--version", help="New version number (e.g., 0.1.3)")
    parser.add_argument("--message", help="Commit message")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-upload", action="store_true", help="Skip PyPI upload")
    parser.add_argument("--all-tests", action="store_true", help="Run full test suite (may require optional deps)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without executing")

    args = parser.parse_args()

    print("🚀 qqgjyx Deployment Script")
    print("=" * 40)

    check_git_status()

    current_version = get_current_version()
    print(f"📋 Current version: {current_version}")

    new_version = args.version if args.version else ".".join([*current_version.split(".")[:-1], str(int(current_version.split(".")[-1]) + 1)])
    print(f"🎯 Target version: {new_version}")

    if args.dry_run:
        print("\n🔍 DRY RUN - Would execute:")
        print(f"  1. Update version to {new_version}")
        print("  2. Run tests" + (" (SKIPPED)" if args.skip_tests else (" (ALL)" if args.all_tests else " (BASIC)")))
        print("  3. Build package")
        print("  4. Validate package")
        print("  5. Upload to PyPI" + (" (SKIPPED)" if args.skip_upload else ""))
        print("  6. Commit and tag")
        return

    update_version(new_version)

    if not args.skip_tests:
        run_tests(run_all=args.all_tests)
    else:
        print("⏭️  Skipping tests")

    build_package()
    validate_package()

    if not args.skip_upload:
        upload_package()
    else:
        print("⏭️  Skipping PyPI upload")

    git_commit_and_tag(new_version, args.message)

    print("\n🎉 Deployment completed successfully!")
    print(f"📦 Package: qqgjyx {new_version}")
    print(f"🔗 PyPI: https://pypi.org/project/qqgjyx/{new_version}/")
    print(f"🏷️  Tag: v{new_version}")


if __name__ == "__main__":
    main()
