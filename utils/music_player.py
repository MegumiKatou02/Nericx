import pygame
import os
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis

class MusicPlayer:
    def __init__(self):
        # pygame.mixer.init()
        try:
            pygame.init() 
            pygame.mixer.init()
            pygame.mixer.music.set_endevent(pygame.USEREVENT)
        except Exception as e:
            print(f"Pygame initialization error: {e}")

        self.current_track = None
        self.playing = False
        self.songs_data = []
        self.filtered_songs = []
        self.current_index = -1
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
    
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
                audio_files = [
                    f for f in os.listdir(folder_path)
                    if f.lower().endswith('.mp3') or f.lower() == "audio.ogg"
                ]
                
                if audio_files:
                    for audio_file  in audio_files:
                        # song_name = f"{' '.join(song_folder.split(' ')[1:])} - {os.path.splitext(mp3)[0]}"
                        song_path = os.path.join(folder_path, audio_file)
                        
                        if audio_file.lower().endswith('.mp3'):
                            audio = MP3(song_path)
                        else:
                            audio = OggVorbis(song_path)

                        duration = int(audio.info.length)

                        minutes = duration // 60
                        seconds = duration % 60
                        duration_str = f"{minutes}:{seconds:02d}"

                        song_name = f"{' '.join(song_folder.split(' ')[1:])} - {duration_str}"
                        self.songs_data.append({
                            "name": song_name,
                            "path": song_path,
                            "beatmapset_id": beatmapset_id
                        })
                # sort
                self.songs_data.sort(key=lambda song: song["name"].lower())
        
        self.filtered_songs = self.songs_data.copy()
        return True, "Songs loaded successfully"
    
    def play_music(self, song, index=None):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        
        try:
            pygame.mixer.music.load(song["path"])
            pygame.mixer.music.play()
            
            self.current_track = song
            self.current_index = index if index is not None else self.find_song_index(song)
            self.playing = True
            return True, song["name"]
        except Exception as e:
            return False, str(e)
    
    def find_song_index(self, song):
        for i, s in enumerate(self.filtered_songs):
            if s["path"] == song["path"]:
                return i
        return -1
    
    def play_next(self):
        if not self.filtered_songs:
            return False, "No songs available"

        if self.current_index == -1 and self.filtered_songs:
            self.current_index = 0

        next_index = (self.current_index + 1) % len(self.filtered_songs)
        next_song = self.filtered_songs[next_index]
        return self.play_music(next_song, next_index)
    
    def check_music_end(self):
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                return self.play_next()
        return False, None
    
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
    
    def __del__(self):
        try:
            pygame.mixer.quit()
            pygame.quit()
        except Exception:
            pass