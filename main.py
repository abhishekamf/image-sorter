#!/usr/bin/env python3
"""
Duplicate Photo Cleaner - Main Entry Point
"""
import sys
import os
import tkinter as tk
from pathlib import Path

# Add src directory to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

def main():
    try:
        # Check dependencies
        import PIL
        import bcrypt
        print("✓ All dependencies loaded successfully")
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Import and run the application
    from gui.main_window import DuplicatePhotoCleanerApp
    
    root = tk.Tk()
    app = DuplicatePhotoCleanerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
