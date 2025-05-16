import tkinter as tk
from tkinter import ttk
from utils.music_player import MusicPlayer
import tkinter.messagebox as messagebox
from pypresence import Presence
import time
import pygame
import config.config
import re
import os
from PIL import Image, ImageTk

class MusicTab(ttk.Frame):
    def __init__(self, master, db_manager, app, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.db_manager = db_manager
        self.app = app

        self.shuffle_mode = False
        self.music_controls_visible = False

        self.music_player = MusicPlayer()
        self.discord_available = False
        self.rpc = None
  
        self.setup_discord_rpc()
        self.create_widgets()
        self.update_state()
        
        self.auto_next_cooldown = False
        self.after(2000, self.check_music_end)
        
        self.progress_update_id = None
        self.update_progress_timer()

    def check_music_end(self):
        try:
            if not self.auto_next_cooldown:
                if not pygame.mixer.music.get_busy() and self.music_player.playing:
                    success, next_track = self.music_player.play_next()
                    
                    if success and next_track:
                        self.auto_next_cooldown = True
                        self.after(2000, self.reset_auto_next_cooldown)
                        
                        try:
                            current_track_name = self.music_player.current_track["name"]
                            
                            for i in range(self.songs_listbox.size()):
                                self.songs_listbox.itemconfig(i, {'bg': '#36393F', 'fg': 'white'})
                            
                            for i in range(self.songs_listbox.size()):
                                if self.songs_listbox.get(i) == current_track_name:
                                    self.songs_listbox.selection_clear(0, tk.END)
                                    self.songs_listbox.selection_set(i)
                                    self.songs_listbox.see(i)
                                    self.songs_listbox.itemconfig(i, {'bg': '#7289DA', 'fg': 'white'})
                                    break
                            
                            self.current_track_label.config(text=current_track_name)
                            self.play_btn.config(text="Tạm dừng")

                            self.update_cover_image(self.music_player.current_track.get("image"))
                            
                            if self.music_controls_visible:
                                current_time = "0:00"
                                total_time = self.music_player.get_formatted_time(self.music_player.track_length)
                                self.time_label.config(text=f"{current_time} / {total_time}")
                            
                            if self.discord_available:
                                self.update_discord_status(current_track_name, 
                                    self.music_player.current_track.get("beatmapset_id"))
                        
                        except Exception as e:
                            print(f"Error updating UI for next track: {e}")
        except Exception as e:
            print(f"Error in check_music_end: {e}")
        
        try:
            self.after(1000, self.check_music_end)
        except Exception as e:
            print(f"Error scheduling next music end check: {e}")
    
    def reset_auto_next_cooldown(self):
        self.auto_next_cooldown = False

    def setup_discord_rpc(self):
        try:
            self.rpc = Presence(f"{config.config.DISCORD_CLIENT_ID}")
            self.rpc.connect()
            self.discord_available = True
            if hasattr(self, 'discord_toggle_btn'):
                self.discord_toggle_btn.config(text="Tắt Discord")
            print("Kết nối Discord RPC thành công")
        except Exception as e:
            print(f"Không thể kết nối Discord RPC: {e}")
            self.discord_available = False
            if hasattr(self, 'discord_toggle_btn'):
                self.discord_toggle_btn.config(text="Bật Discord")
    
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
        
        self.songs_listbox.bind('<Button-1>', self.show_song_image)
        self.songs_listbox.bind('<Return>', self.play_selected_song)
        self.songs_listbox.bind("<Double-1>", self.play_selected_song)
        
        player_frame = ttk.LabelFrame(self.main_frame, text="Trình phát")
        player_frame.pack(fill='x', padx=10, pady=10)

        controls_container = ttk.Frame(player_frame)
        controls_container.pack(fill='x', padx=10, pady=10)
        
        controls_frame = ttk.Frame(controls_container)
        controls_frame.pack(side=tk.LEFT, fill='y')

        basic_controls = ttk.Frame(controls_frame)
        basic_controls.pack(side=tk.TOP, fill='x', pady=5)

        self.play_btn = ttk.Button(basic_controls, text="Phát", command=self.toggle_play)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(basic_controls, text="Dừng", command=self.stop_music).pack(side=tk.LEFT, padx=5)
        
        self.mode_btn = ttk.Button(
            basic_controls,
            text="🔁", 
            command=self.toggle_play_mode,
            width=3 
        )
        self.mode_btn.pack(side=tk.LEFT, padx=5)
        
        self.discord_toggle_btn = ttk.Button(
            basic_controls, 
            text="Tắt Discord", 
            command=self.toggle_discord_connection,
        )
        self.discord_toggle_btn.pack(side=tk.LEFT, padx=5)
        
        self.music_controls_btn = ttk.Button(
            basic_controls,
            text="Tùy chỉnh nhạc",
            command=self.toggle_music_controls
        )
        self.music_controls_btn.pack(side=tk.LEFT, padx=5)
        
        self.advanced_controls_frame = ttk.Frame(controls_frame)
        
        volume_frame = ttk.Frame(self.advanced_controls_frame)
        volume_frame.pack(side=tk.TOP, fill='x', pady=5)
        
        ttk.Label(volume_frame, text="Âm lượng:").pack(side=tk.LEFT, padx=2)
        
        self.volume_scale = ttk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL
        )
        self.volume_scale.set(self.music_player.get_volume() * 100)
        self.volume_scale.pack(side=tk.LEFT, fill='x', expand=True, padx=5)
        self.volume_scale.bind("<ButtonRelease-1>", self.on_volume_change)
        
        time_frame = ttk.Frame(self.advanced_controls_frame)
        time_frame.pack(side=tk.TOP, fill='x', pady=5)
        
        self.time_label = ttk.Label(time_frame, text="0:00 / 0:00")
        self.time_label.pack(side=tk.LEFT, pady=2)
        
        self.cover_image_label = ttk.Label(controls_container)
        self.cover_image_label.pack(side=tk.RIGHT, padx=10)
        
        self.cover_image_label.bind("<Button-1>", 
            lambda e: self.show_fullsize_image(
                None  
            )
        )

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

    def show_song_image(self, event):
        index = self.songs_listbox.nearest(event.y)
        
        if 0 <= index < self.songs_listbox.size():
            song_name = self.songs_listbox.get(index)
            
            song = None
            for s in self.music_player.songs_data:
                if s["name"] == song_name:
                    song = s
                    break
            
            if song and song.get("image"):
                self.update_cover_image(song.get("image"))
    
    def show_fullsize_image(self, image_path):
        if not image_path:
            selection = self.songs_listbox.curselection()
            if selection:
                song_name = self.songs_listbox.get(selection[0])
                for song in self.music_player.songs_data:
                    if song["name"] == song_name:
                        image_path = song.get("image")
                        break

        if not image_path or not os.path.exists(image_path):
            messagebox.showwarning("Cảnh báo", "Không tìcover_image_label.bindm thấy ảnh")
            return
        
        try:
            window_width, window_height = 800, 600
            image_window = tk.Toplevel(self)
            image_window.title("Ảnh bài hát")
            image_window.geometry(f"{window_width}x{window_height}")
            image_window.configure(bg="black")
            # image_window.overrideredirect(True)
            image_window.iconbitmap("icon.ico") 
            image_window.resizable(False, False)

            img = Image.open(image_path)
            img_width, img_height = img.size

            scale = min(window_width / img_width, window_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(resized_img)

            canvas = tk.Canvas(image_window, width=window_width, height=window_height, bg="black", highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True)

            img_id = canvas.create_image(window_width // 2, window_height // 2, image=photo, anchor=tk.CENTER)

            canvas.image = photo

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở ảnh: {str(e)}")

    def update_cover_image(self, image_path=None):
        if not image_path or not os.path.exists(image_path):
            self.cover_image_label.config(image='', text='Không có ảnh')
            self.cover_image_label.image = None
            return

        try:
            img = Image.open(image_path)
            original_width, original_height = img.size
            scale = min(100 / original_width, 50 / original_height)
    
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.cover_image_label.config(image=photo)
            self.cover_image_label.image = photo 
        except Exception as e:
            print(f"Lỗi tải ảnh: {e}")
            self.cover_image_label.config(image='', text='Lỗi tải ảnh')

    def toggle_play_mode(self):
        self.shuffle_mode = not self.shuffle_mode
        
        if self.shuffle_mode:
            self.mode_btn.config(text="🔀")
            self.music_player.set_playback_mode(shuffle=True)
        else:
            self.mode_btn.config(text="🔁")
            self.music_player.set_playback_mode(shuffle=False)
        
        mode = "Trộn bài" if self.shuffle_mode else "Liên tục"
        self.current_track_label.config(text=f"Chế độ: {mode}", foreground="#43B581")
        self.after(2000, lambda: self.update_current_track_display())

    def update_current_track_display(self):
        if self.music_player.current_track:
            self.current_track_label.config(
                text=self.music_player.current_track["name"],
                foreground="white"
            )
        else:
            self.current_track_label.config(text="Không có bài nào", foreground="white")
    
    def toggle_discord_connection(self):
        if self.discord_available:
            self.discord_available = False
            if self.rpc:
                try:
                    self.rpc.close()
                except Exception as e:
                    print(f"Lỗi khi đóng kết nối Discord: {e}")
                finally:
                    self.rpc = None
            self.discord_toggle_btn.config(text="Bật Discord")
            if hasattr(self, 'discord_status_label'):
                self.discord_status_label.config(text="Đã tắt")
        else:
            try:
                self.rpc = Presence(f"{config.config.DISCORD_CLIENT_ID}")
                self.rpc.connect()
                self.discord_available = True
                self.discord_toggle_btn.config(text="Tắt Discord")
                if hasattr(self, 'discord_status_label'):
                    self.discord_status_label.config(text="Đã kết nối")
                
                if self.music_player.playing and self.music_player.current_track:
                    self.update_discord_status(
                        self.music_player.current_track["name"],
                        self.music_player.current_track.get("beatmapset_id")
                    )
            except Exception as e:
                print(f"Không thể kết nối lại Discord: {e}")
                self.discord_available = False
                self.discord_toggle_btn.config(text="Bật Discord")

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

                self.update_cover_image(song.get("image"))
                
                if self.music_controls_visible:
                    current_time = "0:00"
                    total_time = self.music_player.get_formatted_time(self.music_player.track_length)
                    self.time_label.config(text=f"{current_time} / {total_time}")
                
                if self.discord_available:
                    self.update_discord_status(song["name"], song["beatmapset_id"])
            else:
                tk.messagebox.showerror("Lỗi", f"Không thể phát bài hát:\n{result}")

    def remove_duration(self, song_name: str) -> str:
        return re.sub(r' - \d{1,2}:\d{2}$', '', song_name)
    
    def remove_copy_suffix(self, song_name: str) -> str:
        return re.sub(r' - copy$', '', song_name, flags=re.IGNORECASE)
    
    def update_discord_status(self, song_name, beatmapset_id=None):
        if not self.discord_available or not self.rpc:
            return

        try:
            buttons = []
            if beatmapset_id:
                buttons.append({
                    "label": "Xem Beatmap trên osu!", 
                    "url": f"https://osu.ppy.sh/beatmapsets/{beatmapset_id}"
                })

            song_name = self.remove_duration(song_name)
            song_name = self.remove_copy_suffix(song_name)

            update_data = {
                "details": f"{song_name}",
                "state": "Nghe nhạc trong Nericx",
                "start": int(time.time()),

                "large_text": song_name[:128],

                "large_image": "image1",
                "large_text": "Nericx",
            }

            if buttons:
                update_data["buttons"] = buttons  

            self.rpc.update(**update_data)
        except Exception as e:
            print(f"Lỗi cập nhật Discord RPC: {e}")

    def on_close(self):
        if self.rpc:
            self.rpc.close()
        
        if self.progress_update_id:
            self.after_cancel(self.progress_update_id)
    
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
            self.update_cover_image()
            
            if self.music_controls_visible:
                self.time_label.config(text="0:00 / 0:00")
        
            if self.discord_available and self.rpc:
                try:
                    self.rpc.clear()
                    if hasattr(self, 'discord_status_label'):
                        self.discord_status_label.config(text="Không hoạt động")
                except Exception as e:
                    print(f"Lỗi khi tắt Discord RPC: {e}")

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

    def update_progress_timer(self):
        if self.music_player.playing and self.music_player.current_track and self.music_controls_visible:
            current_pos, total_length = self.music_player.get_track_position()
            
            if current_pos < 0:
                current_pos = 0
                
            if total_length > 0:
                current_time = self.music_player.get_formatted_time(current_pos)
                total_time = self.music_player.get_formatted_time(total_length)
                self.time_label.config(text=f"{current_time} / {total_time}")
        
        self.progress_update_id = self.after(1000, self.update_progress_timer)
    
    def skip_forward(self):
        if self.music_player.current_track:
            self.music_player.skip_forward(5)
    
    def skip_backward(self):
        if self.music_player.current_track:
            self.music_player.skip_backward(5)

    def on_volume_change(self, event):
        volume = self.volume_scale.get() / 100.0
        self.music_player.set_volume(volume)

    def toggle_music_controls(self):
        if self.music_controls_visible:
            self.advanced_controls_frame.pack_forget()
            self.music_controls_btn.config(text="Tùy chỉnh nhạc")
            self.music_controls_visible = False
        else:
            self.advanced_controls_frame.pack(side=tk.TOP, fill='x', pady=5)
            self.music_controls_btn.config(text="Ẩn tùy chỉnh")
            self.music_controls_visible = True