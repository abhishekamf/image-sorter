"""
Frame for managing files in the holding folder
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
from pathlib import Path

class HoldingFrame(ttk.Frame):
    def __init__(self, parent, detector, db, user):
        super().__init__(parent)
        self.detector = detector
        self.db = db
        self.user = user
        
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        """Setup the holding folder UI"""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        ttk.Label(header_frame, text="Holding Folder", 
                 font=('Arial', 16, 'bold')).pack(anchor='w')
        ttk.Label(header_frame, text="Files here are NOT permanently deleted. Review and delete when ready.", 
                 font=('Arial', 10)).pack(anchor='w', pady=(5, 0))
        
        # File list
        list_frame = ttk.Frame(self)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create treeview
        columns = ('Filename', 'Size', 'Date Moved')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.tree.heading('Filename', text='Filename')
        self.tree.heading('Size', text='Size')
        self.tree.heading('Date Moved', text='Date Moved')
        
        self.tree.column('Filename', width=400)
        self.tree.column('Size', width=100)
        self.tree.column('Date Moved', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Refresh List", 
                  command=self.refresh_list).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Selected", 
                  command=self.delete_selected).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete All", 
                  command=self.delete_all).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Open Holding Folder", 
                  command=self.open_folder).pack(side='left', padx=5)

    def get_holding_folder(self):
        """Get the holding folder path"""
        settings = self.db.get_settings(self.user['id'])
        if settings and settings[1]:
            return settings[1]
        else:
            return str(Path.home() / ".duplicate_photo_cleaner" / "holding")

    def refresh_list(self):
        """Refresh the file list"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        holding_folder = self.get_holding_folder()
        
        if not os.path.exists(holding_folder):
            self.tree.insert('', 'end', values=('Holding folder is empty', '', ''))
            return
        
        files = os.listdir(holding_folder)
        
        if not files:
            self.tree.insert('', 'end', values=('No files in holding folder', '', ''))
            return
        
        for filename in sorted(files):
            file_path = os.path.join(holding_folder, filename)
            
            try:
                # Get file size
                size = os.path.getsize(file_path)
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size / (1024 * 1024):.1f} MB"
                
                # Get modification time
                import datetime
                mtime = os.path.getmtime(file_path)
                date_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
                
                self.tree.insert('', 'end', values=(filename, size_str, date_str))
            except:
                self.tree.insert('', 'end', values=(filename, 'Error', 'Error'))

    def delete_selected(self):
        """Delete selected files"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select files to delete")
            return
        
        # Get selected filenames
        filenames = []
        for item in selection:
            values = self.tree.item(item)['values']
            if values and values[0] not in ['Holding folder is empty', 'No files in holding folder']:
                filenames.append(values[0])
        
        if not filenames:
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Deletion", 
                                  f"Are you sure you want to permanently delete {len(filenames)} file(s)?"):
            return
        
        # Delete files
        holding_folder = self.get_holding_folder()
        deleted_count = 0
        
        for filename in filenames:
            file_path = os.path.join(holding_folder, filename)
            try:
                os.remove(file_path)
                self.db.log_action(self.user['id'], "permanently_deleted", file_path)
                deleted_count += 1
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete {filename}:\n{str(e)}")
        
        messagebox.showinfo("Success", f"Permanently deleted {deleted_count} file(s)")
        self.refresh_list()

    def delete_all(self):
        """Delete all files in holding folder"""
        holding_folder = self.get_holding_folder()
        
        if not os.path.exists(holding_folder):
            messagebox.showinfo("Info", "Holding folder is empty")
            return
        
        files = os.listdir(holding_folder)
        if not files:
            messagebox.showinfo("Info", "Holding folder is empty")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Deletion", 
                                  f"Are you sure you want to permanently delete ALL {len(files)} file(s) in the holding folder?"):
            return
        
        # Delete all files
        deleted_files = self.detector.permanently_delete(holding_folder)
        
        messagebox.showinfo("Success", f"Permanently deleted {len(deleted_files)} file(s)")
        self.refresh_list()

    def open_folder(self):
        """Open the holding folder in file explorer"""
        holding_folder = self.get_holding_folder()
        
        # Create folder if it doesn't exist
        Path(holding_folder).mkdir(parents=True, exist_ok=True)
        
        import subprocess
        import sys
        
        try:
            if sys.platform == "win32":
                subprocess.Popen(['explorer', holding_folder])
            elif sys.platform == "darwin":
                subprocess.Popen(['open', holding_folder])
            else:  # Linux
                subprocess.Popen(['xdg-open', holding_folder])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{str(e)}")
