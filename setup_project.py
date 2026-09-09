#!/usr/bin/env python3
import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.lstrip('\n'))
    print(f"  ✓ {path}")

def main():
    print("=" * 60)
    print("  DUPLICATE PHOTO CLEANER - Project Setup")
    print("=" * 60)
    
    # 1. requirements.txt
    create_file("requirements.txt", "Pillow>=10.0.0\nbcrypt>=4.0.0\npyinstaller>=6.0.0\n")

    # 2. main.py
    create_file("main.py", """#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from gui.app import DuplicatePhotoCleaner
from tkinter import Tk

def main():
    try:
        from PIL import Image
        import bcrypt
    except ImportError:
        print("Install requirements: pip install -r requirements.txt")
        sys.exit(1)
    root = Tk()
    app = DuplicatePhotoCleaner(root)
    root.mainloop()

if __name__ == "__main__":
    main()
""")

    # 3. Init files
    create_file("src/__init__.py", "")
    create_file("src/database/__init__.py", "")
    create_file("src/core/__init__.py", "")
    create_file("src/gui/__init__.py", "")

    # 4. Database Manager
    create_file("src/database/manager.py", '''import sqlite3, os, datetime, bcrypt

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.expanduser("~"), ".duplicate_photo_cleaner")
            os.makedirs(db_path, exist_ok=True)
            db_path = os.path.join(db_path, "app.db")
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, action TEXT NOT NULL,
            file_path TEXT NOT NULL, hash_value TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id))""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS settings (
            user_id INTEGER PRIMARY KEY,
            retention_months INTEGER DEFAULT 6,
            holding_folder TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id))""")
        self.conn.commit()

    def register_user(self, username, password):
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        try:
            self.cursor.execute("INSERT INTO users (username, password_hash) VALUES (?,?)", (username, pw_hash))
            self.conn.commit()
            uid = self.cursor.lastrowid
            self.cursor.execute("INSERT INTO settings (user_id, retention_months) VALUES (?,6)", (uid,))
            self.conn.commit()
            return uid
        except sqlite3.IntegrityError:
            return None

    def authenticate_user(self, username, password):
        self.cursor.execute("SELECT id, password_hash FROM users WHERE username=?", (username,))
        row = self.cursor.fetchone()
        if row and bcrypt.checkpw(password.encode(), row[1].encode()):
            return row[0]
        return None

    def log_action(self, user_id, action, file_path, hash_value=None):
        self.cursor.execute("INSERT INTO history (user_id, action, file_path, hash_value) VALUES (?,?,?,?)",
                          (user_id, action, file_path, hash_value))
        self.conn.commit()

    def clean_old_history(self, user_id, months):
        cutoff = datetime.datetime.now() - datetime.timedelta(days=months*30)
        self.cursor.execute("DELETE FROM history WHERE user_id=? AND timestamp<?", (user_id, cutoff))
        self.conn.commit()

    def get_history(self, user_id, limit=100):
        self.cursor.execute("SELECT action, file_path, timestamp FROM history WHERE user_id=? ORDER BY timestamp DESC LIMIT ?",
                          (user_id, limit))
        return self.cursor.fetchall()

    def get_settings(self, user_id):
        self.cursor.execute("SELECT retention_months, holding_folder FROM settings WHERE user_id=?", (user_id,))
        return self.cursor.fetchone()

    def update_settings(self, user_id, retention_months, holding_folder):
        self.cursor.execute("UPDATE settings SET retention_months=?, holding_folder=? WHERE user_id=?",
                          (retention_months, holding_folder, user_id))
        self.conn.commit()

    def close(self):
        self.conn.close()
''')

    # 5. Core Detector
    create_file("src/core/detector.py", '''import os, datetime, shutil
from pathlib import Path
from PIL import Image

class DuplicateDetector:
    def __init__(self, db_manager, user_id):
        self.db = db_manager
        self.user_id = user_id
        self.is_scanning = False

    def get_image_hash(self, file_path):
        try:
            with Image.open(file_path) as img:
                if img.mode != 'RGB': img = img.convert('RGB')
                img = img.resize((8,8), Image.LANCZOS).convert('L')
                pixels = list(img.getdata())
                avg = sum(pixels) / len(pixels)
                return ''.join(['1' if p > avg else '0' for p in pixels])
        except: return None

    def find_duplicates(self, folder_path, progress_callback=None):
        exts = {'.jpg','.jpeg','.png','.gif','.bmp','.tiff','.webp'}
        hash_map, duplicates = {}, []
        files = []
        for root, _, filenames in os.walk(folder_path):
            for f in filenames:
                if Path(f).suffix.lower() in exts:
                    files.append(os.path.join(root, f))
        self.is_scanning = True
        for i, fp in enumerate(files):
            if not self.is_scanning: break
            if progress_callback: progress_callback(i+1, len(files), fp)
            h = self.get_image_hash(fp)
            if h:
                if h in hash_map:
                    duplicates.append({'original': hash_map[h], 'duplicate': fp, 'hash': h})
                else:
                    hash_map[h] = fp
        self.is_scanning = False
        return duplicates

    def move_to_holding(self, file_path, holding_folder):
        os.makedirs(holding_folder, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(holding_folder, f"{ts}_{Path(file_path).name}")
        shutil.move(file_path, dest)
        self.db.log_action(self.user_id, "moved_to_holding", file_path, self.get_image_hash(file_path))
        return dest

    def permanently_delete(self, holding_folder):
        if not os.path.exists(holding_folder): return []
        deleted = []
        for fn in os.listdir(holding_folder):
            fp = os.path.join(holding_folder, fn)
            try:
                os.remove(fp)
                deleted.append(fp)
                self.db.log_action(self.user_id, "permanently_deleted", fp)
            except: pass
        return deleted

    def stop_scanning(self):
        self.is_scanning = False
''')

    # 6. GUI App
    create_file("src/gui/app.py", '''import os, threading
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from database.manager import DatabaseManager
from core.detector import DuplicateDetector

COLORS = {
    'bg': '#f0f0f0', 'primary': '#2196F3', 'secondary': '#4CAF50',
    'danger': '#f44336', 'warning': '#FF9800', 'info': '#00BCD4',
    'text': '#333', 'white': '#FFF', 'light': '#F5F5F5'
}

class DuplicatePhotoCleaner:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate Photo Cleaner")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        self.db = DatabaseManager()
        self.current_user = None
        self.detector = None
        self.duplicates = []
        self.current_idx = 0
        self.show_login()

    def clear(self):
        for w in self.root.winfo_children(): w.destroy()

    def show_login(self):
        self.clear()
        main = Frame(self.root, bg=COLORS['primary'])
        main.pack(expand=True, fill=BOTH)
        card = Frame(main, bg='white', padx=50, pady=40)
        card.place(relx=0.5, rely=0.5, anchor=CENTER)
        Label(card, text="Duplicate Photo Cleaner", font=('Segoe UI', 22, 'bold'), bg='white').pack(pady=(10,5))
        Label(card, text="Find and remove duplicate photos safely", font=('Segoe UI', 11), bg='white', fg='gray').pack(pady=(0,20))
        Frame(card, height=2, bg=COLORS['light']).pack(fill=X, pady=10)

        f = Frame(card, bg='white')
        f.pack(pady=10)
        Label(f, text="Username:", bg='white', font=('Segoe UI', 11)).grid(row=0, column=0, pady=(10,5), sticky='w')
        self.u_entry = Entry(f, font=('Segoe UI', 11), width=30, relief='solid', borderwidth=1)
        self.u_entry.grid(row=1, column=0, pady=(0,15), ipady=5)
        Label(f, text="Password:", bg='white', font=('Segoe UI', 11)).grid(row=2, column=0, pady=(5,5), sticky='w')
        self.p_entry = Entry(f, show="*", font=('Segoe UI', 11), width=30, relief='solid', borderwidth=1)
        self.p_entry.grid(row=3, column=0, pady=(0,20), ipady=5)
        self.p_entry.bind('<Return>', lambda e: self.login())

        bf = Frame(card, bg='white')
        bf.pack(pady=10)
        Button(bf, text="Login", command=self.login, bg=COLORS['primary'], fg='white',
               font=('Segoe UI', 11, 'bold'), width=12, relief='flat', cursor='hand2').pack(side=LEFT, padx=5, ipady=5)
        Button(bf, text="Register", command=self.register, bg=COLORS['secondary'], fg='white',
               font=('Segoe UI', 11, 'bold'), width=12, relief='flat', cursor='hand2').pack(side=LEFT, padx=5, ipady=5)

    def login(self):
        u, p = self.u_entry.get().strip(), self.p_entry.get()
        if not u or not p: messagebox.showwarning("Warning", "Enter username and password"); return
        uid = self.db.authenticate_user(u, p)
        if uid:
            self.current_user = {'id': uid, 'username': u}
            self.detector = DuplicateDetector(self.db, uid)
            self.show_main()
        else: messagebox.showerror("Error", "Invalid credentials")

    def register(self):
        u, p = self.u_entry.get().strip(), self.p_entry.get()
        if not u or not p: messagebox.showwarning("Warning", "Enter username and password"); return
        if len(p) < 6: messagebox.showwarning("Warning", "Password must be 6+ characters"); return
        if self.db.register_user(u, p): messagebox.showinfo("Success", "Registered! Please login.")
        else: messagebox.showerror("Error", "Username exists")

    def show_main(self):
        self.clear()
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        fm = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=fm)
        fm.add_command(label="Select Folder & Scan", command=self.select_folder)
        fm.add_separator()
        fm.add_command(label="Settings", command=self.show_settings)
        fm.add_separator()
        fm.add_command(label="Logout", command=self.show_login)
        fm.add_command(label="Exit", command=self.root.quit)
        hm = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="History", menu=hm)
        hm.add_command(label="View History", command=self.show_history)
        hm.add_command(label="Clean Old History", command=self.clean_history)

        self.main_frame = Frame(self.root, bg=COLORS['bg'])
        self.main_frame.pack(fill=BOTH, expand=True)

        toolbar = Frame(self.main_frame, bg='white', height=60)
        toolbar.pack(fill=X)
        toolbar.pack_propagate(False)
        Label(toolbar, text=f"User: {self.current_user['username']}", font=('Segoe UI', 14, 'bold'), bg='white').pack(side=LEFT, padx=20, pady=10)
        self.scan_btn = Button(toolbar, text="Select Folder & Scan", command=self.select_folder,
                               bg=COLORS['primary'], fg='white', font=('Segoe UI', 11, 'bold'), relief='flat', cursor='hand2')
        self.scan_btn.pack(side=RIGHT, padx=20, pady=10, ipady=5)

        nb = ttk.Notebook(self.main_frame)
        nb.pack(fill=BOTH, expand=True, padx=10, pady=5)
        self.dup_frame = Frame(nb, bg='white')
        nb.add(self.dup_frame, text=" Duplicates ")
        self.hold_frame = Frame(nb, bg='white')
        nb.add(self.hold_frame, text=" Holding Folder ")
        self.setup_duplicates()
        self.setup_holding()

    def setup_duplicates(self):
        self.prog_frame = Frame(self.dup_frame, bg='white')
        self.prog_label = Label(self.prog_frame, text="", bg='white')
        self.prog_label.pack()
        self.prog_bar = ttk.Progressbar(self.prog_frame, length=500, mode='determinate')
        self.prog_bar.pack(pady=5, fill=X)

        cf = Frame(self.dup_frame, bg='white')
        cf.pack(fill=BOTH, expand=True, padx=20, pady=10)
        imgf = Frame(cf, bg='white')
        imgf.pack(fill=BOTH, expand=True)

        op = Frame(imgf, bg=COLORS['light'], relief='solid', borderwidth=1)
        op.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        oh = Frame(op, bg=COLORS['secondary'])
        oh.pack(fill=X)
        Label(oh, text="Original (Keep)", font=('Segoe UI', 12, 'bold'), bg=COLORS['secondary'], fg='white', pady=8).pack()
        self.orig_label = Label(op, bg=COLORS['light'], text="Select a folder to scan", font=('Segoe UI', 11))
        self.orig_label.pack(expand=True, fill=BOTH, padx=10, pady=10)

        dp = Frame(imgf, bg=COLORS['light'], relief='solid', borderwidth=1)
        dp.pack(side=RIGHT, fill=BOTH, expand=True, padx=5, pady=5)
        dh = Frame(dp, bg=COLORS['danger'])
        dh.pack(fill=X)
        Label(dh, text="Duplicate (Remove)", font=('Segoe UI', 12, 'bold'), bg=COLORS['danger'], fg='white', pady=8).pack()
        self.dup_label = Label(dp, bg=COLORS['light'], text="Select a folder to scan", font=('Segoe UI', 11))
        self.dup_label.pack(expand=True, fill=BOTH, padx=10, pady=10)

        infof = Frame(cf, bg='white')
        infof.pack(fill=X, pady=5)
        self.orig_info = Label(infof, text="", bg='white', font=('Segoe UI', 9), fg='gray', anchor='w')
        self.orig_info.pack(side=LEFT, padx=10)
        self.dup_info = Label(infof, text="", bg='white', font=('Segoe UI', 9), fg='gray', anchor='e')
        self.dup_info.pack(side=RIGHT, padx=10)

        af = Frame(cf, bg='white')
        af.pack(pady=15)
        self.keep_btn = Button(af, text="Keep Original", command=self.keep_original,
                               bg=COLORS['secondary'], fg='white', font=('Segoe UI', 11, 'bold'), relief='flat', state='disabled')
        self.keep_btn.pack(side=LEFT, padx=5, ipady=8)
        self.skip_btn = Button(af, text="Skip", command=self.skip_pair,
                               bg=COLORS['warning'], fg='white', font=('Segoe UI', 11, 'bold'), relief='flat', state='disabled')
        self.skip_btn.pack(side=LEFT, padx=5, ipady=8)
        self.stop_btn = Button(af, text="Stop", command=self.stop_scan,
                               bg=COLORS['danger'], fg='white', font=('Segoe UI', 11, 'bold'), relief='flat', state='disabled')
        self.stop_btn.pack(side=LEFT, padx=5, ipady=8)

        sf = Frame(self.dup_frame, bg=COLORS['light'], relief='sunken', borderwidth=1)
        sf.pack(fill=X, side=BOTTOM)
        self.status = Label(sf, text="Ready. Select a folder to scan.", bg=COLORS['light'], font=('Segoe UI', 10), anchor='w', padx=10, pady=5)
        self.status.pack(fill=X)

    def setup_holding(self):
        infof = Frame(self.hold_frame, bg='white')
        infof.pack(fill=X, padx=20, pady=(20,10))
        Label(infof, text="Holding Folder", font=('Segoe UI', 16, 'bold'), bg='white').pack(anchor='w')
        Label(infof, text="Files here are NOT deleted permanently. Review and delete when ready.",
              bg='white', font=('Segoe UI', 10), fg='gray').pack(anchor='w', pady=5)

        cf = Frame(self.hold_frame, bg='white')
        cf.pack(fill=BOTH, expand=True, padx=20, pady=10)
        lf = Frame(cf, bg='white')
        lf.pack(fill=BOTH, expand=True)
        sb = Scrollbar(lf)
        sb.pack(side=RIGHT, fill=Y)
        self.hold_list = Listbox(lf, yscrollcommand=sb.set, font=('Segoe UI', 10), relief='solid', borderwidth=1)
        self.hold_list.pack(fill=BOTH, expand=True)
        sb.config(command=self.hold_list.yview)

        af = Frame(self.hold_frame, bg='white')
        af.pack(pady=15)
        Button(af, text="Delete All Permanently", command=self.clear_holding,
               bg=COLORS['danger'], fg='white', font=('Segoe UI', 11, 'bold'), relief='flat').pack(side=LEFT, padx=5, ipady=8)
        Button(af, text="Refresh", command=self.refresh_holding,
               bg=COLORS['info'], fg='white', font=('Segoe UI', 11, 'bold'), relief='flat').pack(side=LEFT, padx=5, ipady=8)
        self.refresh_holding()

    def select_folder(self):
        fp = filedialog.askdirectory(title="Select folder with photos")
        if fp: self.start_scan(fp)

    def start_scan(self, folder):
        s = self.db.get_settings(self.current_user['id'])
        hf = s[1] if s and s[1] else os.path.join(os.path.expanduser("~"), ".duplicate_photo_cleaner", "holding")
        if not s or not s[1]: self.db.update_settings(self.current_user['id'], s[0] if s else 6, hf)
        self.detector = DuplicateDetector(self.db, self.current_user['id'])
        self.prog_frame.pack(fill=X, padx=20, pady=10)
        self.prog_bar['value'] = 0
        self.status.config(text=f"Scanning: {folder}")
        self.scan_btn.config(state='disabled')
        self.keep_btn.config(state='disabled')
        self.skip_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        t = threading.Thread(target=self.scan_thread, args=(folder,))
        t.daemon = True
        t.start()

    def scan_thread(self, folder):
        def cb(curr, total, fp):
            self.root.after(0, lambda: self.prog_bar.config(value=curr, maximum=total))
            self.root.after(0, lambda: self.prog_label.config(text=f"Scanning: {os.path.basename(fp)} ({curr}/{total})"))
        dups = self.detector.find_duplicates(folder, cb)
        self.root.after(0, lambda: self.scan_done(dups))

    def scan_done(self, dups):
        self.prog_frame.pack_forget()
        self.scan_btn.config(state='normal')
        self.duplicates = dups
        if not dups: self.status.config(text="No duplicates found."); return
        self.current_idx = 0
        self.status.config(text=f"Found {len(dups)} duplicate pairs.")
        self.keep_btn.config(state='normal')
        self.skip_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.show_pair()

    def show_pair(self):
        if self.current_idx >= len(self.duplicates):
            self.status.config(text="All done!"); self.keep_btn.config(state='disabled'); self.skip_btn.config(state='disabled'); return
        p = self.duplicates[self.current_idx]
        self.show_image(self.orig_label, p['original'])
        self.show_image(self.dup_label, p['duplicate'])
        self.orig_info.config(text=f"File: {os.path.basename(p['original'])}")
        self.dup_info.config(text=f"File: {os.path.basename(p['duplicate'])}")
        self.status.config(text=f"Pair {self.current_idx+1}/{len(self.duplicates)}")

    def show_image(self, label, path):
        try:
            img = Image.open(path)
            img.thumbnail((350,350), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label.config(image=photo, text=""); label.image = photo
        except: label.config(image="", text=f"Error: {os.path.basename(path)}")

    def keep_original(self):
        if self.current_idx >= len(self.duplicates): return
        p = self.duplicates[self.current_idx]
        s = self.db.get_settings(self.current_user['id'])
        hf = s[1] if s else os.path.join(os.path.expanduser("~"), ".duplicate_photo_cleaner", "holding")
        self.detector.move_to_holding(p['duplicate'], hf)
        self.current_idx += 1
        self.show_pair()

    def skip_pair(self):
        self.current_idx += 1; self.show_pair()

    def stop_scan(self):
        self.detector.stop_scanning()
        self.prog_frame.pack_forget()
        self.scan_btn.config(state='normal')
        self.status.config(text="Scan stopped.")

    def refresh_holding(self):
        s = self.db.get_settings(self.current_user['id'])
        hf = s[1] if s else os.path.join(os.path.expanduser("~"), ".duplicate_photo_cleaner", "holding")
        self.hold_list.delete(0, END)
        if not os.path.exists(hf): self.hold_list.insert(END, "Empty"); return
        files = os.listdir(hf)
        if not files: self.hold_list.insert(END, "Empty")
        else:
            for fn in files:
                sz = os.path.getsize(os.path.join(hf, fn))
                szs = f"{sz/1024:.1f} KB" if sz < 1024*1024 else f"{sz/(1024*1024):.1f} MB"
                self.hold_list.insert(END, f"{fn} ({szs})")

    def clear_holding(self):
        if not messagebox.askyesno("Confirm", "Permanently delete ALL files in holding folder?"): return
        s = self.db.get_settings(self.current_user['id'])
        hf = s[1] if s else os.path.join(os.path.expanduser("~"), ".duplicate_photo_cleaner", "holding")
        deleted = self.detector.permanently_delete(hf)
        messagebox.showinfo("Done", f"Deleted {len(deleted)} files permanently.")
        self.refresh_holding()

    def show_settings(self):
        w = Toplevel(self.root); w.title("Settings"); w.geometry("500x400"); w.configure(bg='white')
        cs = self.db.get_settings(self.current_user['id'])
        cur_ret = cs[0] if cs else 6
        cur_hold = cs[1] if cs else ""
        Label(w, text="History Retention", font=('Segoe UI', 12, 'bold'), bg='white').pack(pady=20)
        rv = StringVar(value=str(cur_ret))
        for m in [1,3,6,12]:
            Radiobutton(w, text=f"{m} month{'s' if m>1 else ''}", variable=rv, value=str(m), bg='white', font=('Segoe UI', 11)).pack(anchor='w', padx=40, pady=2)
        Label(w, text="Holding Folder", font=('Segoe UI', 12, 'bold'), bg='white').pack(pady=20)
        hf = Frame(w, bg='white'); hf.pack(pady=10)
        hv = StringVar(value=cur_hold)
        Entry(hf, textvariable=hv, font=('Segoe UI', 10), width=40).pack(side=LEFT, padx=5)
        Button(hf, text="Browse", command=lambda: hv.set(filedialog.askdirectory()), bg=COLORS['primary'], fg='white').pack(side=LEFT)
        def save():
            self.db.update_settings(self.current_user['id'], int(rv.get()), hv.get() or os.path.join(os.path.expanduser("~"), ".duplicate_photo_cleaner", "holding"))
            messagebox.showinfo("Saved", "Settings saved!"); w.destroy()
        Button(w, text="Save", command=save, bg=COLORS['secondary'], fg='white', font=('Segoe UI', 11, 'bold')).pack(pady=30)

    def show_history(self):
        w = Toplevel(self.root); w.title("History"); w.geometry("700x500"); w.configure(bg='white')
        Label(w, text="Recent Actions", font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=20)
        f = Frame(w, bg='white'); f.pack(fill=BOTH, expand=True, padx=20, pady=10)
        cols = ('Action', 'File', 'Time')
        tree = ttk.Treeview(f, columns=cols, show='headings', height=20)
        for c in cols: tree.heading(c, text=c); tree.column(c, width=200)
        sb = ttk.Scrollbar(f, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=sb.set); tree.pack(side=LEFT, fill=BOTH, expand=True); sb.pack(side=RIGHT, fill=Y)
        for a, fp, t in self.db.get_history(self.current_user['id']): tree.insert('', END, values=(a, fp, t))

    def clean_history(self):
        s = self.db.get_settings(self.current_user['id'])
        self.db.clean_old_history(self.current_user['id'], s[0] if s else 6)
        messagebox.showinfo("Done", "Old history cleaned!")
''')

    # 7. .gitignore
    create_file(".gitignore", """# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
*.spec
*.db

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/

# App data
.duplicate_photo_cleaner/
""")

    # 8. README.md
    readme_content = "# Duplicate Photo Cleaner\n\nA local desktop application to find and remove duplicate photos safely.\n\n## Features\n- Scan any folder for duplicate images\n- Side-by-side comparison\n- Holding folder safety net\n- Multi-user support\n- Action history\n\n## Quick Start\n1. `pip install -r requirements.txt`\n2. `python3 main.py`\n"
    create_file("README.md", readme_content)

    print("\n" + "=" * 60)
    print("  ✅ PROJECT SETUP COMPLETE!")
    print("=" * 60)
    print("\n  NEXT STEPS:")
    print("  1. pip3 install -r requirements.txt")
    print("  2. python3 main.py")

if __name__ == "__main__":
    main()
