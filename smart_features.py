"""
Smart AI-powered features for better duplicate management
"""
import os
from PIL import Image
from datetime import datetime

class SmartRecommendations:
    @staticmethod
    def recommend_which_to_keep(original_path, duplicate_path):
        """AI logic to recommend which file to keep"""
        score_original = 0
        score_duplicate = 0
        reasons = []
        
        try:
            # File size comparison (larger usually better quality)
            orig_size = os.path.getsize(original_path)
            dup_size = os.path.getsize(duplicate_path)
            
            if orig_size > dup_size:
                score_original += 2
                reasons.append(f"Original is {orig_size - dup_size} bytes larger")
            elif dup_size > orig_size:
                score_duplicate += 2
                reasons.append(f"Duplicate is {dup_size - orig_size} bytes larger")
            
            # Image dimensions (higher resolution better)
            with Image.open(original_path) as orig_img:
                orig_pixels = orig_img.width * orig_img.height
            with Image.open(duplicate_path) as dup_img:
                dup_pixels = dup_img.width * dup_img.height
            
            if orig_pixels > dup_pixels:
                score_original += 3
                reasons.append("Original has higher resolution")
            elif dup_pixels > orig_pixels:
                score_duplicate += 3
                reasons.append("Duplicate has higher resolution")
            
            # File name analysis (avoid thumbnails, temp files)
            orig_name = os.path.basename(original_path).lower()
            dup_name = os.path.basename(duplicate_path).lower()
            
            bad_indicators = ['thumb', 'temp', 'copy', 'resize', 'small']
            for indicator in bad_indicators:
                if indicator in orig_name:
                    score_duplicate += 1
                if indicator in dup_name:
                    score_original += 1
            
            # Folder location (avoid temp/cache folders)
            if 'cache' in original_path.lower() or 'temp' in original_path.lower():
                score_duplicate += 2
            if 'cache' in duplicate_path.lower() or 'temp' in duplicate_path.lower():
                score_original += 2
            
        except Exception as e:
            reasons.append(f"Analysis error: {str(e)}")
        
        if score_original > score_duplicate:
            return 'original', reasons
        elif score_duplicate > score_original:
            return 'duplicate', reasons
        else:
            return 'equal', reasons

    @staticmethod
    def get_image_quality_score(image_path):
        """Calculate image quality score"""
        try:
            with Image.open(image_path) as img:
                # Higher resolution = higher score
                resolution_score = (img.width * img.height) / 1000000  # Megapixels
                
                # File size per pixel (compression quality indicator)
                file_size = os.path.getsize(image_path)
                size_per_pixel = file_size / (img.width * img.height)
                
                # Combined score
                quality_score = resolution_score + (size_per_pixel / 10)
                return min(quality_score, 10)  # Cap at 10
        except:
            return 0
