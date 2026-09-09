#!/usr/bin/env python3
"""
Simple test for CI environment
"""
import sys
import os
from pathlib import Path

def main():
    print("=" * 50)
    print("  TESTING DUPLICATE PHOTO CLEANER")
    print("=" * 50)
    
    # Add src to Python path
    project_root = Path(__file__).parent
    src_path = project_root / 'src'
    sys.path.insert(0, str(src_path))
    
    print("✓ Project structure check...")
    
    # Check if main files exist
    required_files = [
        'main.py',
        'requirements.txt',
        'src/database/manager.py',
        'src/core/duplicate_detector.py',
        'src/gui/main_window.py'
    ]
    
    for file in required_files:
        if (project_root / file).exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - MISSING")
            sys.exit(1)
    
    print("\n✓ Import tests...")
    
    try:
        # Test basic imports
        import sqlite3
        print("✓ sqlite3")
        
        from PIL import Image
        print("✓ Pillow")
        
        import bcrypt
        print("✓ bcrypt")
        
        # Test our modules (without GUI)
        from database.manager import DatabaseManager
        print("✓ DatabaseManager")
        
        from core.duplicate_detector import DuplicateDetector
        print("✓ DuplicateDetector")
        
        print("\n✓ Database test...")
        
        # Quick database test
        db = DatabaseManager(":memory:")
        user_id = db.register_user("test", "test123")
        if user_id and db.authenticate_user("test", "test123") == user_id:
            print("✓ Database operations")
            db.close()
        else:
            print("✗ Database operations failed")
            sys.exit(1)
        
        print("\n🎉 ALL TESTS PASSED!")
        print("Ready for build!")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
