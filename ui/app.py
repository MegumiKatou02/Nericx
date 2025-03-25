import tkinter as tk
from tkinter import ttk
from models.database import DatabaseManager
from ui.general_tab import GeneralTab
from ui.backup_tab import BackupTab
from ui.music_tab import MusicTab
from themes.nericx_theme import NericxStyle

class OsuManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nericx")
        self.setup_window()
        
        self.db_manager = DatabaseManager()
        self.osu_path_var = tk.StringVar()
        self.create_ui()
        self.load_saved_config()
    
    def setup_window(self):
        win_width = 800
        win_height = 650

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width // 2) - (win_width // 2)
        y = (screen_height // 2) - (win_height // 2) - 50

        self.root.geometry(f"{win_width}x{win_height}+{x}+{y}")
        self.root.minsize(800, 650)

        NericxStyle.apply_theme(self.root)
    
    def create_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tab_general = GeneralTab(self.notebook, self.db_manager, self)
        self.tab_backup = BackupTab(self.notebook, self.db_manager, self)
        self.tab_music = MusicTab(self.notebook, self.db_manager, self)
        
        self.notebook.add(self.tab_general, text="Chung")
        self.notebook.add(self.tab_backup, text="Sao lưu")
        self.notebook.add(self.tab_music, text="Nhạc")
    
    def load_saved_config(self):
        config = self.db_manager.load_config()
        if config:
            osu_path, backup_path = config
            self.osu_path_var.set(osu_path)
            self.tab_general.osu_path_var.set(osu_path)
            if backup_path:
                self.tab_backup.backup_path_var.set(backup_path)
            
            self.tab_backup.update_state()
            self.tab_music.update_state()
    
    def get_osu_path(self):
        return self.osu_path_var.get()
    
    def notify_config_saved(self):
        self.tab_backup.notify_config_saved()
        self.tab_music.notify_config_saved()
    
    def on_closing(self):
        if hasattr(self.tab_music, 'music_player'):
            self.tab_music.music_player.stop_music()
        
        self.db_manager.close()
        self.root.destroy()