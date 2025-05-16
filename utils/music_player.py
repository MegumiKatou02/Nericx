import pygame
import os
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
import random

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
        self.shuffle_mode = False
        self.track_length = 0
        self.volume = 0.5
        pygame.mixer.music.set_volume(self.volume)
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
                
                image_files = [
                    f for f in os.listdir(folder_path) 
                    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
                ]

                background_images = [
                    f for f in image_files 
                    if any(bg in f.lower() for bg in ['bg', 'background'])
                ]

                image_path = None
                if background_images:
                    image_path = os.path.join(folder_path, background_images[0])
                elif image_files:
                    image_path = os.path.join(folder_path, image_files[0])

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
                            "beatmapset_id": beatmapset_id,
                            "image": image_path
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
            
            if song["path"].lower().endswith('.mp3'):
                audio = MP3(song["path"])
            else:
                audio = OggVorbis(song["path"])
            self.track_length = audio.info.length
            
            return True, song["name"]
        except Exception as e:
            return False, str(e)
    
    def find_song_index(self, song):
        for i, s in enumerate(self.filtered_songs):
            if s["path"] == song["path"]:
                return i
        return -1
    
    def set_playback_mode(self, shuffle=False):
        self.shuffle_mode = shuffle
    
    def play_next(self):
        if not self.filtered_songs:
            return False, "No songs available"

        if self.current_index == -1 and self.filtered_songs:
            self.current_index = 0
        
        if not self.shuffle_mode:
            next_index = (self.current_index + 1) % len(self.filtered_songs)
            next_song = self.filtered_songs[next_index]
            return self.play_music(next_song, next_index)
        else:
            next_index = random.randint(0, len(self.filtered_songs) - 1)
            while next_index == self.current_index and len(self.filtered_songs) > 1:
                next_index = random.randint(0, len(self.filtered_songs) - 1)

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
    
    def get_track_position(self):
        """Return current position in seconds and total length in seconds"""
        if not self.current_track:
            return 0, 0
        
        current_pos = pygame.mixer.music.get_pos() / 1000 
        
        return current_pos, self.track_length
    
    def get_formatted_time(self, seconds):
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
    
    def seek(self, position):
        """Seek to a position in the track (position is 0.0 to 1.0)"""
        if not self.current_track or position < 0 or position > 1:
            return False
        
        target_time = position * self.track_length
        
        try:
            was_playing = self.playing
            current_volume = self.volume
            
            pygame.mixer.music.set_volume(0.1)
            
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.current_track["path"])
            pygame.mixer.music.play(start=target_time)
            
            pygame.mixer.music.set_volume(current_volume)
            
            if not was_playing:
                pygame.mixer.music.pause()
            
            self.playing = was_playing
            return True
        except Exception as e:
            print(f"Error seeking: {e}")
            return False
    
    def skip_forward(self, seconds=5):
        """Skip forward by the specified number of seconds"""
        if not self.current_track:
            return False
        
        current_pos, total_length = self.get_track_position()
        new_pos = min(current_pos + seconds, total_length) / total_length
        return self.seek(new_pos)
    
    def skip_backward(self, seconds=5):
        """Skip backward by the specified number of seconds"""
        if not self.current_track:
            return False
        
        current_pos, total_length = self.get_track_position()
        new_pos = max(current_pos - seconds, 0) / total_length
        return self.seek(new_pos)
    
    def set_volume(self, volume):
        """Set volume between 0.0 and 1.0"""
        if 0.0 <= volume <= 1.0:
            self.volume = volume
            pygame.mixer.music.set_volume(volume)
            return True
        return False
    
    def get_volume(self):
        """Get current volume"""
        return self.volume
    
    def __del__(self):
        try:
            pygame.mixer.quit()
            pygame.quit()
        except Exception:
            pass