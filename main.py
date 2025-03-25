import os
import sqlite3
import zipfile
import tempfile
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, PhotoImage
import pygame
import config

class NericxTheme:
    PRIMARY = "#7289DA"  # Discord Blue
    SECONDARY = "#424549"  # Discord Dark
    ACCENT = "#5b6dae"  # Dark Blue
    BACKGROUND = "#36393F"  # Discord Dark Background
    LIGHT_BACKGROUND = "#40444B"  # Discord Channel Background
    TEXT_LIGHT = "#FFFFFF"  # White
    TEXT_DARK = "#99AAB5"  # Discord Grey Text
    SUCCESS = "#43B581"  # Discord Green
    ERROR = "#F04747"  # Discord Red
    WARNING = "#FAA61A"  # Discord Orange

class NericxStyle:
    @staticmethod
    def apply_theme(root):
        style = ttk.Style()
        style.theme_use('clam') 
        
        style.configure('TFrame', background=NericxTheme.BACKGROUND)
        style.configure('TLabel', background=NericxTheme.BACKGROUND, foreground=NericxTheme.TEXT_LIGHT)
        style.configure('TLabelframe', background=NericxTheme.BACKGROUND, foreground=NericxTheme.TEXT_LIGHT)
        style.configure('TLabelframe.Label', background=NericxTheme.BACKGROUND, foreground=NericxTheme.TEXT_LIGHT)
        
        style.configure('TNotebook', background=NericxTheme.BACKGROUND, borderwidth=0)
        style.configure('TNotebook.Tab', background=NericxTheme.SECONDARY, foreground=NericxTheme.TEXT_LIGHT,
                        padding=[10, 5], font=('Segoe UI', 9, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', NericxTheme.PRIMARY)],
                  foreground=[('selected', NericxTheme.TEXT_LIGHT)])
        
        style.configure('TButton', background=NericxTheme.PRIMARY, foreground=NericxTheme.TEXT_LIGHT,
                      font=('Segoe UI', 9, 'bold'), borderwidth=0, padding=5)
        style.map('TButton', background=[('active', NericxTheme.ACCENT)],
                foreground=[('active', NericxTheme.TEXT_LIGHT)])
        
        style.configure('Faded.TButton', background=NericxTheme.SECONDARY, foreground=NericxTheme.TEXT_DARK)
        style.map('Faded.TButton', background=[('active', NericxTheme.SECONDARY)],
                foreground=[('active', NericxTheme.TEXT_LIGHT)])
        
        style.configure('Success.TButton', background=NericxTheme.SUCCESS, foreground=NericxTheme.TEXT_LIGHT)
        style.map('Success.TButton', background=[('active', NericxTheme.SUCCESS)],
                foreground=[('active', NericxTheme.TEXT_LIGHT)])
        
        style.configure('TEntry', foreground=NericxTheme.TEXT_LIGHT, fieldbackground=NericxTheme.LIGHT_BACKGROUND,
                      borderwidth=0, padding=5)
        
        style.configure('TCheckbutton', background=NericxTheme.BACKGROUND, foreground=NericxTheme.TEXT_LIGHT)
        style.map('TCheckbutton', background=[('active', NericxTheme.BACKGROUND)])
        
        style.configure('TProgressbar', background=NericxTheme.ACCENT, troughcolor=NericxTheme.LIGHT_BACKGROUND, 
                      borderwidth=0, thickness=10)
        
        style.configure('TScrollbar', background=NericxTheme.LIGHT_BACKGROUND, borderwidth=0, arrowsize=12)
        style.map('TScrollbar', background=[('active', NericxTheme.PRIMARY)])
        
        style.configure("TNotebook.Tab", font=("Segoe UI", 10)) 
        style.configure("TCheckbutton", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10))

        root.configure(background=NericxTheme.BACKGROUND)
        root.option_add("*Font", ("Segoe UI", 10))

class OsuManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nericx")

        # icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")  # Đường dẫn đến file icon
        # if os.path.exists(icon_path):
        #     self.root.iconbitmap(icon_path)
        # else:
        #     print("Không tìm thấy file icon: icon.ico")

        win_width = 800
        win_height = 650

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        x = (screen_width // 2) - (win_width // 2)
        y = (screen_height // 2) - (win_height // 2) - 50

        self.root.geometry(f"{win_width}x{win_height}+{x}+{y}")
        self.root.minsize(800, 650)

        NericxStyle.apply_theme(self.root)
        
        self.init_database()
        pygame.mixer.init()
        self.current_track = None
        self.playing = False
        
        self.discord_available = False
        try:
            import discordsdk
            self.discord = discordsdk.Discord(config.DISCORD_CLIENT_ID, discordsdk.CreateFlags.default)
            self.activity_manager = self.discord.get_activity_manager()
            self.discord_available = True
        except Exception as e:
            print(f"Discord SDK không khả dụng: {e}")
        
        self.create_ui()
        self.load_saved_config()
    
    def init_database(self):
        self.conn = sqlite3.connect('osu_manager.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY,
            osu_path TEXT,
            last_backup_path TEXT
        )
        ''')
        self.conn.commit()
    
    def create_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tab_general = ttk.Frame(self.notebook)
        self.tab_backup = ttk.Frame(self.notebook)
        self.tab_music = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_general, text="Chung")
        self.notebook.add(self.tab_backup, text="Sao lưu")
        self.notebook.add(self.tab_music, text="Nhạc")
        
        self.setup_general_tab()
        self.setup_backup_tab()
        self.setup_music_tab()
    
    def setup_general_tab(self):
        path_frame = ttk.LabelFrame(self.tab_general, text="Cấu hình đường dẫn Osu!")
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
        
        help_frame = ttk.LabelFrame(self.tab_general, text="Hướng dẫn")
        help_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        help_text = tk.Text(help_frame, wrap=tk.WORD, height=10, bg=NericxTheme.BACKGROUND, fg="white", relief=tk.FLAT)
        help_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        help_content = """Cách tìm thư mục Osu!:
1. Mở Osu!
2. Vào cài đặt
3. Tìm tùy chọn "Open osu! folder"
4. Nhấn vào để mở thư mục
5. Sao chép đường dẫn từ trình quản lý tệp
6. Dán vào ô trên

Lưu ý: Thư mục Osu! thường chứa các thư mục con như 'Songs', 'Skins', 'Replays', v.v."""
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
    
    def setup_backup_tab(self):
        warning_label = ttk.Label(self.tab_backup, text="Vui lòng cấu hình đường dẫn Osu! trong tab Chung trước", foreground='red')
        warning_label.pack(pady=10)
        self.backup_warning_label = warning_label
        
        self.backup_main_frame = ttk.Frame(self.tab_backup)
        self.backup_main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        backup_options_frame = ttk.LabelFrame(self.backup_main_frame, text="Các mục cần sao lưu")
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
        
        output_frame = ttk.Frame(self.backup_main_frame)
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
        
        backup_btn = ttk.Button(self.backup_main_frame, text="Tạo sao lưu", command=self.create_backup)
        backup_btn.pack(pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.backup_main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill='x', padx=10, pady=10)
        
        self.progress_label = ttk.Label(self.backup_main_frame, text="")
        self.progress_label.pack(pady=5)
        
        self.update_backup_tab_state()
    
    def setup_music_tab(self):
        warning_label = ttk.Label(self.tab_music, text="Vui lòng cấu hình đường dẫn Osu! trong tab Chung trước", foreground='red')
        warning_label.pack(pady=10)
        self.music_warning_label = warning_label
        
        self.music_main_frame = ttk.Frame(self.tab_music)
        self.music_main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        if not self.discord_available:
            discord_warning = ttk.Label(
                self.music_main_frame, 
                text="Discord SDK không khả dụng. Tích hợp Discord đã bị tắt.",
                foreground='orange'
            )
            discord_warning.pack(pady=5)
        
        songs_frame = ttk.LabelFrame(self.music_main_frame, text="Thư viện bài hát")
        songs_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        search_frame = ttk.Frame(songs_frame)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text="Tìm kiếm:").pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_songs)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill='x', expand=True, padx=5)
        
        songs_list_frame = ttk.Frame(songs_frame)
        songs_list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(songs_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        self.songs_listbox = tk.Listbox(songs_list_frame, yscrollcommand=scrollbar.set, height=15, background=NericxTheme.BACKGROUND, foreground=NericxTheme.TEXT_LIGHT)
        self.songs_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.songs_listbox.yview)
        
        self.songs_listbox.bind("<Double-1>", self.play_selected_song)
        
        player_frame = ttk.LabelFrame(self.music_main_frame, text="Trình phát")
        player_frame.pack(fill='x', padx=10, pady=10)
        
        controls_frame = ttk.Frame(player_frame)
        controls_frame.pack(padx=10, pady=10)
        
        self.play_btn = ttk.Button(controls_frame, text="Phát", command=self.toggle_play)
        self.play_btn.grid(row=0, column=0, padx=5)
        
        ttk.Button(controls_frame, text="Dừng", command=self.stop_music).grid(row=0, column=1, padx=5)
        
        info_frame = ttk.Frame(player_frame)
        info_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(info_frame, text="Bài hát hiện tại:").grid(row=0, column=0, sticky='w')
        self.current_track_label = ttk.Label(info_frame, text="Không có")
        self.current_track_label.grid(row=0, column=1, sticky='w', padx=5)
        
        if self.discord_available:
            discord_frame = ttk.Frame(player_frame)
            discord_frame.pack(fill='x', padx=10, pady=10)
            
            ttk.Label(discord_frame, text="Trạng thái Discord:").grid(row=0, column=0, sticky='w')
            self.discord_status_label = ttk.Label(discord_frame, text="Đã kết nối")
            self.discord_status_label.grid(row=0, column=1, sticky='w', padx=5)
        
        self.update_music_tab_state()
    
    def browse_osu_folder(self):
        folder_path = filedialog.askdirectory(title="Chọn thư mục Osu!")
        if folder_path:
            self.osu_path_var.set(folder_path)

    def browse_backup_folder(self):
        folder_path = filedialog.askdirectory(title="Chọn thư mục sao lưu")
        if folder_path:
            self.backup_path_var.set(folder_path)

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
        
        self.cursor.execute("DELETE FROM config")
        self.cursor.execute("INSERT INTO config (osu_path, last_backup_path) VALUES (?, ?)", 
                        (osu_path, self.backup_path_var.get() or ""))
        self.conn.commit()
        
        messagebox.showinfo("Thành công", "Cấu hình đã được lưu thành công!")

        self.update_backup_tab_state()
        self.update_music_tab_state()
        
        if self.notebook.index(self.notebook.select()) == 2:
            self.load_songs()

    
    def load_saved_config(self):
        self.cursor.execute("SELECT osu_path, last_backup_path FROM config LIMIT 1")
        result = self.cursor.fetchone()
        
        if result:
            osu_path, backup_path = result
            self.osu_path_var.set(osu_path)
            self.backup_path_var.set(backup_path or "")
            
            self.update_backup_tab_state()
            self.update_music_tab_state()
    
    def update_backup_tab_state(self):
        osu_path = self.osu_path_var.get()
        
        if osu_path and os.path.exists(osu_path):
            self.backup_warning_label.pack_forget()
            self.backup_main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        else:
            self.backup_main_frame.pack_forget()
            self.backup_warning_label.pack(pady=10)
    
    def update_music_tab_state(self):
        osu_path = self.osu_path_var.get()
        
        if osu_path and os.path.exists(osu_path):
            self.music_warning_label.pack_forget()
            self.music_main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            self.load_songs()
        else:
            self.music_main_frame.pack_forget()
            self.music_warning_label.pack(pady=10)
    
    def create_backup(self):
        osu_path = self.osu_path_var.get()
        backup_path = self.backup_path_var.get()
        
        if not backup_path:
            backup_path = filedialog.askdirectory(title="Chọn thư mục sao lưu")
            if not backup_path:
                return
            self.backup_path_var.set(backup_path)
            
            self.cursor.execute("UPDATE config SET last_backup_path = ?", (backup_path,))
            self.conn.commit()
        
        selected_items = [key for key, var in self.backup_vars.items() if var.get()]
        
        if not selected_items:
            messagebox.showerror("Lỗi", "Vui lòng chọn ít nhất một mục để sao lưu!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_zip_name = f"osu_backup_{timestamp}.zip"
        final_zip_path = os.path.join(backup_path, final_zip_name)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            individual_zips = []
            total_items = len(selected_items)
            
            self.progress_var.set(0)
            self.progress_label.config(text="Đang chuẩn bị sao lưu...")
            self.root.update()
            
            for i, item in enumerate(selected_items):
                item_path = os.path.join(osu_path, item if item != "scores" else "data/r")
                if os.path.exists(item_path):
                    item_zip_path = os.path.join(temp_dir, f"{item}.zip")
                    
                    self.progress_label.config(text=f"Đang nén {item}...")
                    self.root.update()
                    
                    with zipfile.ZipFile(item_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for root, dirs, files in os.walk(item_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, osu_path)
                                zipf.write(file_path, arcname)
                    
                    individual_zips.append(item_zip_path)
                
                self.progress_var.set((i + 1) / total_items * 90) 
                self.root.update()
            
            self.progress_label.config(text="Đang tạo tệp sao lưu cuối cùng...")
            self.root.update()
            
            with zipfile.ZipFile(final_zip_path, 'w', zipfile.ZIP_DEFLATED) as final_zip:
                for zip_file in individual_zips:
                    final_zip.write(zip_file, os.path.basename(zip_file))
            
            self.progress_var.set(100)
            self.progress_label.config(text=f"Sao lưu hoàn tất: {final_zip_name}")
            self.root.update()
            
            messagebox.showinfo("Thành công", f"Sao lưu đã được tạo thành công: {final_zip_path}")

    
    def load_songs(self):
        osu_path = self.osu_path_var.get()
        songs_path = os.path.join(osu_path, "Songs")
        
        if not os.path.exists(songs_path):
            messagebox.showwarning("Cảnh báo", "Không tìm thấy thư mục Songs!")
            return
        
        self.songs_listbox.delete(0, tk.END)
        
        self.songs_data = []
        
        for song_folder in os.listdir(songs_path):
            folder_path = os.path.join(songs_path, song_folder)
            
            if os.path.isdir(folder_path):
                mp3_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp3')]
                
                if mp3_files:
                    for mp3 in mp3_files:
                        song_folder_cleaned = " ".join(song_folder.split(" ")[1:])
                        song_name = f"{song_folder_cleaned} - {os.path.splitext(mp3)[0]}"
                        song_path = os.path.join(folder_path, mp3)

                        self.songs_data.append({
                            "name": song_name,
                            "path": song_path
                        })
                        
                        self.songs_listbox.insert(tk.END, song_name)

        self.songs_listbox.configure(
            selectbackground=NericxTheme.PRIMARY,
            selectforeground=NericxTheme.TEXT_LIGHT
        )
    
    def filter_songs(self, *args):
        search_term = self.search_var.get().lower()
        
        self.songs_listbox.delete(0, tk.END)
        
        for song in self.songs_data:
            if search_term in song["name"].lower():
                self.songs_listbox.insert(tk.END, song["name"])
    
    def play_selected_song(self, event=None):
        selection = self.songs_listbox.curselection()
        
        if not selection:
            return
        
        displayed_name = self.songs_listbox.get(selection[0])
        
        selected_song = None
        for song in self.songs_data:
            if song["name"] == displayed_name:
                selected_song = song
                break
        
        if selected_song:
            self.play_music(selected_song)
    
    def play_music(self, song):
        for i in range(self.songs_listbox.size()):
            self.songs_listbox.itemconfig(i, {'bg': NericxTheme.BACKGROUND, 'fg': NericxTheme.TEXT_LIGHT})

        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        
        try:
            pygame.mixer.music.load(song["path"])
            pygame.mixer.music.play()
            
            self.current_track = song
            self.current_track_label.config(text=song["name"])
            self.play_btn.config(text="Tạm dừng")
            self.playing = True

            index = self.songs_data.index(song)
            self.songs_listbox.itemconfig(index, {'bg': NericxTheme.PRIMARY, 'fg': NericxTheme.TEXT_LIGHT})
            
            self.songs_listbox.see(index)
            
            if self.discord_available:
                try:
                    import discordsdk
                    activity = discordsdk.Activity()
                    activity.state = "Đang nghe nhạc qua Nericx"
                    activity.details = song["name"]
                    activity.timestamps.start = int(datetime.now().timestamp())
                    
                    self.activity_manager.update_activity(activity, lambda result: print(f"Kết quả: {result}"))
                    self.discord_status_label.config(text="Đang chia sẻ nhạc")
                    
                    def discord_callback():
                        if self.discord_available and self.playing:
                            self.discord.run_callbacks()
                            self.root.after(1000, discord_callback)
                    
                    discord_callback()
                except Exception as e:
                    print(f"Lỗi Discord RPC: {e}")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể phát bài hát:\n{str(e)}")

    
    def toggle_play(self):
        if not self.current_track:
            if self.songs_listbox.size() > 0:
                self.songs_listbox.selection_set(0)
                self.play_selected_song()
            return
        
        if self.playing:
            pygame.mixer.music.pause()
            self.play_btn.config(text="Phát")
            self.playing = False
        else:
            pygame.mixer.music.unpause()
            self.play_btn.config(text="Tạm dừng")
            self.playing = True

    
    def stop_music(self):
        for i in range(self.songs_listbox.size()):
            self.songs_listbox.itemconfig(i, {'bg': NericxTheme.BACKGROUND, 'fg': NericxTheme.TEXT_LIGHT})
        
        pygame.mixer.music.stop()
        self.play_btn.config(text="Phát")
        self.playing = False
        self.current_track_label.config(text="Không có bài nào")
        
        if self.discord_available:
            try:
                self.activity_manager.clear_activity(lambda result: print(f"Kết quả xóa hoạt động: {result}"))
                self.discord_status_label.config(text="Không hoạt động")
            except Exception as e:
                print(f"Lỗi Discord RPC: {e}")

    
    def on_closing(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        
        if hasattr(self, 'conn'):
            self.conn.close()
        
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = OsuManagerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    root.iconbitmap("icon.ico") 

    root.mainloop()