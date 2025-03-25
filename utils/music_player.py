import pygame
import os
from datetime import datetime

class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.current_track = None
        self.playing = False
        self.songs_data = []
    
    def load_songs(self, osu_path):
        songs_path = os.path.join(osu_path, "Songs")
        self.songs_data = []
        
        if not os.path.exists(songs_path):
            return False, "Không tìm thấy thư mục Songs!"

        for song_folder in os.listdir(songs_path):
            folder_path = os.path.join(songs_path, song_folder)
            
            if os.path.isdir(folder_path):
                beatmapset_id = song_folder.split(" ")[0] if " " in song_folder else None
                
                mp3_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp3')]
                
                if mp3_files:
                    for mp3 in mp3_files:
                        song_name = f"{' '.join(song_folder.split(' ')[1:])} - {os.path.splitext(mp3)[0]}"
                        song_path = os.path.join(folder_path, mp3)

                        self.songs_data.append({
                            "name": song_name,
                            "path": song_path,
                            "beatmapset_id": beatmapset_id
                        })
        
        return True, "Songs loaded successfully"
    
    def play_music(self, song):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        
        try:
            pygame.mixer.music.load(song["path"])
            pygame.mixer.music.play()
            
            self.current_track = song
            self.playing = True
            return True, song["name"]
        except Exception as e:
            return False, str(e)
    
    def toggle_play(self):
        if not self.current_track:
            return False, "No track selected"
        
        if self.playing:
            pygame.mixer.music.pause()
            self.playing = False
            return True, "Paused"
        else:
            pygame.mixer.music.unpause()
            self.playing = True
            return True, "Playing"
    
    def stop_music(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.current_track = None
        return True, "Stopped"
    
    def get_song_list(self):
        return [song["name"] for song in self.songs_data]
    
    def get_song_by_name(self, name):
        for song in self.songs_data:
            if song["name"] == name:
                return song
        return None