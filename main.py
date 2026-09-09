#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path

class DuplicatePhotoCleaner:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate Photo Cleaner v1.0")
        self.root.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="Duplicate Photo Cleaner", 
                         font=("Arial", 20, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                                text="Select a folder to scan for duplicate photos:")
        instructions.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Buttons
        self.select_btn = ttk.Button(main_frame, text="Select Folder", 
                                    command=self.select_folder)
        self.select_btn.grid(row=2, column=0, pady=10, padx=5)
        
        self.scan_btn = ttk.Button(main_frame, text="Start Scan", 
                                  command=self.start_scan, state="disabled")
        self.scan_btn.grid(row=2, column=1, pady=10, padx=5)
        
        # Results area
        self.results_text = tk.Text(main_frame, height=20, width=80)
        self.results_text.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", 
                                 command=self.results_text.yview)
        scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.selected_folder = None
        
    def select_folder(self):
        folder = filedialog.askdirectory(title="Select folder with photos")
        if folder:
            self.selected_folder = folder
            self.scan_btn.config(state="normal")
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Selected folder: {folder}\n\n")
            
    def start_scan(self):
        if not self.selected_folder:
            return
            
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Scanning for duplicate photos...\n\n")
        self.root.update()
        
        # Simple scan simulation
        photo_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        files_found = []
        
        try:
            for root, dirs, files in os.walk(self.selected_folder):
                for file in files:
                    if Path(file).suffix.lower() in photo_extensions:
                        files_found.append(os.path.join(root, file))
                        
            self.results_text.insert(tk.END, f"Found {len(files_found)} image files\n")
            
            if files_found:
                self.results_text.insert(tk.END, "\nImage files found:\n")
                for i, file_path in enumerate(files_found[:20]):  # Show first 20
                    self.results_text.insert(tk.END, f"{i+1}. {os.path.basename(file_path)}\n")
                if len(files_found) > 20:
                    self.results_text.insert(tk.END, f"... and {len(files_found) - 20} more files\n")
            else:
                self.results_text.insert(tk.END, "No image files found in the selected folder.\n")
                
        except Exception as e:
            self.results_text.insert(tk.END, f"Error scanning folder: {str(e)}\n")

def main():
    root = tk.Tk()
    app = DuplicatePhotoCleaner(root)
    
    # Configure grid weights for resizing
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    root.mainloop()

if __name__ == "__main__":
    main()
