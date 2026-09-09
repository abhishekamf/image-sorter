"""
Main GUI window for the Duplicate Photo Cleaner
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path

from database.manager import DatabaseManager
from core.duplicate_detector import DuplicateDetector
from gui.login_window import LoginWindow
from gui.comparison_frame import ComparisonFrame
from gui.holding_frame import HoldingFrame

class DuplicatePhotoCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate Photo Cleaner v1.0")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Initialize components
        self.db = DatabaseManager()
        self.current_user = None
        self.detector = None
        
        # Show login window
        self.show_login()

    def show_login(self):
        """Show login/registration window"""
        self.clear_window()
        login_window = LoginWindow(self.root, self.on_login_success)

    def on_login_success(self, user_data):
        """Handle successful login"""
        self.current_user = user_data
        self.detector = DuplicateDetector(self.db, user_data['id'])
        self.show_main_window()

    def show_main_window(self):
        """Show the main application window"""
        self.clear_window()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Comparison tab
        self.comparison_frame = ComparisonFrame(notebook, self.detector, self.db, self.current_user)
        notebook.add(self.comparison_frame, text="Find Duplicates")
        
        # Holding folder tab
        self.holding_frame = HoldingFrame(notebook, self.detector, self.db, self.current_user)
        notebook.add(self.holding_frame, text="Holding Folder")
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text=f"Logged in as: {self.current_user['username']}")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Select Folder & Scan", command=self.select_folder_and_scan)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # History menu
        history_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="History", menu=history_menu)
        history_menu.add_command(label="View History", command=self.show_history)
        history_menu.add_command(label="Clean Old History", command=self.clean_history)

    def select_folder_and_scan(self):
        """Open folder selection dialog and start scan"""
        folder_path = filedialog.askdirectory(title="Select folder containing photos")
        if folder_path:
            self.comparison_frame.start_scan(folder_path)

    def show_settings(self):
        """Show settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x400")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Get current settings
        settings = self.db.get_settings(self.current_user['id'])
        current_retention = settings[0] if settings else 6
        current_holding = settings[1] if settings else ""
        
        # Create settings form
        ttk.Label(settings_window, text="History Retention (months):").pack(pady=10)
        
        retention_var = tk.StringVar(value=str(current_retention))
        retention_frame = ttk.Frame(settings_window)
        retention_frame.pack(pady=5)
        
        for months in [1, 3, 6, 12]:
            ttk.Radiobutton(retention_frame, text=f"{months} month{'s' if months > 1 else ''}", 
                           variable=retention_var, value=str(months)).pack(anchor='w')
        
        ttk.Label(settings_window, text="Holding Folder:").pack(pady=(20, 5))
        
        holding_frame = ttk.Frame(settings_window)
        holding_frame.pack(pady=5, padx=20, fill='x')
        
        holding_var = tk.StringVar(value=current_holding)
        holding_entry = ttk.Entry(holding_frame, textvariable=holding_var, width=50)
        holding_entry.pack(side='left', expand=True, fill='x')
        
        def browse_folder():
            folder = filedialog.askdirectory()
            if folder:
                holding_var.set(folder)
        
        ttk.Button(holding_frame, text="Browse", command=browse_folder).pack(side='right', padx=(5, 0))
        
        def save_settings():
            try:
                retention = int(retention_var.get())
                holding = holding_var.get() or str(Path.home() / ".duplicate_photo_cleaner" / "holding")
                self.db.update_settings(self.current_user['id'], retention, holding)
                messagebox.showinfo("Settings", "Settings saved successfully!")
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid retention period")
        
        ttk.Button(settings_window, text="Save", command=save_settings).pack(pady=20)

    def show_history(self):
        """Show action history window"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Action History")
        history_window.geometry("800x600")
        history_window.transient(self.root)
        
        # Create treeview for history
        tree = ttk.Treeview(history_window, columns=('Action', 'File', 'Time'), show='headings')
        tree.heading('Action', text='Action')
        tree.heading('File', text='File Path')
        tree.heading('Time', text='Timestamp')
        
        tree.column('Action', width=150)
        tree.column('File', width=400)
        tree.column('Time', width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(history_window, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side='right', fill='y', padx=(0, 10), pady=10)
        
        # Load history data
        history = self.db.get_history(self.current_user['id'])
        for action, file_path, timestamp in history:
            tree.insert('', 'end', values=(action, file_path, timestamp))

    def clean_history(self):
        """Clean old history entries"""
        settings = self.db.get_settings(self.current_user['id'])
        retention_months = settings[0] if settings else 6
        
        self.db.clean_old_history(self.current_user['id'], retention_months)
        messagebox.showinfo("History", "Old history entries have been cleaned!")

    def logout(self):
        """Logout current user"""
        self.current_user = None
        self.detector = None
        self.show_login()

    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Clear menu
        self.root.config(menu=tk.Menu())
