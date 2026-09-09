#!/usr/bin/env python3
"""
Duplicate Photo Cleaner - Main Entry Point
"""
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def main():
    try:
        from gui.main_window import DuplicatePhotoCleanerApp
        import tkinter as tk
        
        root = tk.Tk()
        app = DuplicatePhotoCleanerApp(root)
        root.mainloop()
        
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
