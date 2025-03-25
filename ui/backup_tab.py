import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from utils.backup_manager import BackupManager

class BackupTab(ttk.Frame):
    def __init__(self, master, db_manager, app, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.db_manager = db_manager
        self.app = app 
        self.create_widgets()
        self.update_state()
    
    def create_widgets(self):
        self.warning_label = ttk.Label(self, text="Vui lòng cấu hình đường dẫn Osu! trong tab Chung trước", foreground='red')
        self.warning_label.pack(pady=10)
        
        self.main_frame = ttk.Frame(self)
        
        backup_options_frame = ttk.LabelFrame(self.main_frame, text="Các mục cần sao lưu")
        backup_options_frame.pack(fill='x', padx=10, pady=10)
        
        self.backup_vars = {
            "skins": tk.BooleanVar(value=True),
            "songs": tk.BooleanVar(value=True),
            "screenshots": tk.BooleanVar(value=True),
            "replays": tk.BooleanVar(value=True),
            "scores": tk.BooleanVar(value=True)
        }
        
        row = 0
        for key, var in self.backup_vars.items():
            ttk.Checkbutton(backup_options_frame, text=key.capitalize(), variable=var).grid(
                row=row // 3, column=row % 3, sticky='w', padx=10, pady=5
            )
            row += 1
        
        output_frame = ttk.Frame(self.main_frame)
        output_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(output_frame, text="Thư mục sao lưu:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        output_entry_frame = ttk.Frame(output_frame)
        output_entry_frame.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        output_frame.columnconfigure(1, weight=1)
        
        self.backup_path_var = tk.StringVar()
        self.backup_path_entry = ttk.Entry(output_entry_frame, textvariable=self.backup_path_var)
        self.backup_path_entry.pack(side=tk.LEFT, fill='x', expand=True)
        
        browse_output_btn = ttk.Button(output_entry_frame, text="Duyệt", command=self.browse_backup_folder)
        browse_output_btn.pack(side=tk.RIGHT, padx=5)
        
        backup_btn = ttk.Button(self.main_frame, text="Tạo sao lưu", command=self.create_backup)
        backup_btn.pack(pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill='x', padx=10, pady=10)
        
        self.progress_label = ttk.Label(self.main_frame, text="")
        self.progress_label.pack(pady=5)
    
    def browse_backup_folder(self):
        folder_path = filedialog.askdirectory(title="Chọn thư mục sao lưu")
        if folder_path:
            self.backup_path_var.set(folder_path)
            self.db_manager.update_backup_path(folder_path)
    
    def create_backup(self):
        backup_path = self.backup_path_var.get()
        
        if not backup_path:
            backup_path = filedialog.askdirectory(title="Chọn thư mục sao lưu")
            if not backup_path:
                return
            self.backup_path_var.set(backup_path)
            self.db_manager.update_backup_path(backup_path)
        
        selected_items = [key for key, var in self.backup_vars.items() if var.get()]
        
        if not selected_items:
            messagebox.showerror("Lỗi", "Vui lòng chọn ít nhất một mục để sao lưu!")
            return
        
        osu_path = self.app.get_osu_path()
        if not osu_path:
            messagebox.showerror("Lỗi", "Vui lòng cấu hình đường dẫn Osu! trước")
            return
        
        backup_manager = BackupManager(
            osu_path, 
            backup_path, 
            self.progress_var, 
            self.progress_label, 
            self.master
        )
        
        success, result = backup_manager.create_backup(selected_items)
        
        if success:
            messagebox.showinfo("Thành công", f"Sao lưu đã được tạo thành công: {result}")
        else:
            messagebox.showerror("Lỗi", f"Không thể tạo sao lưu:\n{result}")
    
    def update_state(self):
        osu_path = self.app.get_osu_path()
        
        if osu_path:
            self.warning_label.pack_forget()
            self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            config = self.db_manager.load_config()
            if config and config[1]:
                self.backup_path_var.set(config[1])
        else:
            self.main_frame.pack_forget()
            self.warning_label.pack(pady=10)
    
    def notify_config_saved(self):
        self.update_state()