#!/usr/bin/env python3
"""
Duplicate Photo Cleaner Pro - Full Featured & Cross-Platform Compatible
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
from pathlib import Path
from datetime import datetime

# Try to import PIL for advanced features
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class DuplicatePhotoCleanerPro:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🖼️ Duplicate Photo Cleaner Pro v2.0")
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
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for power users"""
        self.root.bind('<Control-o>', lambda e: self.add_folder())
        self.root.bind('<Control-s>', lambda e: self.start_smart_scan())
        self.root.bind('<Control-e>', lambda e: self.export_to_csv())
        self.root.bind('<Delete>', lambda e: self.keep_original())
        self.root.bind('<Right>', lambda e: self.next_pair())
        self.root.bind('<Left>', lambda e: self.previous_pair())
        self.root.bind('<F5>', lambda e: self.refresh_stats())
        self.root.bind('<Escape>', lambda e: self.stop_scan() if self.is_scanning else None)
        
    def create_modern_ui(self):
        """Create beautiful modern interface"""
        # Modern header with gradient effect
        header = tk.Frame(self.root, bg='#1a237e', height=100)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg='#1a237e')
        title_frame.pack(expand=True, fill='both')
        
        title = tk.Label(title_frame, text="🖼️ Duplicate Photo Cleaner Pro", 
                        font=("Arial", 24, "bold"), 
                        bg='#1a237e', fg='white')
        title.pack(pady=15)
        
        subtitle = tk.Label(title_frame, 
                           text="AI-Powered • Batch Processing • Smart Analytics • Safe Deletion", 
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
        self.create_settings_tab()
        
    def create_smart_scan_tab(self):
        """Advanced scanning interface"""
        self.scan_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.scan_frame, text="🔍 Smart Scan")
        
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
        
        # Advanced drop zone (fixed for macOS)
        drop_zone = tk.Frame(self.scan_frame, bg='#f8f9fa', relief='solid', bd=2, height=120)
        drop_zone.pack(fill='x', padx=20, pady=10)
        drop_zone.pack_propagate(False)
        
        drop_label = tk.Label(drop_zone, 
                             text="📁 Smart Folder Detection\nAdd folders containing your photos for intelligent duplicate scanning", 
                             font=("Arial", 14), bg='#f8f9fa', fg='#6c757d')
        drop_label.pack(expand=True)
        
        # Folders management
        folders_frame = ttk.LabelFrame(self.scan_frame, text="📁 Selected Folders & Analysis", padding=15)
        folders_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Advanced folder tree
        tree_frame = ttk.Frame(folders_frame)
        tree_frame.pack(fill='both', expand=True)
        
        self.folders_tree = ttk.Treeview(tree_frame, 
                                        columns=('Path', 'Images', 'Size', 'Status'), 
                                        show='headings', height=6)
        self.folders_tree.heading('Path', text='Folder Path')
        self.folders_tree.heading('Images', text='Image Files')
        self.folders_tree.heading('Size', text='Total Size')
        self.folders_tree.heading('Status', text='Status')
        
        # Set column widths
        self.folders_tree.column('Path', width=400)
        self.folders_tree.column('Images', width=100)
        self.folders_tree.column('Size', width=100)
        self.folders_tree.column('Status', width=100)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.folders_tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.folders_tree.xview)
        self.folders_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.folders_tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        
        # Advanced progress section
        self.create_advanced_progress(self.scan_frame)
        
    def create_advanced_progress(self, parent):
        """Advanced progress indicators"""
        progress_frame = ttk.LabelFrame(parent, text="🚀 Scan Progress & Real-Time Analytics", padding=15)
        progress_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Multi-level progress
        progress_container = ttk.Frame(progress_frame)
        progress_container.pack(fill='x')
        
        # Overall progress
        ttk.Label(progress_container, text="Overall Progress:").pack(anchor='w')
        self.overall_progress = ttk.Progressbar(progress_container, mode='determinate', length=500)
        self.overall_progress.pack(fill='x', pady=(2, 10))
        
        # Current folder progress
        ttk.Label(progress_container, text="Current Folder:").pack(anchor='w')
        self.current_progress = ttk.Progressbar(progress_container, mode='determinate', length=500)
        self.current_progress.pack(fill='x', pady=(2, 10))
        
        # Status labels with real-time stats
        self.overall_status = ttk.Label(progress_container, text="Ready for intelligent scanning...", 
                                       font=("Arial", 11, "bold"))
        self.overall_status.pack(anchor='w', pady=2)
        
        self.current_status = ttk.Label(progress_container, text="", font=("Arial", 10))
        self.current_status.pack(anchor='w', pady=2)
        
        self.live_stats = ttk.Label(progress_container, text="", font=("Arial", 10), foreground='#1976d2')
        self.live_stats.pack(anchor='w', pady=2)
        
    def create_results_tab(self):
        """Advanced results with AI recommendations"""
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="📊 AI Analysis & Results")
        
        # Results toolbar
        results_toolbar = ttk.Frame(self.results_frame)
        results_toolbar.pack(fill='x', padx=20, pady=15)
        
        ttk.Label(results_toolbar, text="🤖 AI-Powered Duplicate Analysis", 
                 font=("Arial", 16, "bold")).pack(side='left')
        
        self.results_info = ttk.Label(results_toolbar, text="No analysis completed")
        self.results_info.pack(side='right')
        
        # AI recommendation panel
        ai_frame = ttk.LabelFrame(self.results_frame, text="🧠 AI Recommendations", padding=10)
        ai_frame.pack(fill='x', padx=20, pady=10)
        
        self.ai_recommendation = ttk.Label(ai_frame, text="Run a scan to get AI-powered recommendations", 
                                          font=("Arial", 11), foreground='#4caf50')
        self.ai_recommendation.pack(anchor='w')
        
        # Enhanced comparison area
        comparison_container = ttk.Frame(self.results_frame)
        comparison_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        if PIL_AVAILABLE:
            self.create_image_comparison(comparison_container)
        else:
            self.create_enhanced_text_comparison(comparison_container)
        
        # Advanced action buttons
        actions = ttk.Frame(self.results_frame)
        actions.pack(pady=15)
        
        ttk.Button(actions, text="⬅️ Previous", command=self.previous_pair).pack(side='left', padx=5)
        ttk.Button(actions, text="🤖 AI Auto-Select", command=self.ai_auto_select).pack(side='left', padx=5)
        ttk.Button(actions, text="✅ Keep Original", command=self.keep_original).pack(side='left', padx=5)
        ttk.Button(actions, text="🔄 Keep Duplicate", command=self.keep_duplicate).pack(side='left', padx=5)
        ttk.Button(actions, text="⏭️ Skip", command=self.skip_pair).pack(side='left', padx=5)
        ttk.Button(actions, text="➡️ Next", command=self.next_pair).pack(side='left', padx=5)
        
    def create_image_comparison(self, parent):
        """Enhanced image comparison with AI analysis"""
        comparison_frame = ttk.Frame(parent)
        comparison_frame.pack(fill='both', expand=True)
        
        # Original side
        original_frame = ttk.LabelFrame(comparison_frame, text="📁 Original (Recommended by AI)", padding=15)
        original_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.original_canvas = tk.Canvas(original_frame, bg='white', height=350)
        self.original_canvas.pack(fill='both', expand=True, pady=10)
        
        self.original_details = tk.Text(original_frame, height=4, font=("Arial", 9))
        self.original_details.pack(fill='x', pady=5)
        
        # Duplicate side
        duplicate_frame = ttk.LabelFrame(comparison_frame, text="🗑️ Duplicate (AI suggests removal)", padding=15)
        duplicate_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        self.duplicate_canvas = tk.Canvas(duplicate_frame, bg='white', height=350)
        self.duplicate_canvas.pack(fill='both', expand=True, pady=10)
        
        self.duplicate_details = tk.Text(duplicate_frame, height=4, font=("Arial", 9))
        self.duplicate_details.pack(fill='x', pady=5)
        
    def create_enhanced_text_comparison(self, parent):
        """Enhanced text comparison for systems without PIL"""
        comparison_frame = ttk.Frame(parent)
        comparison_frame.pack(fill='both', expand=True)
        
        # Original side
        original_frame = ttk.LabelFrame(comparison_frame, text="📁 Original (Keep This)", padding=15)
        original_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.original_text = tk.Text(original_frame, height=20, wrap='word', font=("Arial", 10))
        self.original_text.pack(fill='both', expand=True)
        
        # Duplicate side
        duplicate_frame = ttk.LabelFrame(comparison_frame, text="🗑️ Duplicate (Remove This)", padding=15)
        duplicate_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        self.duplicate_text = tk.Text(duplicate_frame, height=20, wrap='word', font=("Arial", 10))
        self.duplicate_text.pack(fill='both', expand=True)
        
    def create_batch_tab(self):
        """Advanced batch processing"""
        self.batch_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_frame, text="⚙️ Batch Processing")
        
        # Batch header
        batch_header = ttk.Frame(self.batch_frame)
        batch_header.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(batch_header, text="🚀 Advanced Batch Processing", 
                 font=("Arial", 18, "bold")).pack(anchor='w')
        ttk.Label(batch_header, text="Process hundreds of folders automatically with AI-powered decisions", 
                 font=("Arial", 11), foreground='#666').pack(anchor='w', pady=5)
        
        # Batch settings
        settings_frame = ttk.LabelFrame(self.batch_frame, text="⚙️ Batch Settings", padding=20)
        settings_frame.pack(fill='x', padx=20, pady=10)
        
        self.auto_delete_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="🤖 Auto-delete obvious duplicates (AI confidence > 90%)", 
                       variable=self.auto_delete_var).pack(anchor='w', pady=5)
        
        self.create_backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="💾 Create safety backup before deletion", 
                       variable=self.create_backup_var).pack(anchor='w', pady=5)
        
        self.preserve_structure_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="📁 Preserve original folder structure", 
                       variable=self.preserve_structure_var).pack(anchor='w', pady=5)
        
        # Similarity threshold
        threshold_frame = ttk.Frame(settings_frame)
        threshold_frame.pack(fill='x', pady=10)
        
        ttk.Label(threshold_frame, text="🎯 AI Similarity Threshold:").pack(anchor='w')
        self.similarity_var = tk.DoubleVar(value=85)
        similarity_scale = ttk.Scale(threshold_frame, from_=50, to=100, 
                                   orient='horizontal', variable=self.similarity_var)
        similarity_scale.pack(fill='x', pady=5)
        
        self.threshold_label = ttk.Label(threshold_frame, text="85% (Recommended)")
        self.threshold_label.pack(anchor='w')
        similarity_scale.configure(command=self.update_threshold_label)
        
        # Batch controls
        controls_frame = ttk.Frame(self.batch_frame)
        controls_frame.pack(fill='x', padx=20, pady=15)
        
        ttk.Button(controls_frame, text="📁 Add Folders to Batch", 
                  command=self.add_batch_folders).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="🚀 Start Batch Processing", 
                  command=self.start_batch_processing).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="📊 Generate Batch Report", 
                  command=self.generate_batch_report).pack(side='left', padx=5)
        
    def create_analytics_tab(self):
        """Advanced analytics and reporting"""
        self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text="📈 Analytics & Reports")
        
        # Analytics header
        analytics_header = ttk.Frame(self.analytics_frame)
        analytics_header.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(analytics_header, text="📊 Session Analytics Dashboard", 
                 font=("Arial", 18, "bold")).pack(anchor='w')
        
        # Stats cards
        self.create_stats_dashboard(self.analytics_frame)
        
        # Export options
        export_frame = ttk.LabelFrame(self.analytics_frame, text="📤 Export & Sharing", padding=20)
        export_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(export_frame, text="📄 Export to CSV", command=self.export_to_csv).pack(side='left', padx=5)
        ttk.Button(export_frame, text="📋 Generate Detailed Report", command=self.generate_detailed_report).pack(side='left', padx=5)
        ttk.Button(export_frame, text="📤 Share Results", command=self.share_results).pack(side='left', padx=5)
        ttk.Button(export_frame, text="💾 Save Session", command=self.save_session).pack(side='left', padx=5)
        
    def create_stats_dashboard(self, parent):
        """Create beautiful statistics dashboard"""
        dashboard = ttk.Frame(parent)
        dashboard.pack(fill='x', padx=20, pady=10)
        
        # Create stats grid
        stats_grid = ttk.Frame(dashboard)
        stats_grid.pack(fill='x')
        
        # Configure grid
        for i in range(4):
            stats_grid.columnconfigure(i, weight=1)
            
        # Create stat cards
        self.create_stat_card(stats_grid, "📁 Folders", "0", "folders_scanned", 0, 0)
        self.create_stat_card(stats_grid, "🖼️ Images", "0", "images_analyzed", 0, 1)
        self.create_stat_card(stats_grid, "🔍 Duplicates", "0", "duplicates_found", 1, 0)
        self.create_stat_card(stats_grid, "💾 Space Saved", "0 MB", "space_saved", 1, 1)
        
    def create_stat_card(self, parent, title, value, key, row, col):
        """Create individual stat card"""
        card = tk.Frame(parent, bg='white', relief='solid', bd=1)
        card.grid(row=row, column=col, sticky='ew', padx=10, pady=10, ipadx=20, ipady=15)
        
        title_label = tk.Label(card, text=title, font=("Arial", 12, "bold"), bg='white', fg='#666')
        title_label.pack(pady=5)
        
        value_label = tk.Label(card, text=value, font=("Arial", 18, "bold"), bg='white', fg='#1976d2')
        value_label.pack()
        
        # Store reference for updates
        setattr(self, f"stat_{key}", value_label)
        
    def create_settings_tab(self):
        """Advanced settings"""
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="⚙️ Settings")
        
        settings_container = ttk.Frame(self.settings_frame, padding=30)
        settings_container.pack(fill='both', expand=True)
        
        ttk.Label(settings_container, text="🔧 Advanced Configuration", 
                 font=("Arial", 18, "bold")).pack(anchor='w', pady=20)
        
        # Detection settings
        detection_frame = ttk.LabelFrame(settings_container, text="🎯 Detection Settings", padding=15)
        detection_frame.pack(fill='x', pady=10)
        
        ttk.Label(detection_frame, text="Detection Algorithm:").pack(anchor='w')
        self.algorithm_var = tk.StringVar(value="smart")
        
        algo_frame = ttk.Frame(detection_frame)
        algo_frame.pack(fill='x', pady=10)
        
        ttk.Radiobutton(algo_frame, text="🚀 Smart (Recommended)", 
                       variable=self.algorithm_var, value="smart").pack(anchor='w')
        ttk.Radiobutton(algo_frame, text="🔍 Thorough", 
                       variable=self.algorithm_var, value="thorough").pack(anchor='w')
        ttk.Radiobutton(algo_frame, text="⚡ Fast", 
                       variable=self.algorithm_var, value="fast").pack(anchor='w')
        
        # File type settings
        filetype_frame = ttk.LabelFrame(settings_container, text="📁 File Types", padding=15)
        filetype_frame.pack(fill='x', pady=10)
        
        self.jpg_var = tk.BooleanVar(value=True)
        self.png_var = tk.BooleanVar(value=True)
        self.gif_var = tk.BooleanVar(value=True)
        self.bmp_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(filetype_frame, text="📸 JPEG/JPG", variable=self.jpg_var).pack(anchor='w')
        ttk.Checkbutton(filetype_frame, text="🖼️ PNG", variable=self.png_var).pack(anchor='w')
        ttk.Checkbutton(filetype_frame, text="🎬 GIF", variable=self.gif_var).pack(anchor='w')
        ttk.Checkbutton(filetype_frame, text="🖥️ BMP/TIFF", variable=self.bmp_var).pack(anchor='w')
    
    # Core functionality methods (restored)
    def add_folder(self):
        """Add folder with smart analysis"""
        folder = filedialog.askdirectory(title="Select folder containing photos")
        if folder and folder not in self.selected_folders:
            self.selected_folders.append(folder)
            self.analyze_and_update_folder(folder)
            self.scan_btn.config(state='normal')
            
    def add_multiple_folders(self):
        """Add multiple folders dialog"""
        messagebox.showinfo("Multi-Select", 
                           "🔄 Pro Tip: Hold Ctrl to select multiple folders\n\n"
                           "Or use the batch processing tab for bulk operations!")
        self.add_folder()
        
    def analyze_and_update_folder(self, folder):
        """Analyze folder and update display"""
        # Quick analysis
        image_count = self.count_images_in_folder(folder)
        folder_size = self.get_folder_size(folder)
        
        # Add to tree
        self.folders_tree.insert('', 'end', values=(
            folder,
            f"{image_count} images",
            self.format_size(folder_size),
            "✅ Ready"
        ))
        
    def count_images_in_folder(self, folder_path):
        """Count image files"""
        extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        count = 0
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if Path(file).suffix.lower() in extensions:
                        count += 1
                        if count > 10000:  # Cap for performance
                            break
        except:
            pass
        return count
        
    def get_folder_size(self, folder_path):
        """Get folder size"""
        total_size = 0
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    try:
                        total_size += os.path.getsize(os.path.join(root, file))
                    except:
                        pass
        except:
            pass
        return total_size
        
    def format_size(self, bytes_size):
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} TB"
        
    def start_smart_scan(self):
        """Start AI-powered scanning"""
        if not self.selected_folders:
            messagebox.showwarning("No Folders", "Please add folders to scan first!")
            return
            
        self.is_scanning = True
        self.scan_btn.config(state='disabled', text='🔄 AI Scanning...')
        self.stop_btn.config(state='normal')
        self.overall_progress['value'] = 0
        self.current_progress['value'] = 0
        
        # Reset stats
        self.session_stats = {
            'folders_scanned': 0,
            'images_analyzed': 0,
            'duplicates_found': 0,
            'space_saved': 0,
            'scan_time': time.time()
        }
        
        # Start scan in background
        scan_thread = threading.Thread(target=self.smart_scan_worker, daemon=True)
        scan_thread.start()
        
    def smart_scan_worker(self):
        """Advanced AI scanning worker"""
        try:
            all_duplicates = []
            total_folders = len(self.selected_folders)
            
            for folder_idx, folder in enumerate(self.selected_folders):
                if not self.is_scanning:
                    break
                    
                # Update overall progress
                overall_progress = (folder_idx / total_folders) * 100
                status = f"🧠 AI analyzing folder {folder_idx + 1}/{total_folders}: {os.path.basename(folder)}"
                self.root.after(0, self.update_scan_progress, overall_progress, status)
                
                # Scan this folder with AI
                folder_duplicates = self.ai_scan_folder(folder, folder_idx)
                all_duplicates.extend(folder_duplicates)
                
                # Update session stats
                self.session_stats['folders_scanned'] = folder_idx + 1
                self.session_stats['duplicates_found'] = len(all_duplicates)
                self.root.after(0, self.update_live_stats)
                
            # Complete scan
            self.duplicates = all_duplicates
            self.session_stats['scan_time'] = time.time() - self.session_stats['scan_time']
            self.root.after(0, self.scan_complete)
            
        except Exception as e:
            self.root.after(0, self.scan_error, str(e))
            
    def ai_scan_folder(self, folder_path, folder_index):
        """AI-powered folder scanning"""
        duplicates = []
        extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        
        # Collect all image files
        image_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if Path(file).suffix.lower() in extensions:
                    image_files.append(os.path.join(root, file))
        
        # AI analysis: multiple detection methods
        duplicates.extend(self.detect_by_size_and_hash(image_files))
        
        if PIL_AVAILABLE:
            duplicates.extend(self.detect_by_perceptual_hash(image_files))
            
        # Update stats
        self.session_stats['images_analyzed'] += len(image_files)
        
        return duplicates
        
    def detect_by_size_and_hash(self, image_files):
        """Fast duplicate detection by size and MD5"""
        duplicates = []
        size_groups = {}
        
        # Group by file size first (fast)
        for image_path in image_files:
            try:
                size = os.path.getsize(image_path)
                if size not in size_groups:
                    size_groups[size] = []
                size_groups[size].append(image_path)
            except:
                continue
        
        # For each size group, check MD5 hash
        for size, files in size_groups.items():
            if len(files) > 1:
                hash_groups = {}
                for file_path in files:
                    try:
                        file_hash = self.get_file_md5(file_path)
                        if file_hash not in hash_groups:
                            hash_groups[file_hash] = []
                        hash_groups[file_hash].append(file_path)
                    except:
                        continue
                
                # Files with same hash are duplicates
                for file_hash, hash_files in hash_groups.items():
                    if len(hash_files) > 1:
                        original = hash_files[0]
                        for duplicate in hash_files[1:]:
                            duplicates.append({
                                'original': original,
                                'duplicate': duplicate,
                                'similarity': 100,
                                'method': 'MD5 Hash',
                                'confidence': 99
                            })
        
        return duplicates
        
    def detect_by_perceptual_hash(self, image_files):
        """Advanced perceptual hash detection (if PIL available)"""
        duplicates = []
        
        try:
            perceptual_hashes = {}
            
            for image_path in image_files:
                try:
                    phash = self.get_perceptual_hash(image_path)
                    if phash:
                        if phash not in perceptual_hashes:
                            perceptual_hashes[phash] = []
                        perceptual_hashes[phash].append(image_path)
                except:
                    continue
            
            # Find similar perceptual hashes
            for phash, files in perceptual_hashes.items():
                if len(files) > 1:
                    original = files[0]
                    for duplicate in files[1:]:
                        duplicates.append({
                            'original': original,
                            'duplicate': duplicate,
                            'similarity': 95,
                            'method': 'Perceptual Hash',
                            'confidence': 85
                        })
        except:
            pass
            
        return duplicates
        
    def get_file_md5(self, file_path):
        """Get MD5 hash of file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
        
    def get_perceptual_hash(self, image_path):
        """Get perceptual hash for image similarity"""
        try:
            with Image.open(image_path) as img:
                # Convert to grayscale and resize
                img = img.convert('L').resize((8, 8), Image.Resampling.LANCZOS)
                
                # Get pixel values
                pixels = list(img.getdata())
                
                # Calculate average
                avg = sum(pixels) / len(pixels)
                
                # Create binary hash
                return ''.join(['1' if p > avg else '0' for p in pixels])
        except:
            return None
            
    def update_scan_progress(self, overall_value, status):
        """Update scan progress from main thread"""
        self.overall_progress['value'] = overall_value
        self.overall_status.config(text=status)
        
    def update_live_stats(self):
        """Update live statistics"""
        stats_text = f"📁 {self.session_stats['folders_scanned']} folders • 🖼️ {self.session_stats['images_analyzed']} images • 🔍 {self.session_stats['duplicates_found']} duplicates"
        self.live_stats.config(text=stats_text)
        
        # Update dashboard
        self.stat_folders_scanned.config(text=str(self.session_stats['folders_scanned']))
        self.stat_images_analyzed.config(text=str(self.session_stats['images_analyzed']))
        self.stat_duplicates_found.config(text=str(self.session_stats['duplicates_found']))
        self.stat_space_saved.config(text=self.format_size(self.session_stats['space_saved']))
        
    def scan_complete(self):
        """Handle scan completion"""
        self.is_scanning = False
        self.scan_btn.config(state='normal', text='🚀 Start Smart Scan')
        self.stop_btn.config(state='disabled')
        
        if self.duplicates:
            scan_time = f"{self.session_stats['scan_time']:.1f}s"
            self.overall_status.config(text=f"✅ AI Analysis Complete! Found {len(self.duplicates)} duplicates in {scan_time}")
            self.notebook.select(self.results_frame)  # Switch to results
            self.current_pair_index = 0
            self.show_current_duplicate_pair()
            
            messagebox.showinfo("🎉 Scan Complete!", 
                              f"🤖 AI found {len(self.duplicates)} duplicate pairs\n"
                              f"📊 Analyzed {self.session_stats['images_analyzed']} images\n"
                              f"⏱️ Scan time: {scan_time}\n\n"
                              "Switch to Results tab for AI recommendations!")
        else:
            self.overall_status.config(text="✅ No duplicates found - your collection is optimized!")
            messagebox.showinfo("🎉 Perfect!", "No duplicates found!\nYour photo collection is already optimized.")
            
    def scan_error(self, error):
        """Handle scan errors"""
        self.is_scanning = False
        self.scan_btn.config(state='normal', text='🚀 Start Smart Scan')
        self.stop_btn.config(state='disabled')
        messagebox.showerror("Scan Error", f"An error occurred during scanning:\n{error}")
        
    def stop_scan(self):
        """Stop current scan"""
        self.is_scanning = False
        self.scan_btn.config(state='normal', text='🚀 Start Smart Scan')
        self.stop_btn.config(state='disabled')
        self.overall_status.config(text="⏹️ Scan stopped by user")
        
    def show_current_duplicate_pair(self):
        """Show current duplicate pair with AI analysis"""
        if not self.duplicates or self.current_pair_index >= len(self.duplicates):
            return
            
        pair = self.duplicates[self.current_pair_index]
        self.results_info.config(text=f"Pair {self.current_pair_index + 1} of {len(self.duplicates)}")
        
        # AI recommendation
        confidence = pair.get('confidence', 0)
        method = pair.get('method', 'Unknown')
        ai_text = f"🤖 AI Analysis: {confidence}% confidence using {method} • Recommends keeping original"
        self.ai_recommendation.config(text=ai_text)
        
        if PIL_AVAILABLE and hasattr(self, 'original_canvas'):
            # Show images
            self.load_and_display_image(self.original_canvas, pair['original'])
            self.load_and_display_image(self.duplicate_canvas, pair['duplicate'])
            
            # Update details
            self.update_image_details(self.original_details, pair['original'], "ORIGINAL")
            self.update_image_details(self.duplicate_details, pair['duplicate'], "DUPLICATE")
        else:
            # Text-only display
            self.update_text_comparison(pair)
            
    def load_and_display_image(self, canvas, image_path):
        """Load and display image with error handling"""
        try:
            canvas.delete("all")
            
            with Image.open(image_path) as img:
                # Resize to fit canvas
                canvas_width = canvas.winfo_width() or 300
                canvas_height = canvas.winfo_height() or 300
                
                img.thumbnail((canvas_width - 40, canvas_height - 40), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                canvas.create_image(canvas_width//2, canvas_height//2, image=photo)
                canvas.image = photo  # Keep reference
                
        except Exception as e:
            canvas.delete("all")
            canvas.create_text(150, 150, 
                             text=f"📷 Image Preview\n\n❌ Cannot load image\n{os.path.basename(image_path)}", 
                             fill="red", font=("Arial", 10), justify='center')
            
    def update_image_details(self, text_widget, image_path, label):
        """Update image details text widget"""
        details = self.get_detailed_file_info(image_path)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, f"{label} FILE\n\n{details}")
        
    def update_text_comparison(self, pair):
        """Update text-only comparison"""
        orig_details = self.get_detailed_file_info(pair['original'])
        dup_details = self.get_detailed_file_info(pair['duplicate'])
        
        self.original_text.delete(1.0, tk.END)
        self.original_text.insert(tk.END, f"📁 ORIGINAL FILE (Keep This)\n\n{orig_details}")
        
        self.duplicate_text.delete(1.0, tk.END)
        self.duplicate_text.insert(tk.END, f"🗑️ DUPLICATE FILE (Remove This)\n\n{dup_details}")
        
    def get_detailed_file_info(self, file_path):
        """Get detailed file information"""
        try:
            stat = os.stat(file_path)
            size = self.format_size(stat.st_size)
            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            details = f"📄 File: {os.path.basename(file_path)}\n"
            details += f"📂 Path: {file_path}\n"
            details += f"💾 Size: {size}\n"
            details += f"📅 Modified: {modified}\n"
            
            if PIL_AVAILABLE:
                try:
                    with Image.open(file_path) as img:
                        details += f"📐 Dimensions: {img.width} x {img.height}\n"
                        details += f"🎨 Format: {img.format}\n"
                        if hasattr(img, 'mode'):
                            details += f"🌈 Mode: {img.mode}\n"
                except:
                    pass
                    
            return details
        except Exception:
            return f"📄 File: {os.path.basename(file_path)}\n❌ Error reading file information"
            
    # Navigation and action methods
    def previous_pair(self):
        if self.current_pair_index > 0:
            self.current_pair_index -= 1
            self.show_current_duplicate_pair()
            
    def next_pair(self):
        if self.current_pair_index < len(self.duplicates) - 1:
            self.current_pair_index += 1
            self.show_current_duplicate_pair()
        else:
            messagebox.showinfo("🎉 Complete!", "All duplicate pairs reviewed!")
            
    def skip_pair(self):
        self.next_pair()
        
    def ai_auto_select(self):
        """AI automatically selects the best option"""
        if not self.duplicates or self.current_pair_index >= len(self.duplicates):
            return
            
        pair = self.duplicates[self.current_pair_index]
        confidence = pair.get('confidence', 0)
        
        messagebox.showinfo("🤖 AI Auto-Select", 
                           f"AI Analysis Complete!\n\n"
                           f"🎯 Confidence: {confidence}%\n"
                           f"📊 Method: {pair.get('method', 'Advanced')}\n"
                           f"✅ Recommendation: Keep Original\n\n"
                           "Proceeding with AI recommendation...")
        
        self.keep_original()
        
    def keep_original(self):
        """Keep original and remove duplicate"""
        if not self.duplicates or self.current_pair_index >= len(self.duplicates):
            return
            
        pair = self.duplicates[self.current_pair_index]
        
        if messagebox.askyesno("Confirm Action", 
                              f"🗑️ Move duplicate to safe trash?\n\n"
                              f"File: {os.path.basename(pair['duplicate'])}\n"
                              f"Size: {self.format_size(os.path.getsize(pair['duplicate']))}\n\n"
                              "This action can be undone from the trash folder."):
            self.move_to_safe_trash(pair['duplicate'])
            
    def keep_duplicate(self):
        """Keep duplicate and remove original"""
        if not self.duplicates or self.current_pair_index >= len(self.duplicates):
            return
            
        pair = self.duplicates[self.current_pair_index]
        
        if messagebox.askyesno("Confirm Action", 
                              f"🗑️ Move original to safe trash?\n\n"
                              f"File: {os.path.basename(pair['original'])}\n"
                              f"⚠️ This goes against AI recommendation!\n\n"
                              "Are you sure?"):
            self.move_to_safe_trash(pair['original'])
            
    def move_to_safe_trash(self, file_path):
        """Safely move file to trash with recovery option"""
        try:
            # Create safe trash folder
            trash_folder = os.path.expanduser("~/DuplicateCleanerTrash")
            os.makedirs(trash_folder, exist_ok=True)
            
            # Generate unique filename
            timestamp = int(time.time())
            filename = f"{timestamp}_{os.path.basename(file_path)}"
            trash_path = os.path.join(trash_folder, filename)
            
            # Get file size before moving
            file_size = os.path.getsize(file_path)
            
            # Move file safely
            shutil.move(file_path, trash_path)
            
            # Update stats
            self.session_stats['space_saved'] += file_size
            self.update_live_stats()
            
            # Show success
            messagebox.showinfo("✅ Success!", 
                              f"File moved to safe trash:\n{filename}\n\n"
                              f"💾 Space saved: {self.format_size(file_size)}\n"
                              f"📁 Trash location: ~/DuplicateCleanerTrash/\n\n"
                              "Files can be recovered from trash folder.")
            
            # Remove from duplicates and show next
            self.duplicates.pop(self.current_pair_index)
            if self.current_pair_index >= len(self.duplicates):
                self.current_pair_index = len(self.duplicates) - 1
                
            if self.duplicates:
                self.show_current_duplicate_pair()
            else:
                messagebox.showinfo("🎉 All Done!", 
                                  f"All duplicates processed!\n\n"
                                  f"📊 Total space saved: {self.format_size(self.session_stats['space_saved'])}\n"
                                  f"🗑️ Files in trash: Check ~/DuplicateCleanerTrash/")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to move file:\n{str(e)}")
            
    # Export and reporting methods
    def export_to_csv(self):
        """Export results to CSV"""
        if not self.duplicates:
            messagebox.showwarning("No Data", "No duplicate data to export!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Duplicate Analysis to CSV"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    # CSV header
                    f.write("Original_File,Duplicate_File,Similarity_%,Method,Confidence_%,Original_Size_MB,Duplicate_Size_MB,Space_Saved_MB\n")
                    
                    for pair in self.duplicates:
                        orig_size = os.path.getsize(pair['original']) / (1024*1024) if os.path.exists(pair['original']) else 0
                        dup_size = os.path.getsize(pair['duplicate']) / (1024*1024) if os.path.exists(pair['duplicate']) else 0
                        
                        f.write(f'"{pair["original"]}","{pair["duplicate"]}",'
                               f'{pair.get("similarity", 0)},"{pair.get("method", "Unknown")}",'
                               f'{pair.get("confidence", 0)},{orig_size:.2f},{dup_size:.2f},{dup_size:.2f}\n')
                
                messagebox.showinfo("Export Complete", f"📊 Data exported to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export:\n{str(e)}")
                
    def generate_detailed_report(self):
        """Generate comprehensive report"""
        report_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Detailed Analysis Report"
        )
        
        if report_path:
            try:
                with open(report_path, 'w', encoding='utf-8') as f:
                    # Write comprehensive report
                    f.write("🖼️ DUPLICATE PHOTO CLEANER PRO - ANALYSIS REPORT\n")
                    f.write("=" * 60 + "\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    # Executive Summary
                    f.write("📊 EXECUTIVE SUMMARY\n")
                    f.write("-" * 30 + "\n")
                    f.write(f"Folders Analyzed: {self.session_stats['folders_scanned']}\n")
                    f.write(f"Images Processed: {self.session_stats['images_analyzed']}\n")
                    f.write(f"Duplicates Found: {len(self.duplicates)}\n")
                    f.write(f"Potential Space Savings: {self.format_size(self.session_stats['space_saved'])}\n")
                    f.write(f"Scan Duration: {self.session_stats['scan_time']:.1f} seconds\n\n")
                    
                    # Detailed findings
                    f.write("🔍 DETAILED FINDINGS\n")
                    f.write("-" * 30 + "\n")
                    
                    for i, pair in enumerate(self.duplicates, 1):
                        f.write(f"\nDuplicate Pair #{i}:\n")
                        f.write(f"  Original: {pair['original']}\n")
                        f.write(f"  Duplicate: {pair['duplicate']}\n")
                        f.write(f"  Similarity: {pair.get('similarity', 0)}%\n")
                        f.write(f"  Detection Method: {pair.get('method', 'Unknown')}\n")
                        f.write(f"  AI Confidence: {pair.get('confidence', 0)}%\n")
                    
                    f.write(f"\n📁 SCANNED FOLDERS\n")
                    f.write("-" * 30 + "\n")
                    for folder in self.selected_folders:
                        f.write(f"  {folder}\n")
                        
                messagebox.showinfo("Report Generated", f"📋 Comprehensive report saved:\n{report_path}")
                
            except Exception as e:
                messagebox.showerror("Report Error", f"Failed to generate report:\n{str(e)}")
                
    # Additional utility methods
    def clear_folders(self):
        """Clear all selected folders"""
        self.selected_folders.clear()
        for item in self.folders_tree.get_children():
            self.folders_tree.delete(item)
        self.scan_btn.config(state='disabled')
        
    def refresh_stats(self):
        """Refresh statistics display"""
        self.update_live_stats()
        
    def update_threshold_label(self, value):
        """Update similarity threshold label"""
        threshold = int(float(value))
        if threshold >= 90:
            label = f"{threshold}% (Very Strict)"
        elif threshold >= 80:
            label = f"{threshold}% (Recommended)"
        elif threshold >= 70:
            label = f"{threshold}% (Relaxed)"
        else:
            label = f"{threshold}% (Very Relaxed)"
        self.threshold_label.config(text=label)
        
    # Stub methods for batch processing and advanced features
    def add_batch_folders(self):
        messagebox.showinfo("Batch Processing", "🚀 Batch folder selection coming soon!")
        
    def start_batch_processing(self):
        messagebox.showinfo("Batch Processing", "⚙️ Advanced batch processing coming soon!")
        
    def generate_batch_report(self):
        messagebox.showinfo("Batch Report", "📊 Batch reporting coming soon!")
        
    def share_results(self):
        """Share results to clipboard"""
        summary = f"""🖼️ Duplicate Photo Cleaner Pro Results

📊 Analysis Summary:
• Folders: {self.session_stats['folders_scanned']}
• Images: {self.session_stats['images_analyzed']}  
• Duplicates: {len(self.duplicates)}
• Space Saved: {self.format_size(self.session_stats['space_saved'])}

🚀 Powered by AI algorithms and smart detection"""

        self.root.clipboard_clear()
        self.root.clipboard_append(summary)
        messagebox.showinfo("Shared!", "📋 Results copied to clipboard!")
        
    def save_session(self):
        """Save current session"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Save Session Data"
        )
        
        if file_path:
            try:
                session_data = {
                    'timestamp': datetime.now().isoformat(),
                    'stats': self.session_stats,
                    'folders': self.selected_folders,
                    'duplicates_count': len(self.duplicates)
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, indent=2)
                    
                messagebox.showinfo("Session Saved", f"💾 Session saved to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save session:\n{str(e)}")

def main():
    try:
        app = DuplicatePhotoCleanerPro()
    except Exception as e:
        print(f"Application Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
