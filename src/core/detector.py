import os, datetime, shutil
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
