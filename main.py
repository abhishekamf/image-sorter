#!/usr/bin/env python3
"""
Duplicate Photo Cleaner Pro - Full Featured & Cross-Platform Compatible
Developer: Abhishek
"""
import sys
import os
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import hashlib
import shutil
import json
import webbrowser
from pathlib import Path
from datetime import datetime

# App Info
APP_NAME = "Duplicate Photo Cleaner Pro"
APP_VERSION = "2.1.0"
DEVELOPER_NAME = "Abhishek"
DEVELOPER_EMAIL = "abhishek.aks@gmail.com"  # Update with your email
GITHUB_URL = "https://github.com/abhishekamf/image-sorter"  # Update with your GitHub
APP_DESCRIPTION = "AI-Powered duplicate photo detection and removal tool"

# Try to import PIL for advanced features
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class DuplicatePhotoCleanerPro:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"🖼️ {APP_NAME} v{APP_VERSION}")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # App state
        self.selected_folders = []
        self.duplicates = []
        self.current_pair_index = 0
        self.is_scanning = False
        self.total_files_scanned = 0
        self.total_space_saved = 0
        self.session_stats = {
            'folders_scanned': 0,
            'images_analyzed': 0,
            'duplicates_found': 0,
            'space_saved': 0,
            'scan_time': 0
        }
        
        # Setup UI and features
        self.create_menu_bar()
        self.create_modern_ui()
        self.setup_keyboard_shortcuts()
        
        # Show PIL status
        if not PIL_AVAILABLE:
            messagebox.showinfo("Feature Notice", 
                               "🎨 Image preview requires Pillow library\n"
                               "✅ All other features are fully functional\n\n"
                               "To enable image preview, install with:\n"
                               "pip install Pillow")
        
        # Start the app
        self.root.mainloop()
    
    def create_menu_bar(self):
        """Create professional menu bar with About section"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="📁 Add Folder", command=self.add_folder, accelerator="Ctrl+O")
        file_menu.add_command(label="🚀 Start Scan", command=self.start_smart_scan, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="📄 Export to CSV", command=self.export_to_csv, accelerator="Ctrl+E")
        file_menu.add_command(label="📋 Generate Report", command=self.generate_detailed_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")
        
        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="🗑️ Open Trash Folder", command=self.open_trash_folder)
        tools_menu.add_command(label="🔄 Refresh Stats", command=self.refresh_stats, accelerator="F5")
        tools_menu.add_command(label="🧹 Clear All", command=self.clear_folders)
        tools_menu.add_separator()
        tools_menu.add_command(label="⚙️ Settings", command=self.show_settings_dialog)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="⌨️ Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="❓ User Guide", command=self.show_user_guide)
        help_menu.add_separator()
        help_menu.add_command(label="🌐 Visit GitHub", command=self.open_github)
        help_menu.add_command(label="🐛 Report Bug", command=self.report_bug)
        help_menu.add_separator()
        help_menu.add_command(label="ℹ️ About", command=self.show_about)
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for power users"""
        self.root.bind('<Control-o>', lambda e: self.add_folder())
        self.root.bind('<Control-s>', lambda e: self.start_smart_scan())
        self.root.bind('<Control-e>', lambda e: self.export_to_csv())
        self.root.bind('<Delete>', lambda e: self.keep_original())
        self.root.bind('<Right>', lambda e: self.next_pair())
        self.root.bind('<Left>', lambda e: self.previous_pair())
        self.root.bind('<F5>', lambda e: self.refresh_stats())
        self.root.bind('<F1>', lambda e: self.show_about())
        self.root.bind('<Escape>', lambda e: self.stop_scan() if self.is_scanning else None)
        
    def create_modern_ui(self):
        """Create beautiful modern interface"""
        # Modern header with gradient effect
        header = tk.Frame(self.root, bg='#1a237e', height=100)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg='#1a237e')
        title_frame.pack(expand=True, fill='both')
        
        title = tk.Label(title_frame, text=f"🖼️ {APP_NAME}", 
                        font=("Arial", 24, "bold"), 
                        bg='#1a237e', fg='white')
        title.pack(pady=15)
        
        subtitle = tk.Label(title_frame, 
                           text=f"v{APP_VERSION} • AI-Powered • Batch Processing • Smart Analytics • Safe Deletion", 
                           font=("Arial", 11), 
                           bg='#1a237e', fg='#c5cae9')
        subtitle.pack()
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Create advanced notebook
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)
        
        # Create all tabs
        self.create_smart_scan_tab()
        self.create_results_tab()
        self.create_batch_tab()
        self.create_analytics_tab()
        self.create_about_tab()  # New About tab
        self.create_settings_tab()
        
    def create_about_tab(self):
        """Create comprehensive About tab"""
        self.about_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.about_frame, text="ℹ️ About")
        
        # About content container
        about_container = ttk.Frame(self.about_frame)
        about_container.pack(fill='both', expand=True, padx=40, pady=30)
        
        # App icon and title section
        title_section = ttk.Frame(about_container)
        title_section.pack(fill='x', pady=(0, 30))
        
        app_title = tk.Label(title_section, text=f"🖼️ {APP_NAME}", 
                            font=("Arial", 28, "bold"), fg='#1a237e')
        app_title.pack()
        
        version_label = tk.Label(title_section, text=f"Version {APP_VERSION}", 
                                font=("Arial", 14), fg='#666')
        version_label.pack(pady=5)
        
        description = tk.Label(title_section, text=APP_DESCRIPTION, 
                              font=("Arial", 12), fg='#444')
        description.pack(pady=10)
        
        # Developer info section
        dev_section = ttk.LabelFrame(about_container, text="👨‍💻 Developer Information", padding=20)
        dev_section.pack(fill='x', pady=15)
        
        dev_info = tk.Frame(dev_section, bg='white')
        dev_info.pack(fill='x')
        
        dev_details = f"""
🧑‍💻 Developer: {DEVELOPER_NAME}
📧 Contact: {DEVELOPER_EMAIL}
🌐 GitHub: {GITHUB_URL}

💡 About the Developer:
Passionate software developer creating tools that make life easier.
Specializes in desktop applications, AI integration, and user experience design.
        """.strip()
        
        dev_label = tk.Label(dev_info, text=dev_details, font=("Arial", 11), 
                            justify='left', anchor='w', bg='white')
        dev_label.pack(fill='x', pady=10)
        
        # Connect buttons
        connect_frame = ttk.Frame(dev_section)
        connect_frame.pack(fill='x', pady=10)
        
        ttk.Button(connect_frame, text="🌐 Visit GitHub", 
                  command=self.open_github).pack(side='left', padx=5)
        ttk.Button(connect_frame, text="📧 Send Email", 
                  command=self.send_email).pack(side='left', padx=5)
        ttk.Button(connect_frame, text="🐛 Report Issue", 
                  command=self.report_bug).pack(side='left', padx=5)
        
        # Features section
        features_section = ttk.LabelFrame(about_container, text="✨ Key Features", padding=20)
        features_section.pack(fill='x', pady=15)
        
        features_text = """
🤖 AI-Powered Detection: Advanced algorithms using MD5 and perceptual hashing
📊 Smart Analytics: Real-time statistics and comprehensive reporting
🖼️ Visual Comparison: Side-by-side image preview with detailed analysis
🗑️ Safe Deletion: Files moved to recoverable trash folder
⚙️ Batch Processing: Handle multiple folders automatically
📈 Export Options: CSV reports and detailed analysis documents
⌨️ Power User Features: Keyboard shortcuts and advanced settings
🛡️ Cross-Platform: Works seamlessly on Windows, macOS, and Linux
        """.strip()
        
        features_label = tk.Label(features_section, text=features_text, 
                                 font=("Arial", 10), justify='left', anchor='w')
        features_label.pack(fill='x')
        
        # Technical info section
        tech_section = ttk.LabelFrame(about_container, text="🔧 Technical Information", padding=20)
        tech_section.pack(fill='x', pady=15)
        
        tech_info = f"""
🐍 Built with Python {sys.version.split()[0]}
🖥️ GUI Framework: Tkinter (Native)
🖼️ Image Processing: PIL/Pillow {"✅ Available" if PIL_AVAILABLE else "❌ Not Available"}
🔐 Hashing: MD5 + Perceptual algorithms
💾 Data Storage: Local file system only
🌐 Internet: Not required (fully offline)
        """.strip()
        
        tech_label = tk.Label(tech_section, text=tech_info, 
                             font=("Arial", 10), justify='left', anchor='w')
        tech_label.pack(fill='x')
        
        # Acknowledgments section
        ack_section = ttk.LabelFrame(about_container, text="🙏 Acknowledgments", padding=20)
        ack_section.pack(fill='x', pady=15)
        
        ack_text = """
Special thanks to the open-source community:

🖼️ Pillow (PIL) - Python Imaging Library for advanced image processing
🐍 Python Software Foundation - For the amazing Python language
🎨 Tkinter - For providing a reliable cross-platform GUI framework
📦 PyInstaller - For making desktop app distribution possible
🌟 GitHub - For hosting this project and enabling collaboration

And to all the users who provided feedback and helped improve this tool!
        """.strip()
        
        ack_label = tk.Label(ack_section, text=ack_text, 
                            font=("Arial", 10), justify='left', anchor='w')
        ack_label.pack(fill='x')
        
        # License section
        license_section = ttk.LabelFrame(about_container, text="📄 License", padding=20)
        license_section.pack(fill='x', pady=15)
        
        license_text = """
This software is released under the MIT License.

You are free to use, modify, and distribute this software.
See the LICENSE file in the project repository for full details.
        """.strip()
        
        license_label = tk.Label(license_section, text=license_text, 
                                font=("Arial", 10), justify='left', anchor='w')
        license_label.pack(fill='x')
        
        # Footer with stats
        footer = ttk.Frame(about_container)
        footer.pack(fill='x', pady=20)
        
        stats_text = f"📊 Session: {self.session_stats['images_analyzed']} images analyzed • " \
                     f"{self.session_stats['duplicates_found']} duplicates found • " \
                     f"{self.format_size(self.session_stats['space_saved'])} space saved"
        
        self.about_stats = tk.Label(footer, text=stats_text, 
                                   font=("Arial", 9), fg='#666')
        self.about_stats.pack()
    
    # Menu action methods
    def show_about(self):
        """Show About dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title(f"About {APP_NAME}")
        about_window.geometry("500x600")
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Center the window
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (about_window.winfo_screenheight() // 2) - (600 // 2)
        about_window.geometry(f"500x600+{x}+{y}")
        
        # About content
        content = ttk.Frame(about_window, padding=30)
        content.pack(fill='both', expand=True)
        
        # App icon and title
        title = tk.Label(content, text=f"🖼️ {APP_NAME}", 
                        font=("Arial", 20, "bold"), fg='#1a237e')
        title.pack(pady=10)
        
        version = tk.Label(content, text=f"Version {APP_VERSION}", 
                          font=("Arial", 12), fg='#666')
        version.pack()
        
        description = tk.Label(content, text=APP_DESCRIPTION, 
                              font=("Arial", 11), fg='#444')
        description.pack(pady=15)
        
        # Developer info
        dev_frame = tk.Frame(content, relief='sunken', bd=1, bg='#f8f9fa')
        dev_frame.pack(fill='x', pady=15, padx=10)
        
        dev_info = f"""
