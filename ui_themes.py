"""
Modern UI themes and styling
"""
import tkinter as tk
from tkinter import ttk

class ModernTheme:
    # Dark theme colors
    DARK = {
        'bg': '#2b2b2b',
        'fg': '#ffffff',
        'select_bg': '#404040',
        'button_bg': '#0078d4',
        'button_hover': '#106ebe',
        'accent': '#00d4aa',
        'danger': '#ff4444',
        'warning': '#ffaa00'
    }
    
    # Light theme colors  
    LIGHT = {
        'bg': '#f0f0f0',
        'fg': '#000000', 
        'select_bg': '#e0e0e0',
        'button_bg': '#0078d4',
        'button_hover': '#106ebe',
        'accent': '#00aa88',
        'danger': '#cc3333',
        'warning': '#cc8800'
    }
    
    @staticmethod
    def apply_dark_theme(root):
        """Apply dark theme to the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('TFrame', background=ModernTheme.DARK['bg'])
        style.configure('TLabel', background=ModernTheme.DARK['bg'], 
                       foreground=ModernTheme.DARK['fg'])
        style.configure('TButton', background=ModernTheme.DARK['button_bg'],
                       foreground='white')
        
        root.configure(bg=ModernTheme.DARK['bg'])
