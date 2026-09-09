"""
Advanced Batch Processing System
"""
import os
import threading
import time
from queue import Queue
from datetime import datetime
import json

class BatchProcessor:
    def __init__(self, callback=None):
        self.callback = callback
        self.job_queue = Queue()
        self.is_processing = False
        self.current_job = None
        self.processed_jobs = []
        self.batch_settings = {
            'auto_delete': False,
            'similarity_threshold': 85,
            'preserve_folders': True,
            'backup_before_delete': True,
            'max_concurrent': 3
        }
    
    def add_batch_job(self, folder_paths, job_name=None):
        """Add multiple folders to batch processing queue"""
        job_id = f"batch_{int(time.time())}"
        job = {
            'id': job_id,
            'name': job_name or f"Batch Job {len(self.processed_jobs) + 1}",
            'folders': folder_paths,
            'created': datetime.now(),
            'status': 'queued',
            'progress': 0,
            'results': {
                'total_files': 0,
                'duplicates_found': 0,
                'space_saved': 0,
                'errors': []
            }
        }
        
        self.job_queue.put(job)
        if self.callback:
            self.callback('job_added', job)
        
        return job_id
    
    def start_batch_processing(self):
        """Start processing the batch queue"""
        if self.is_processing:
            return False
        
        self.is_processing = True
        thread = threading.Thread(target=self._process_batch_worker, daemon=True)
        thread.start()
        return True
    
    def _process_batch_worker(self):
        """Background worker for batch processing"""
        while not self.job_queue.empty() and self.is_processing:
            job = self.job_queue.get()
            self.current_job = job
            
            if self.callback:
                self.callback('job_started', job)
            
            try:
                self._process_single_job(job)
                job['status'] = 'completed'
            except Exception as e:
                job['status'] = 'failed'
                job['results']['errors'].append(str(e))
            
            job['completed'] = datetime.now()
            self.processed_jobs.append(job)
            
            if self.callback:
                self.callback('job_completed', job)
        
        self.is_processing = False
        self.current_job = None
        
        if self.callback:
            self.callback('batch_completed', self.get_batch_summary())
    
    def _process_single_job(self, job):
        """Process a single batch job"""
        total_duplicates = []
        total_files = 0
        
        for i, folder_path in enumerate(job['folders']):
            if not self.is_processing:  # Check if cancelled
                break
            
            # Update job progress
            job['progress'] = (i / len(job['folders'])) * 100
            job['current_folder'] = folder_path
            
            if self.callback:
                self.callback('job_progress', job)
            
            # Process this folder
            folder_results = self._scan_folder_for_duplicates(folder_path)
            total_duplicates.extend(folder_results['duplicates'])
            total_files += folder_results['files_scanned']
            
            # Auto-delete if enabled
            if self.batch_settings['auto_delete']:
                self._auto_delete_duplicates(folder_results['duplicates'])
        
        # Update job results
        job['results']['total_files'] = total_files
        job['results']['duplicates_found'] = len(total_duplicates)
        job['results']['space_saved'] = self._calculate_space_saved(total_duplicates)
        job['progress'] = 100
    
    def _scan_folder_for_duplicates(self, folder_path):
        """Scan a single folder for duplicates"""
        # Implement duplicate detection logic here
        # This is a simplified version
        duplicates = []
        files_scanned = 0
        
        photo_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if os.path.splitext(file)[1].lower() in photo_extensions:
                    files_scanned += 1
                    # Simplified duplicate detection by file size
                    # In real implementation, use perceptual hashing
        
        return {
            'duplicates': duplicates,
            'files_scanned': files_scanned
        }
    
    def _auto_delete_duplicates(self, duplicates):
        """Automatically delete duplicates with safety checks"""
        if not self.batch_settings['auto_delete']:
            return
        
        for dup_info in duplicates:
            try:
                # Safety: Create backup if enabled
                if self.batch_settings['backup_before_delete']:
                    self._backup_file(dup_info['duplicate'])
                
                # Move to trash instead of permanent delete
                self._move_to_trash(dup_info['duplicate'])
                
            except Exception as e:
                if self.current_job:
                    self.current_job['results']['errors'].append(f"Delete error: {e}")
    
    def _backup_file(self, file_path):
        """Create backup before deletion"""
        backup_dir = os.path.join(os.path.expanduser("~"), ".duplicate_cleaner_backup")
        os.makedirs(backup_dir, exist_ok=True)
        # Implementation would copy file to backup directory
    
    def _move_to_trash(self, file_path):
        """Move file to system trash"""
        # Implementation would use platform-specific trash functionality
        pass
    
    def _calculate_space_saved(self, duplicates):
        """Calculate total space that would be saved"""
        total_bytes = 0
        for dup in duplicates:
            try:
                if os.path.exists(dup['duplicate']):
                    total_bytes += os.path.getsize(dup['duplicate'])
            except:
                pass
        return total_bytes
    
    def stop_batch_processing(self):
        """Stop batch processing"""
        self.is_processing = False
    
    def get_batch_summary(self):
        """Get summary of all processed jobs"""
        return {
            'total_jobs': len(self.processed_jobs),
            'successful_jobs': len([j for j in self.processed_jobs if j['status'] == 'completed']),
            'failed_jobs': len([j for j in self.processed_jobs if j['status'] == 'failed']),
            'total_duplicates': sum(j['results']['duplicates_found'] for j in self.processed_jobs),
            'total_space_saved': sum(j['results']['space_saved'] for j in self.processed_jobs)
        }
    
    def export_batch_report(self, file_path):
        """Export detailed batch report"""
        report = {
            'generated': datetime.now().isoformat(),
            'summary': self.get_batch_summary(),
            'jobs': self.processed_jobs,
            'settings': self.batch_settings
        }
        
        with open(file_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
