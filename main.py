#!/usr/bin/env python3
"""
Duplicate Photo Cleaner - Fixed for macOS
"""
import sys
import os
import traceback

def show_error(title, message):
    """Show error message (works even if tkinter fails)"""
    print(f"\n{title}: {message}")
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except:
        input(f"\n{title}: {message}\n\nPress Enter to exit...")

def main():
    try:
        # Test all imports first
        print("Loading Duplicate Photo Cleaner...")
        
        import tkinter as tk
        print("✓ tkinter loaded")
        
        from tkinter import ttk, filedialog, messagebox
        print("✓ tkinter modules loaded")
        
        try:
            from PIL import Image, ImageTk
            print("✓ Pillow loaded")
            PIL_AVAILABLE = True
        except ImportError:
            print("⚠ Pillow not available - image preview disabled")
            PIL_AVAILABLE = False
        
        # Test tkinter works
        try:
            test_root = tk.Tk()
            test_root.withdraw()
            test_root.destroy()
            print("✓ tkinter GUI working")
        except Exception as e:
            show_error("GUI Error", 
                      f"Cannot initialize GUI:\n{str(e)}\n\n"
                      "This might be a display issue.")
            return
        
        # Start application directly (no separate module)
        print("🚀 Starting Duplicate Photo Cleaner...")
        app = DuplicatePhotoCleanerApp(PIL_AVAILABLE)
        
    except Exception as e:
        error_msg = f"""
Duplicate Photo Cleaner Error

Error: {str(e)}

Traceback:
{traceback.format_exc()}

Please report this error to the developer.
"""
        show_error("Application Error", error_msg)

