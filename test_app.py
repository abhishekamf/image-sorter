#!/usr/bin/env python3
import sys
from pathlib import Path

def main():
    print("Testing application...")
    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from gui.main_window import DuplicatePhotoCleanerApp
        print("✓ All imports successful!")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
