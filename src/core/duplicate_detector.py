"""
Core duplicate detection functionality
"""
import os
import hashlib
import shutil
import datetime
from pathlib import Path
from PIL import Image

class DuplicateDetector:
    def __init__(self, db_manager, user_id):
        self.db = db_manager
        self.user_id = user_id
        self.is_scanning = False
        self.supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

    def get_image_hash(self, file_path):
        """Generate perceptual hash for image comparison"""
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize to 8x8 and convert to grayscale
                img = img.resize((8, 8), Image.Resampling.LANCZOS).convert('L')
                
                # Get pixel values
                pixels = list(img.getdata())
                
                # Calculate average
                avg = sum(pixels) / len(pixels)
                
                # Create hash based on whether each pixel is above or below average
                hash_bits = ['1' if pixel > avg else '0' for pixel in pixels]
                return ''.join(hash_bits)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None

    def find_duplicates(self, folder_path, progress_callback=None):
        """Find duplicate images in the specified folder"""
        image_files = []
        
        # Collect all image files
        for root, _, files in os.walk(folder_path):
            for file in files:
                if Path(file).suffix.lower() in self.supported_extensions:
                    image_files.append(os.path.join(root, file))
        
        hash_map = {}
        duplicates = []
        self.is_scanning = True
        
        for i, file_path in enumerate(image_files):
            if not self.is_scanning:
                break
                
            if progress_callback:
                progress_callback(i + 1, len(image_files), file_path)
            
            file_hash = self.get_image_hash(file_path)
            if file_hash:
                if file_hash in hash_map:
                    duplicates.append({
                        'original': hash_map[file_hash],
                        'duplicate': file_path,
                        'hash': file_hash
                    })
                else:
                    hash_map[file_hash] = file_path
        
        self.is_scanning = False
        return duplicates

    def move_to_holding(self, file_path, holding_folder):
        """Move file to holding folder with timestamp"""
        Path(holding_folder).mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Path(file_path).name
        dest_path = Path(holding_folder) / f"{timestamp}_{filename}"
        
        # Ensure unique filename
        counter = 1
        while dest_path.exists():
            name_parts = filename.rsplit('.', 1)
            if len(name_parts) == 2:
                new_name = f"{timestamp}_{name_parts[0]}_{counter}.{name_parts[1]}"
            else:
                new_name = f"{timestamp}_{filename}_{counter}"
            dest_path = Path(holding_folder) / new_name
            counter += 1
        
        shutil.move(file_path, dest_path)
        
        # Log the action
        file_hash = self.get_image_hash(str(dest_path))
        self.db.log_action(self.user_id, "moved_to_holding", file_path, file_hash)
        
        return str(dest_path)

    def permanently_delete(self, holding_folder):
        """Permanently delete all files in holding folder"""
        if not os.path.exists(holding_folder):
            return []
        
        deleted_files = []
        for filename in os.listdir(holding_folder):
            file_path = os.path.join(holding_folder, filename)
            try:
                os.remove(file_path)
                deleted_files.append(file_path)
                self.db.log_action(self.user_id, "permanently_deleted", file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
        
        return deleted_files

    def stop_scanning(self):
        """Stop the current scanning operation"""
        self.is_scanning = False
