import os
import zipfile
import tempfile
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

class BackupManager:
    def __init__(self, osu_path, backup_path, progress_var, progress_label, root):
        self.osu_path = osu_path
        self.backup_path = backup_path
        self.progress_var = progress_var
        self.progress_label = progress_label
        self.root = root
    
    def create_backup(self, selected_items):
        if not self.backup_path:
            return False, "No backup path specified"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_zip_name = f"osu_backup_{timestamp}.zip"
        final_zip_path = os.path.join(self.backup_path, final_zip_name)
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                individual_zips = []
                total_items = len(selected_items)
                
                self._update_progress(0, "Đang chuẩn bị sao lưu...")
                
                for i, item in enumerate(selected_items):
                    item_path = os.path.join(self.osu_path, item if item != "scores" else "data/r")
                    if os.path.exists(item_path):
                        item_zip_path = os.path.join(temp_dir, f"{item}.zip")
                        
                        self._update_progress((i + 1) / total_items * 90, f"Đang nén {item}...")
                        
                        with zipfile.ZipFile(item_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                            for root, dirs, files in os.walk(item_path):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    arcname = os.path.relpath(file_path, self.osu_path)
                                    zipf.write(file_path, arcname)
                        
                        individual_zips.append(item_zip_path)
                
                self._update_progress(90, "Đang tạo tệp sao lưu cuối cùng...")
                
                with zipfile.ZipFile(final_zip_path, 'w', zipfile.ZIP_DEFLATED) as final_zip:
                    for zip_file in individual_zips:
                        final_zip.write(zip_file, os.path.basename(zip_file))
                
                self._update_progress(100, f"Sao lưu hoàn tất: {final_zip_name}")
                
                return True, final_zip_path
        except Exception as e:
            return False, str(e)
    
    def _update_progress(self, value, text):
        self.progress_var.set(value)
        self.progress_label.config(text=text)
        self.root.update()