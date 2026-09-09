#!/usr/bin/env python3
import sys
from pathlib import Path

def test_imports():
    print("Testing imports...")
    try:
        import tkinter as tk
        print("✓ tkinter")
        
        from PIL import Image
        print("✓ Pillow")
        
        import bcrypt
        print("✓ bcrypt")
        
        # Test our modules
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        
        from database.manager import DatabaseManager
        print("✓ DatabaseManager")
        
        from core.duplicate_detector import DuplicateDetector
        print("✓ DuplicateDetector")
        
        from gui.main_window import DuplicatePhotoCleanerApp
        print("✓ GUI modules")
        
        print("\n✓ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n✗ Import failed: {e}")
        return False

def main():
    print("=" * 50)
    print("  DUPLICATE PHOTO CLEANER - TEST")
    print("=" * 50)
    
    if test_imports():
        print("\n✓ ALL TESTS PASSED!")
        print("Ready to build!")
    else:
        print("\n✗ TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
