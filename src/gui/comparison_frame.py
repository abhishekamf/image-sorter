"""
Frame for comparing and managing duplicate images
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from pathlib import Path
from PIL import Image, ImageTk

class ComparisonFrame(ttk.Frame):
    def __init__(self, parent, detector, db, user):
        super().__init__(parent)
        self.detector = detector
        self.db = db
        self.user = user
        self.duplicates = []
        self.current_index = 0
        
        self.setup_ui()

    def setup_ui(self):
        """Setup the comparison UI"""
        # Progress frame (hidden initially)
        self.progress_frame = ttk.Frame(self)
        
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(fill='x', padx=20, pady=5)
        
        # Main content frame
        content_frame = ttk.Frame(self)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Control buttons
        control_frame = ttk.Frame(content_frame)
        control_frame.pack(fill='x', pady=(0, 20))
        
        self.scan_btn = ttk.Button(control_frame, text="Select Folder & Scan", 
                                  command=self.select_and_scan)
        self.scan_btn.pack(side='left')
        
        self.stop_btn = ttk.Button(control_frame, text="Stop Scan", 
                                  command=self.stop_scan, state='disabled')
        self.stop_btn.pack(side='left', padx=(10, 0))
        
        # Image comparison frame
        comparison_frame = ttk.Frame(content_frame)
        comparison_frame.pack(fill='both', expand=True)
        
        # Original image frame
        original_frame = ttk.LabelFrame(comparison_frame, text="Original (Keep)")
        original_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.original_label = ttk.Label(original_frame, text="No scan in progress", 
                                       anchor='center')
        self.original_label.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Duplicate image frame
        duplicate_frame = ttk.LabelFrame(comparison_frame, text="Duplicate (Will be moved)")
        duplicate_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        self.duplicate_label = ttk.Label(duplicate_frame, text="No scan in progress", 
                                        anchor='center')
        self.duplicate_label.pack(expand=True, fill='both', padx=10, pady=10)
        
        # File info frame
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill='x', pady=10)
        
        self.original_info = ttk.Label(info_frame, text="")
        self.original_info.pack(side='left')
        
        self.duplicate_info = ttk.Label(info_frame, text="")
        self.duplicate_info.pack(side='right')
        
        # Action buttons
        action_frame = ttk.Frame(content_frame)
        action_frame.pack(pady=20)
        
        self.keep_original_btn = ttk.Button(action_frame, text="Keep Original & Remove Duplicate", 
                                           command=self.keep_original, state='disabled')
        self.keep_original_btn.pack(side='left', padx=5)
        
        self.skip_btn = ttk.Button(action_frame, text="Skip This Pair", 
                                  command=self.skip_pair, state='disabled')
        self.skip_btn.pack(side='left', padx=5)
        
        # Status
        self.status_label = ttk.Label(content_frame, text="Ready to scan for duplicates")
        self.status_label.pack(side='bottom', anchor='w')

    def select_and_scan(self):
        """Open folder dialog and start scanning"""
        from tkinter import filedialog
        folder_path = filedialog.askdirectory(title="Select folder containing photos")
        if folder_path:
            self.start_scan(folder_path)

    def start_scan(self, folder_path):
        """Start scanning for duplicates"""
        self.duplicates = []
        self.current_index = 0
        
        # Show progress
        self.progress_frame.pack(fill='x', pady=10, before=self.winfo_children()[1])
        self.progress_bar['value'] = 0
        
        # Update UI state
        self.scan_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.keep_original_btn.config(state='disabled')
        self.skip_btn.config(state='disabled')
        
        self.status_label.config(text=f"Scanning: {folder_path}")
        
        # Start scanning in a separate thread
        scan_thread = threading.Thread(target=self.scan_worker, args=(folder_path,))
        scan_thread.daemon = True
        scan_thread.start()

    def scan_worker(self, folder_path):
        """Worker thread for scanning"""
        def progress_callback(current, total, file_path):
            self.after(0, self.update_progress, current, total, file_path)
        
        try:
            duplicates = self.detector.find_duplicates(folder_path, progress_callback)
            self.after(0, self.scan_completed, duplicates)
        except Exception as e:
            self.after(0, self.scan_error, str(e))

    def update_progress(self, current, total, file_path):
        """Update progress bar and label"""
        self.progress_bar.config(value=current, maximum=total)
        filename = Path(file_path).name
        self.progress_label.config(text=f"Processing: {filename} ({current}/{total})")

    def scan_completed(self, duplicates):
        """Handle scan completion"""
        self.progress_frame.pack_forget()
        self.duplicates = duplicates
        
        # Update UI state
        self.scan_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        if duplicates:
            self.current_index = 0
            self.keep_original_btn.config(state='normal')
            self.skip_btn.config(state='normal')
            self.status_label.config(text=f"Found {len(duplicates)} duplicate pairs")
            self.show_current_pair()
        else:
            self.status_label.config(text="No duplicates found!")
            self.original_label.config(image='', text="No duplicates found")
            self.duplicate_label.config(image='', text="No duplicates found")

    def scan_error(self, error_msg):
        """Handle scan error"""
        self.progress_frame.pack_forget()
        self.scan_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="Scan failed")
        messagebox.showerror("Scan Error", f"An error occurred during scanning:\n{error_msg}")

    def stop_scan(self):
        """Stop the current scan"""
        self.detector.stop_scanning()
        self.progress_frame.pack_forget()
        self.scan_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="Scan stopped")

    def show_current_pair(self):
        """Display the current duplicate pair"""
        if self.current_index >= len(self.duplicates):
            self.show_completion()
            return
        
        pair = self.duplicates[self.current_index]
        
        # Load and display images
        self.load_image(self.original_label, pair['original'])
        self.load_image(self.duplicate_label, pair['duplicate'])
        
        # Update info labels
        original_name = Path(pair['original']).name
        duplicate_name = Path(pair['duplicate']).name
        
        self.original_info.config(text=f"File: {original_name}")
        self.duplicate_info.config(text=f"File: {duplicate_name}")
        
        self.status_label.config(text=f"Pair {self.current_index + 1} of {len(self.duplicates)}")

    def load_image(self, label, image_path):
        """Load and display an image in the given label"""
        try:
            # Open and resize image
            with Image.open(image_path) as img:
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                label.config(image=photo, text='')
                label.image = photo  # Keep a reference
        except Exception as e:
            label.config(image='', text=f"Error loading image:\n{Path(image_path).name}")
            label.image = None

    def keep_original(self):
        """Keep original and move duplicate to holding folder"""
        if self.current_index >= len(self.duplicates):
            return
        
        pair = self.duplicates[self.current_index]
        
        # Get holding folder from settings
        settings = self.db.get_settings(self.user['id'])
        holding_folder = settings[1] if settings else str(Path.home() / ".duplicate_photo_cleaner" / "holding")
        
        try:
            # Move duplicate to holding folder
            moved_path = self.detector.move_to_holding(pair['duplicate'], holding_folder)
            
            # Move to next pair
            self.current_index += 1
            self.show_current_pair()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to move file to holding folder:\n{str(e)}")

    def skip_pair(self):
        """Skip the current pair without taking action"""
        self.current_index += 1
        self.show_current_pair()

    def show_completion(self):
        """Show completion message"""
        self.keep_original_btn.config(state='disabled')
        self.skip_btn.config(state='disabled')
        self.status_label.config(text="All duplicates processed!")
        
        self.original_label.config(image='', text="All duplicates processed!")
        self.duplicate_label.config(image='', text="Check the Holding Folder tab")
        
        messagebox.showinfo("Complete", "All duplicate pairs have been processed!")
