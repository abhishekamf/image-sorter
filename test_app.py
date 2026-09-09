#!/usr/bin/env python3
"""
Test script to verify the application works before building
"""
import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import tkinter as tk
        print("✓ tkinter")
        
        import PIL
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

def test_database():
    """Test database operations"""
    print("\nTesting database...")
    
    try:
        from database.manager import DatabaseManager
        
        # Use temporary database
        db = DatabaseManager(":memory:")
        
        # Test user registration
        user_id = db.register_user("testuser", "testpass123")
        if user_id:
            print("✓ User registration")
        else:
            print("✗ User registration failed")
            return False
        
        # Test authentication
        auth_id = db.authenticate_user("testuser", "testpass123")
        if auth_id == user_id:
            print("✓ User authentication")
        else:
            print("✗ User authentication failed")
            return False
        
        db.close()
        print("✓ Database tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def main():
    print("=" * 50)
    print("  DUPLICATE PHOTO CLEANER - TEST")
    print("=" * 50)
    
    success = True
    
    if not test_imports():
        success = False
    
    if not test_database():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("  ✓ ALL TESTS PASSED!")
        print("  Ready to build or run the application")
    else:
        print("  ✗ SOME TESTS FAILED!")
        print("  Please fix the issues before proceeding")
    print("=" * 50)

if __name__ == "__main__":
    main()
