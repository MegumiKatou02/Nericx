import tkinter as tk
from tkinter import ttk
from utils.music_player import MusicPlayer
from datetime import datetime

class MusicTab(ttk.Frame):
    def __init__(self, master, db_manager, app, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.db_manager = db_manager
        self.app = app
        self.music_player = MusicPlayer()
        self.discord_available = False
        self.setup_discord()
        self.create_widgets()
        self.update_state()
    
    def setup_discord(self):
        try:
            import discordsdk
            from config.config import DISCORD_CLIENT_ID
            self.discord = discordsdk.Discord(DISCORD_CLIENT_ID, discordsdk.CreateFlags.default)
            self.activity_manager = self.discord.get_activity_manager()
            self.discord_available = True
        except Exception as e:
            print(f"Discord SDK không khả dụng: {e}")
    
    def create_widgets(self):
        self.warning_label = ttk.Label(self, text="Vui lòng cấu hình đường dẫn Osu! trong tab Chung trước", foreground='red')
        self.warning_label.pack(pady=10)
        
        self.main_frame = ttk.Frame(self)
        
        if not self.discord_available:
            discord_warning = ttk.Label(
                self.main_frame, 
                text="Discord SDK không khả dụng. Tích hợp Discord đã bị tắt.",
                foreground='orange'
            )
            discord_warning.pack(pady=5)
        
        songs_frame = ttk.LabelFrame(self.main_frame, text="Thư viện bài hát")
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
        
        self.songs_listbox = tk.Listbox(songs_list_frame, yscrollcommand=scrollbar.set, height=15, bg='#36393F', fg='white')
        self.songs_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.songs_listbox.yview)
        
        self.songs_listbox.bind("<Double-1>", self.play_selected_song)
        
        player_frame = ttk.LabelFrame(self.main_frame, text="Trình phát")
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
    
    def filter_songs(self, *args):
        search_term = self.search_var.get().lower()
        
        current_selection = self.songs_listbox.curselection()
        current_selection_name = self.songs_listbox.get(current_selection[0]) if current_selection else None
        
        self.songs_listbox.delete(0, tk.END)
        
        filtered_songs = []
        for song in self.music_player.songs_data:
            if search_term in song["name"].lower():
                self.songs_listbox.insert(tk.END, song["name"])
                filtered_songs.append(song)
        
        if current_selection_name:
            for i, song_name in enumerate(self.songs_listbox.get(0, tk.END)):
                if song_name == current_selection_name:
                    self.songs_listbox.selection_set(i)
                    self.songs_listbox.see(i)
                    break
    
    def play_selected_song(self, event=None):
        selection = self.songs_listbox.curselection()
        
        if not selection:
            return
        
        song_name = self.songs_listbox.get(selection[0])
        
        song = None
        for s in self.music_player.songs_data:
            if s["name"] == song_name:
                song = s
                break
        
        if song:
            success, result = self.music_player.play_music(song)
            
            if success:
                self.current_track_label.config(text=result)
                self.play_btn.config(text="Tạm dừng")
                
                for i in range(self.songs_listbox.size()):
                    self.songs_listbox.itemconfig(i, {'bg': '#36393F', 'fg': 'white'})
                
                self.songs_listbox.itemconfig(selection[0], {'bg': '#7289DA', 'fg': 'white'})
                self.songs_listbox.see(selection[0])
                
                if self.discord_available:
                    self.update_discord_status(song["name"])
            else:
                tk.messagebox.showerror("Lỗi", f"Không thể phát bài hát:\n{result}")
    
    def update_discord_status(self, song_name):
        try:
            import discordsdk
            activity = discordsdk.Activity()
            activity.state = "Đang nghe nhạc qua Nericx"
            activity.details = song_name
            activity.timestamps.start = int(datetime.now().timestamp())
            
            self.activity_manager.update_activity(activity, lambda result: print(f"Kết quả: {result}"))
            self.discord_status_label.config(text="Đang chia sẻ nhạc")
            
            def discord_callback():
                if self.discord_available and self.music_player.playing:
                    self.discord.run_callbacks()
                    self.after(1000, discord_callback)
            
            discord_callback()
        except Exception as e:
            print(f"Lỗi Discord RPC: {e}")
    
    def toggle_play(self):
        if not self.music_player.current_track:
            if self.songs_listbox.size() > 0:
                self.songs_listbox.selection_set(0)
                self.play_selected_song()
            return
        
        success, result = self.music_player.toggle_play()
        
        if success:
            if result == "Paused":
                self.play_btn.config(text="Phát")
            else:
                self.play_btn.config(text="Tạm dừng")
    
    def stop_music(self):
        for i in range(self.songs_listbox.size()):
            self.songs_listbox.itemconfig(i, {'bg': '#36393F', 'fg': 'white'})
        
        success, result = self.music_player.stop_music()
        
        if success:
            self.play_btn.config(text="Phát")
            self.current_track_label.config(text="Không có bài nào")
            
            if self.discord_available:
                try:
                    self.activity_manager.clear_activity(lambda result: print(f"Kết quả xóa hoạt động: {result}"))
                    self.discord_status_label.config(text="Không hoạt động")
                except Exception as e:
                    print(f"Lỗi Discord RPC: {e}")
    
    def update_state(self):
        osu_path = self.app.get_osu_path()
        
        if osu_path:
            self.warning_label.pack_forget()
            self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            success, result = self.music_player.load_songs(osu_path)
            
            if success:
                self.songs_listbox.delete(0, tk.END)
                for song in self.music_player.get_song_list():
                    self.songs_listbox.insert(tk.END, song)
            else:
                tk.messagebox.showwarning("Cảnh báo", result)
        else:
            self.main_frame.pack_forget()
            self.warning_label.pack(pady=10)
    
    def notify_config_saved(self):
        self.update_state()