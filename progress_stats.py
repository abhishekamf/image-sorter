"""
Beautiful progress indicators and statistics
"""
import tkinter as tk
from tkinter import ttk
import threading
import time

class AnimatedProgress:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.progress = ttk.Progressbar(self.frame, mode='determinate', length=400)
        self.label = ttk.Label(self.frame, text="Ready to scan...")
        self.stats_label = ttk.Label(self.frame, text="")
        
        self.label.pack(pady=5)
        self.progress.pack(pady=10, padx=20, fill='x')
        self.stats_label.pack(pady=5)
        
    def update_progress(self, current, total, filename="", stats=None):
        """Update progress bar with animation"""
        percentage = (current / total) * 100 if total > 0 else 0
        self.progress['value'] = percentage
        
        # Animated text
        dots = "." * (current % 4)
        self.label.config(text=f"Scanning {filename}{dots}")
        
        if stats:
            self.stats_label.config(
                text=f"📁 Files: {stats.get('files', 0)} | "
                     f"🖼️ Images: {stats.get('images', 0)} | "
                     f"🔍 Duplicates: {stats.get('duplicates', 0)} | "
                     f"💾 Space to save: {stats.get('space_saved', '0 MB')}"
            )

class Statistics:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.files_scanned = 0
        self.images_found = 0
        self.duplicates_found = 0
        self.space_that_can_be_saved = 0
        self.scan_time = 0
        
    def calculate_space_saved(self, duplicate_files):
        """Calculate how much space can be saved"""
        total_bytes = 0
        for dup_info in duplicate_files:
            try:
                duplicate_path = dup_info.get('duplicate', '')
                if os.path.exists(duplicate_path):
                    total_bytes += os.path.getsize(duplicate_path)
            except:
                pass
        
        # Convert to human readable format
        if total_bytes < 1024:
            return f"{total_bytes} B"
        elif total_bytes < 1024**2:
            return f"{total_bytes/1024:.1f} KB"
        elif total_bytes < 1024**3:
            return f"{total_bytes/(1024**2):.1f} MB"
        else:
            return f"{total_bytes/(1024**3):.1f} GB"
    
    def get_summary(self):
        """Get a beautiful summary of the scan"""
        return {
            'files': self.files_scanned,
            'images': self.images_found,
            'duplicates': self.duplicates_found,
            'space_saved': self.calculate_space_saved([])
        }
