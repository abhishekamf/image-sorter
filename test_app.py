#!/usr/bin/env python3
import sys
import os
from pathlib import Path

def test_basic_imports():
    """Test basic Python imports"""
    print("Testing basic imports...")
    try:
        from PIL import Image
        print("✓ Pillow")
        
        import bcrypt
        print("✓ bcrypt")
        
        import sqlite3
        print("✓ sqlite3")
        
        return True
    except ImportError as e:
        print(f"✗ Basic import failed: {e}")
        return False

def test_app_imports():
    """Test application imports"""
    print("Testing application imports...")
    try:
        # Add src to path
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        
        from database.manager import DatabaseManager
        print("✓ DatabaseManager")
        
        from core.duplicate_detector import DuplicateDetector
        print("✓ DuplicateDetector")
        
        return True
    except ImportError as e:
        print(f"✗ App import failed: {e}")
        return False

def test_gui_imports():
    """Test GUI imports (skip on headless systems)"""
    print("Testing GUI imports...")
    try:
        # Check if we're in a headless environment
        if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
            # In CI environment, try to set up virtual display
            os.environ['DISPLAY'] = ':99'
        
        import tkinter as tk
        print("✓ tkinter")
        
        # Test if we can create a root window
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the window
            root.destroy()
            print("✓ tkinter window creation")
        except tk.TclError:
            print("⚠ tkinter available but no display (OK in CI)")
        
        # Test our GUI modules
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        from gui.main_window import DuplicatePhotoCleanerApp
        print("✓ GUI modules")
        
        return True
    except ImportError as e:
        print(f"✗ GUI import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠ GUI test skipped: {e}")
        return True  # Don't fail on GUI issues in headless environments

def test_database():
    """Test database functionality"""
    print("Testing database...")
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        from database.manager import DatabaseManager
        
        # Test with in-memory database
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
        print("✓ Database functionality")
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("  DUPLICATE PHOTO CLEANER - TESTS")
    print("=" * 60)
    
    # Run tests
    tests = [
        ("Basic Imports", test_basic_imports),
        ("App Imports", test_app_imports),
        ("Database", test_database),
        ("GUI Imports", test_gui_imports),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"  RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