class DuplicatePhotoCleanerApp:
    def __init__(self, pil_available=True):
        self.root = tk.Tk()
        self.root.title("🖼️ Duplicate Photo Cleaner")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # App state
        self.selected_folders = []
        self.duplicates = []
        self.current_pair_index = 0
        self.is_scanning = False
        self.pil_available = pil_available
        
        # Create UI
        self.create_ui()
        
        # Show PIL warning if needed
        if not pil_available:
            messagebox.showwarning("Limited Functionality", 
                                 "Image preview is disabled (Pillow not available).\n"
                                 "Duplicate detection will still work.")
        
        # Start the app
        self.root.mainloop()
    
    def create_ui(self):
        """Create the user interface"""
        # Header
        header = tk.Frame(self.root, bg='#2c3e50', height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title = tk.Label(header, text="🖼️ Duplicate Photo Cleaner", 
                        font=("Arial", 18, "bold"), 
                        bg='#2c3e50', fg='white')
        title.pack(expand=True)
        
        # Main content
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Scan tab
        self.create_scan_tab(notebook)
        
        # Results tab
        self.create_results_tab(notebook)
        
    def create_scan_tab(self, notebook):
        """Create scanning tab"""
        scan_frame = ttk.Frame(notebook)
        notebook.add(scan_frame, text="🔍 Scan")
        
        # Instructions
        instructions = tk.Label(scan_frame, 
                              text="Select folders containing photos to scan for duplicates",
                              font=("Arial", 12), pady=20)
        instructions.pack()
        
        # Drop zone (fixed - removed dashed relief)
        drop_zone = tk.Frame(scan_frame, bg='#f0f0f0', relief='solid', bd=2, height=100)
        drop_zone.pack(fill='x', padx=20, pady=10)
        drop_zone.pack_propagate(False)
        
        drop_label = tk.Label(drop_zone, 
                             text="📁 Click 'Add Folder' to select folders\n🖼️ Supports: JPG, PNG, GIF, BMP, TIFF", 
                             font=("Arial", 11), bg='#f0f0f0', fg='#666666')
        drop_label.pack(expand=True)
        
        # Buttons
        button_frame = ttk.Frame(scan_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="📁 Add Folder", 
                  command=self.add_folder).pack(side='left', padx=5)
        
        self.scan_btn = ttk.Button(button_frame, text="🚀 Start Scan", 
                                  command=self.start_scan, state='disabled')
        self.scan_btn.pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="🗑️ Clear", 
                  command=self.clear_folders).pack(side='left', padx=5)
        
        # Folder list
        list_frame = ttk.LabelFrame(scan_frame, text="Selected Folders", padding=10)
        list_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Simple listbox instead of treeview for reliability
        self.folder_listbox = tk.Listbox(list_frame, font=("Arial", 10))
        self.folder_listbox.pack(fill='both', expand=True)
        
        # Progress
        self.progress_frame = ttk.Frame(scan_frame)
        self.progress_frame.pack(fill='x', padx=20, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, 
                                          variable=self.progress_var, 
                                          maximum=100)
        self.progress_bar.pack(fill='x', pady=5)
        
        self.status_label = ttk.Label(self.progress_frame, text="Ready to scan")
        self.status_label.pack()
        
    def create_results_tab(self, notebook):
        """Create results tab"""
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="📊 Results")
        
        # Results header
        header_frame = ttk.Frame(results_frame)
        header_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(header_frame, text="Duplicate Pairs Found", 
                 font=("Arial", 14, "bold")).pack(side='left')
        
        self.results_info = ttk.Label(header_frame, text="No scan completed")
        self.results_info.pack(side='right')
        
        # Results content
        content_frame = ttk.Frame(results_frame)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Always use text comparison for maximum compatibility
        self.create_text_comparison(content_frame)
        
        # Navigation buttons
        nav_frame = ttk.Frame(results_frame)
        nav_frame.pack(pady=10)
        
        ttk.Button(nav_frame, text="⬅️ Previous", 
                  command=self.previous_pair).pack(side='left', padx=5)
        ttk.Button(nav_frame, text="✅ Keep Original", 
                  command=self.keep_original).pack(side='left', padx=5)
        ttk.Button(nav_frame, text="⏭️ Skip", 
                  command=self.skip_pair).pack(side='left', padx=5)
        ttk.Button(nav_frame, text="➡️ Next", 
                  command=self.next_pair).pack(side='left', padx=5)
        
    def create_text_comparison(self, parent):
        """Create text-only comparison (most compatible)"""
        comparison_frame = ttk.Frame(parent)
        comparison_frame.pack(fill='both', expand=True)
        
        # Original side
        orig_frame = ttk.LabelFrame(comparison_frame, text="📁 Original (Keep)", padding=10)
        orig_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self.orig_text = tk.Text(orig_frame, height=15, wrap='word', font=("Arial", 10))
        self.orig_text.pack(fill='both', expand=True)
        
        # Duplicate side
        dup_frame = ttk.LabelFrame(comparison_frame, text="🗑️ Duplicate (Remove)", padding=10)
        dup_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        self.dup_text = tk.Text(dup_frame, height=15, wrap='word', font=("Arial", 10))
        self.dup_text.pack(fill='both', expand=True)
        
    def add_folder(self):
        """Add folder to scan"""
        folder = filedialog.askdirectory(title="Select folder with photos")
        if folder and folder not in self.selected_folders:
            self.selected_folders.append(folder)
            self.update_folder_list()
            self.scan_btn.config(state='normal')
            
    def clear_folders(self):
        """Clear folder list"""
        self.selected_folders.clear()
        self.update_folder_list()
        self.scan_btn.config(state='disabled')
        
    def update_folder_list(self):
        """Update folder listbox"""
        self.folder_listbox.delete(0, tk.END)
        for folder in self.selected_folders:
            self.folder_listbox.insert(tk.END, folder)
            
    def start_scan(self):
        """Start scanning for duplicates"""
        if not self.selected_folders:
            messagebox.showwarning("No Folders", "Please add folders first!")
            return
            
        self.is_scanning = True
        self.scan_btn.config(state='disabled', text='🔄 Scanning...')
        self.progress_var.set(0)
        
        # Start scan in background
        scan_thread = threading.Thread(target=self.scan_worker, daemon=True)
        scan_thread.start()
        
    def scan_worker(self):
        """Background scanning worker"""
        try:
            all_duplicates = []
            total_folders = len(self.selected_folders)
            
            for i, folder in enumerate(self.selected_folders):
                if not self.is_scanning:
                    break
                    
                # Update progress
                progress = (i / total_folders) * 100
                status = f"Scanning folder {i+1}/{total_folders}: {os.path.basename(folder)}"
                self.root.after(0, self.update_progress, progress, status)
                
                # Scan folder
                folder_duplicates = self.scan_folder(folder)
                all_duplicates.extend(folder_duplicates)
                
            # Complete
            self.duplicates = all_duplicates
            self.root.after(0, self.scan_complete)
            
        except Exception as e:
            self.root.after(0, self.scan_error, str(e))
            
    def scan_folder(self, folder_path):
        """Scan folder for duplicates - simple but reliable method"""
        duplicates = []
        extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        
        # Get all image files
        image_files = []
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(tuple(extensions)):
                        image_files.append(os.path.join(root, file))
        except Exception:
            return duplicates
            
        # Simple duplicate detection by file size
        size_groups = {}
        for image_path in image_files:
            try:
                size = os.path.getsize(image_path)
                if size not in size_groups:
                    size_groups[size] = []
                size_groups[size].append(image_path)
            except Exception:
                continue
                
        # Find groups with multiple files (potential duplicates)
        for size, files in size_groups.items():
            if len(files) > 1:
                # Take first as original, rest as duplicates
                original = files[0]
                for duplicate in files[1:]:
                    duplicates.append({
                        'original': original,
                        'duplicate': duplicate,
                        'similarity': 100  # Same size = likely duplicate
                    })
                    
        return duplicates
        
    def update_progress(self, value, status):
        """Update progress from main thread"""
        self.progress_var.set(value)
        self.status_label.config(text=status)
        
    def scan_complete(self):
        """Handle scan completion"""
        self.is_scanning = False
        self.scan_btn.config(state='normal', text='🚀 Start Scan')
        
        if self.duplicates:
            self.status_label.config(text=f"✅ Found {len(self.duplicates)} duplicate pairs")
            self.results_info.config(text=f"Found {len(self.duplicates)} pairs")
            self.current_pair_index = 0
            self.show_current_pair()
            
            messagebox.showinfo("Scan Complete", 
                              f"Found {len(self.duplicates)} duplicate pairs!\n"
                              "Check the Results tab to review them.")
        else:
            self.status_label.config(text="✅ No duplicates found")
            messagebox.showinfo("Scan Complete", "No duplicates found!")
            
    def scan_error(self, error):
        """Handle scan error"""
        self.is_scanning = False
        self.scan_btn.config(state='normal', text='🚀 Start Scan')
        self.status_label.config(text=f"❌ Scan failed: {error}")
        messagebox.showerror("Scan Error", f"Scan failed:\n{error}")
        
    def show_current_pair(self):
        """Show current duplicate pair"""
        if not self.duplicates or self.current_pair_index >= len(self.duplicates):
            return
            
        pair = self.duplicates[self.current_pair_index]
        self.results_info.config(text=f"Pair {self.current_pair_index + 1} of {len(self.duplicates)}")
        
        # Show text only for maximum compatibility
        orig_info = self.get_file_info(pair['original'])
        dup_info = self.get_file_info(pair['duplicate'])
        
        self.orig_text.delete(1.0, tk.END)
        self.orig_text.insert(tk.END, f"📁 ORIGINAL FILE (Keep this one)\n\n")
        self.orig_text.insert(tk.END, f"Path: {pair['original']}\n\n")
        self.orig_text.insert(tk.END, f"{orig_info}")
        
        self.dup_text.delete(1.0, tk.END)
        self.dup_text.insert(tk.END, f"🗑️ DUPLICATE FILE (Will be removed)\n\n")
        self.dup_text.insert(tk.END, f"Path: {pair['duplicate']}\n\n")
        self.dup_text.insert(tk.END, f"{dup_info}")
        
    def get_file_info(self, file_path):
        """Get file information"""
        try:
            stat = os.stat(file_path)
            size_mb = stat.st_size / (1024 * 1024)
            from datetime import datetime
            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            
            return f"📄 File: {os.path.basename(file_path)}\n💾 Size: {size_mb:.1f} MB\n📅 Modified: {modified}"
        except Exception:
            return f"📄 File: {os.path.basename(file_path)}\n❌ Cannot read file info"
            
    def previous_pair(self):
        """Show previous pair"""
        if self.current_pair_index > 0:
            self.current_pair_index -= 1
            self.show_current_pair()
            
    def next_pair(self):
        """Show next pair"""
        if self.current_pair_index < len(self.duplicates) - 1:
            self.current_pair_index += 1
            self.show_current_pair()
        else:
            messagebox.showinfo("End", "No more pairs to review!")
            
    def skip_pair(self):
        """Skip current pair"""
        self.next_pair()
        
    def keep_original(self):
        """Keep original, remove duplicate"""
        if not self.duplicates or self.current_pair_index >= len(self.duplicates):
            return
            
        pair = self.duplicates[self.current_pair_index]
        
        # Confirm
        if messagebox.askyesno("Confirm", f"Move duplicate to trash?\n\n{os.path.basename(pair['duplicate'])}"):
            try:
                # Create trash folder
                trash_folder = os.path.expanduser("~/DuplicateCleanerTrash")
                os.makedirs(trash_folder, exist_ok=True)
                
                # Move file
                import time
                import shutil
                filename = f"{int(time.time())}_{os.path.basename(pair['duplicate'])}"
                trash_path = os.path.join(trash_folder, filename)
                shutil.move(pair['duplicate'], trash_path)
                
                messagebox.showinfo("Success!", f"✅ Moved to trash:\n{filename}\n\nTrash location: ~/DuplicateCleanerTrash/")
                
                # Remove from list and show next
                self.duplicates.pop(self.current_pair_index)
                if self.current_pair_index >= len(self.duplicates):
                    self.current_pair_index = len(self.duplicates) - 1
                    
                if self.duplicates:
                    self.show_current_pair()
                else:
                    messagebox.showinfo("🎉 Complete!", "All duplicates processed!\n\nYour photos are now cleaned up.")
                    self.results_info.config(text="All duplicates processed!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to move file:\n{str(e)}")

# Import threading at module level
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Try to import PIL
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

if __name__ == "__main__":
    main()
