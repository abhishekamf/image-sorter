"""
Login and registration window
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database.manager import DatabaseManager

class LoginWindow:
    def __init__(self, parent, success_callback):
        self.parent = parent
        self.success_callback = success_callback
        self.db = DatabaseManager()
        
        self.setup_ui()

    def setup_ui(self):
        """Setup the login UI"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(expand=True, fill='both')
        
        # Center frame
        center_frame = ttk.Frame(main_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title
        title_label = ttk.Label(center_frame, text="Duplicate Photo Cleaner", 
                               font=('Arial', 20, 'bold'))
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(center_frame, text="Find and safely remove duplicate photos", 
                                  font=('Arial', 10))
        subtitle_label.pack(pady=(0, 30))
        
        # Login form
        form_frame = ttk.LabelFrame(center_frame, text="Login / Register", padding=20)
        form_frame.pack(padx=20, pady=10)
        
        # Username
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky='w', pady=5)
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky='ew')
        
        # Password
        ttk.Label(form_frame, text="Password:").grid(row=2, column=0, sticky='w', pady=5)
        self.password_entry = ttk.Entry(form_frame, show="*", width=30)
        self.password_entry.grid(row=3, column=0, columnspan=2, pady=(0, 20), sticky='ew')
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        login_btn = ttk.Button(button_frame, text="Login", command=self.login)
        login_btn.pack(side='left', padx=(0, 10))
        
        register_btn = ttk.Button(button_frame, text="Register", command=self.register)
        register_btn.pack(side='left')
        
        # Bind Enter key
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Focus on username entry
        self.username_entry.focus()

    def login(self):
        """Handle login attempt"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Warning", "Please enter both username and password")
            return
        
        user_id = self.db.authenticate_user(username, password)
        if user_id:
            user_data = {'id': user_id, 'username': username}
            self.success_callback(user_data)
        else:
            messagebox.showerror("Error", "Invalid username or password")
            self.password_entry.delete(0, 'end')

    def register(self):
        """Handle registration attempt"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Warning", "Please enter both username and password")
            return
        
        if len(password) < 6:
            messagebox.showwarning("Warning", "Password must be at least 6 characters long")
            return
        
        user_id = self.db.register_user(username, password)
        if user_id:
            messagebox.showinfo("Success", "Registration successful! You can now login.")
            self.password_entry.delete(0, 'end')
        else:
            messagebox.showerror("Error", "Username already exists")