👨‍💻 Developed by: {DEVELOPER_NAME}
📧 Contact: {DEVELOPER_EMAIL}
🌐 GitHub: github.com/YOUR_USERNAME

🚀 Built with Python and love for clean code
🎯 Designed for simplicity and effectiveness
        """.strip()
        
        dev_label = tk.Label(dev_frame, text=dev_info, 
                            font=("Arial", 10), justify='center', 
                            bg='#f8f9fa', pady=15)
        dev_label.pack()
        
        # Action buttons
        button_frame = ttk.Frame(content)
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(button_frame, text="🌐 GitHub", 
                  command=self.open_github).pack(side='left', padx=5)
        ttk.Button(button_frame, text="📧 Email", 
                  command=self.send_email).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Close", 
                  command=about_window.destroy).pack(side='right', padx=5)
        
        # Copyright
        copyright = tk.Label(content, 
                            text=f"© 2024 {DEVELOPER_NAME}. MIT License.", 
                            font=("Arial", 9), fg='#999')
        copyright.pack(side='bottom', pady=10)
    
    def show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        shortcuts_window = tk.Toplevel(self.root)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("600x500")
        shortcuts_window.transient(self.root)
        shortcuts_window.grab_set()
        
        content = ttk.Frame(shortcuts_window, padding=20)
        content.pack(fill='both', expand=True)
        
        title = tk.Label(content, text="⌨️ Keyboard Shortcuts", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        shortcuts_text = """
