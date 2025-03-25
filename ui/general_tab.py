import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class GeneralTab(ttk.Frame):
    def __init__(self, master, db_manager, app, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.db_manager = db_manager
        self.app = app  # Lưu reference đến app
        self.create_widgets()
    
    def create_widgets(self):
        path_frame = ttk.LabelFrame(self, text="Cấu hình đường dẫn Osu!")
        path_frame.pack(fill='x', expand=True, padx=10, pady=10)
        
        ttk.Label(path_frame, text="Đường dẫn đến thư mục Osu!:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        path_entry_frame = ttk.Frame(path_frame)
        path_entry_frame.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        path_frame.columnconfigure(1, weight=1)
        
        self.osu_path_var = tk.StringVar()
        self.osu_path_entry = ttk.Entry(path_entry_frame, textvariable=self.osu_path_var)
        self.osu_path_entry.pack(side=tk.LEFT, fill='x', expand=True)
        
        browse_btn = ttk.Button(path_entry_frame, text="Duyệt", command=self.browse_osu_folder)
        browse_btn.pack(side=tk.RIGHT, padx=5)
        
        save_btn = ttk.Button(path_frame, text="Lưu cấu hình", command=self.save_config)
        save_btn.grid(row=1, column=0, columnspan=2, pady=10)
        
        help_frame = ttk.LabelFrame(self, text="Hướng dẫn")
        help_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        help_text = tk.Text(help_frame, wrap=tk.WORD, height=10, bg='#36393F', fg="white", relief=tk.FLAT)
        help_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        help_content = """Cách tìm thư mục Osu!:
1. Mở osu!
2. Vào cài đặt
3. Tìm tùy chọn "Open osu! folder"
4. Nhấn vào để mở thư mục
5. Sao chép đường dẫn từ trình quản lý tệp
6. Dán vào ô trên

(Folder game osu! trên windows thường có dạng C:/Users/[tên]/AppData/Local/osu!)

Lưu ý: Thư mục osu! thường chứa các thư mục con như 'Songs', 'Skins', 'Replays', v.v."""
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
    
    def browse_osu_folder(self):
        folder_path = filedialog.askdirectory(title="Chọn thư mục Osu!")
        if folder_path:
            self.osu_path_var.set(folder_path)
    
    def save_config(self):
        osu_path = self.osu_path_var.get()
        
        if not osu_path:
            messagebox.showerror("Lỗi", "Vui lòng chỉ định đường dẫn thư mục Osu!")
            return
        
        if not os.path.exists(osu_path):
            messagebox.showerror("Lỗi", "Thư mục được chỉ định không tồn tại!")
            return
        
        required_folders = ['Songs', 'Skins']
        missing_folders = [folder for folder in required_folders if not os.path.exists(os.path.join(osu_path, folder))]
        
        if missing_folders:
            result = messagebox.askyesno("Cảnh báo", 
                f"Các thư mục sau đang bị thiếu: {', '.join(missing_folders)}.\n"
                "Có thể đây không phải là một thư mục Osu! hợp lệ.\n"
                "Bạn có muốn sử dụng nó không?")
            
            if not result:
                return
        
        self.db_manager.save_config(osu_path, "")
        self.app.osu_path_var.set(osu_path)
        messagebox.showinfo("Thành công", "Cấu hình đã được lưu thành công!")
        
        self.app.notify_config_saved()
    
    def load_config(self, osu_path):
        self.osu_path_var.set(osu_path)
        