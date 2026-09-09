#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from gui.app import DuplicatePhotoCleaner
from tkinter import Tk

def main():
    try:
        from PIL import Image
        import bcrypt
    except ImportError:
        print("Install requirements: pip install -r requirements.txt")
        sys.exit(1)
    root = Tk()
    app = DuplicatePhotoCleaner(root)
    root.mainloop()

if __name__ == "__main__":
    main()
