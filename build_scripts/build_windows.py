#!/usr/bin/env python3
"""
Windows build script for Duplicate Photo Cleaner
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    
    print("✓ Success")
    return True

def main():
    print("=" * 60)
    print("  BUILDING DUPLICATE PHOTO CLEANER FOR WINDOWS")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing requirements"):
        sys.exit(1)
    
    # Clean previous builds
    if Path("build").exists():
        shutil.rmtree("build")
    if Path("dist").exists():
        shutil.rmtree("dist")
    
    # Build with PyInstaller
    pyinstaller_command = [
        "pyinstaller",
        "--onedir",
        "--windowed",
        "--name=DuplicatePhotoCleaner",
        "--add-data=src;src",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=bcrypt._bcrypt",
        "--distpath=dist",
        "main.py"
    ]
    
    if not run_command(" ".join(pyinstaller_command), "Building executable"):
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("  BUILD COMPLETE!")
    print("=" * 60)
    print(f"  Executable location: {Path('dist/DuplicatePhotoCleaner').absolute()}")
    print("  Run: dist/DuplicatePhotoCleaner/DuplicatePhotoCleaner.exe")

if __name__ == "__main__":
    main()