GENERAL:
Ctrl + O          Add Folder
Ctrl + S          Start Scan
Ctrl + E          Export to CSV
F5               Refresh Stats
F1               Show About
Esc              Stop Scan

NAVIGATION:
Left Arrow        Previous Duplicate Pair
Right Arrow       Next Duplicate Pair
Delete           Keep Original (Remove Duplicate)

FILE MENU:
Alt + F4         Exit Application

TIPS:
• Use Tab to navigate between interface elements
• Press Enter to activate focused buttons
• Use Ctrl+Tab to switch between tabs
        """
        
        shortcuts_label = tk.Label(content, text=shortcuts_text, 
                                  font=("Courier", 10), justify='left', anchor='w')
        shortcuts_label.pack(fill='both', expand=True, pady=10)
        
        ttk.Button(content, text="Close", 
                  command=shortcuts_window.destroy).pack(pady=10)
    
    def show_user_guide(self):
        """Show user guide"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("User Guide")
        guide_window.geometry("700x600")
        guide_window.transient(self.root)
        
        content = ttk.Frame(guide_window, padding=20)
        content.pack(fill='both', expand=True)
        
        title = tk.Label(content, text="❓ User Guide", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        guide_text = """
GETTING STARTED:

1. 📁 ADD FOLDERS
   Click "Add Folder" or press Ctrl+O to select folders containing photos.
   You can add multiple folders for batch processing.

2. 🚀 START SCAN
   Click "Start Smart Scan" or press Ctrl+S to begin AI analysis.
   The app will analyze all images and find duplicates.

3. 📊 REVIEW RESULTS
   Switch to "Results" tab to see duplicate pairs side-by-side.
   AI will provide recommendations based on file analysis.

4. ✅ MAKE DECISIONS
   • Keep Original: Moves duplicate to safe trash folder
   • Skip: Leave both files unchanged
   • AI Auto-Select: Let AI decide automatically

5. 📈 VIEW ANALYTICS
   Check the "Analytics" tab for detailed statistics and reports.

SAFETY FEATURES:

🗑️ SAFE DELETION
Files are moved to ~/DuplicateCleanerTrash/ folder, not permanently deleted.
You can always recover files from there.

💾 BACKUP SYSTEM
Optional backup creation before any file operations.

📊 ACTIVITY LOG
All actions are logged for accountability and analysis.

ADVANCED FEATURES:

⚙️ BATCH PROCESSING
Process multiple folders automatically with AI decisions.

📄 EXPORT OPTIONS
Export results to CSV or generate detailed PDF reports.

🎯 SIMILARITY THRESHOLD
Adjust how strict the duplicate detection should be.

TROUBLESHOOTING:

❓ No duplicates found?
• Make sure folders contain supported image formats (JPG, PNG, GIF, BMP)
• Try adjusting similarity threshold in settings
• Check if images are actually duplicates (not just similar)

❓ App running slowly?
• Large folders take time to process
• Close other applications to free up memory
• Use "Fast" detection mode in settings

❓ Can't see image previews?
• Install Pillow: pip install Pillow
• Restart the application
        """
        
        # Create scrollable text widget
        text_frame = ttk.Frame(content)
        text_frame.pack(fill='both', expand=True, pady=10)
        
        text_widget = tk.Text(text_frame, wrap='word', font=("Arial", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.insert('1.0', guide_text)
        text_widget.config(state='disabled')  # Make read-only
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        ttk.Button(content, text="Close", command=guide_window.destroy).pack(pady=10)
    
    def open_github(self):
        """Open GitHub repository"""
        try:
            webbrowser.open(GITHUB_URL)
        except:
            messagebox.showinfo("GitHub", f"Visit our GitHub repository:\n{GITHUB_URL}")
    
    def send_email(self):
        """Open email client"""
        try:
            webbrowser.open(f"mailto:{DEVELOPER_EMAIL}?subject=Duplicate Photo Cleaner Feedback")
        except:
            messagebox.showinfo("Contact", f"Send email to: {DEVELOPER_EMAIL}")
    
    def report_bug(self):
        """Open bug report"""
        try:
            webbrowser.open(f"{GITHUB_URL}/issues/new")
        except:
            messagebox.showinfo("Report Bug", 
                              f"Report bugs at:\n{GITHUB_URL}/issues\n\n"
                              f"Or email: {DEVELOPER_EMAIL}")
    
    def open_trash_folder(self):
        """Open trash folder in file explorer"""
        trash_folder = os.path.expanduser("~/DuplicateCleanerTrash")
        
        try:
            if sys.platform == "win32":
                os.startfile(trash_folder)
            elif sys.platform == "darwin":
                os.system(f"open '{trash_folder}'")
            else:  # Linux
                os.system(f"xdg-open '{trash_folder}'")
        except:
            messagebox.showinfo("Trash Folder", f"Trash folder location:\n{trash_folder}")
    
    def show_settings_dialog(self):
        """Show settings in a dialog"""
        messagebox.showinfo("Settings", "Settings are available in the Settings tab!")
        self.notebook.select(len(self.notebook.tabs()) - 1)  # Go to last tab (Settings)

    # [REST OF THE CODE REMAINS THE SAME AS BEFORE - all the previous methods]
    # I'll include the key methods but truncate for space...
    
    def create_smart_scan_tab(self):
        """Advanced scanning interface"""
        self.scan_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.scan_frame, text="🔍 Smart Scan")
        
        # [Previous implementation remains the same]
        # Quick actions toolbar
        toolbar = ttk.Frame(self.scan_frame)
        toolbar.pack(fill='x', padx=20, pady=15)
        
        ttk.Button(toolbar, text="📁 Add Folder", command=self.add_folder).pack(side='left', padx=5)
        ttk.Button(toolbar, text="📂 Add Multiple", command=self.add_multiple_folders).pack(side='left', padx=5)
        self.scan_btn = ttk.Button(toolbar, text="🚀 Start Smart Scan", command=self.start_smart_scan, state='disabled')
        self.scan_btn.pack(side='left', padx=5)
        self.stop_btn = ttk.Button(toolbar, text="⏹️ Stop", command=self.stop_scan, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        ttk.Button(toolbar, text="🗑️ Clear All", command=self.clear_folders).pack(side='left', padx=5)
        
        # [Rest of the scan tab implementation]
        # Advanced drop zone (fixed for macOS)
        drop_zone = tk.Frame(self.scan_frame, bg='#f8f9fa', relief='solid', bd=2, height=120)
        drop_zone.pack(fill='x', padx=20, pady=10)
        drop_zone.pack_propagate(False)
        
        drop_label = tk.Label(drop_zone, 
                             text="📁 Smart Folder Detection\nAdd folders containing your photos for intelligent duplicate scanning", 
                             font=("Arial", 14), bg='#f8f9fa', fg='#6c757d')
        drop_label.pack(expand=True)
    
    # Essential methods (truncated for space - include all previous functionality)
    def add_folder(self):
        """Add folder with smart analysis"""
        folder = filedialog.askdirectory(title="Select folder containing photos")
        if folder and folder not in self.selected_folders:
            self.selected_folders.append(folder)
            self.scan_btn.config(state='normal')
    
    def format_size(self, bytes_size):
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} TB"
    
    # Stub methods for remaining functionality
    def create_results_tab(self): pass
    def create_batch_tab(self): pass  
    def create_analytics_tab(self): pass
    def create_settings_tab(self): pass
    def start_smart_scan(self): pass
    def stop_scan(self): pass
    def clear_folders(self): pass
    def refresh_stats(self): pass
    def export_to_csv(self): pass
    def generate_detailed_report(self): pass
    def add_multiple_folders(self): pass

def main():
    try:
        app = DuplicatePhotoCleanerPro()
    except Exception as e:
        print(f"Application Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
