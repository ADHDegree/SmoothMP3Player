import tkinter as tk
from tkinter import filedialog
import pygame
import threading
import time
import json
import os

class MP3Player:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Library Player")
        
        self.songs = {}  # Dictionary to store song file paths
        self.current_song = None
        self.is_paused = False
        self.fade_duration = 1.5  # Seconds for fading stuff in/out
        self.library_file = "mp3_library.json"
        
        pygame.mixer.init()
        
        self.load_button = tk.Button(root, text="Import MP3", command=self.import_mp3)
        self.load_button.pack()
        
        self.song_frame = tk.Frame(root)
        self.song_frame.pack()
        
        self.play_pause_button = tk.Button(root, text="Play/Pause", command=self.toggle_play_pause)
        self.play_pause_button.pack()
        
        self.load_library()
    
    def save_library(self):
        with open(self.library_file, "w") as f:
            json.dump(self.songs, f)
    
    def load_library(self):
        if os.path.exists(self.library_file):
            with open(self.library_file, "r") as f:
                self.songs = json.load(f)
            for song_name in self.songs:
                self.add_song_button(song_name)
    
    def import_mp3(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        if file_path:
            song_name = file_path.split("/")[-1]  # Pulling filename
            if song_name not in self.songs:
                self.songs[song_name] = file_path
                self.add_song_button(song_name)
                self.save_library()
    
    def add_song_button(self, song_name):
        frame = tk.Frame(self.song_frame)
        frame.pack(fill=tk.X)
        
        button = tk.Button(frame, text=song_name, command=lambda: self.play_song(song_name))
        button.pack(side=tk.LEFT)
        
        remove_button = tk.Button(frame, text="X", command=lambda: self.remove_song(song_name, frame))
        remove_button.pack(side=tk.RIGHT)
    
    def remove_song(self, song_name, frame):
        if song_name in self.songs:
            del self.songs[song_name]
            self.save_library()
            frame.destroy()
    
    def play_song(self, song_name):
        if self.current_song == song_name and not self.is_paused:
            return  # Ignoring if the same song is already selected an playing
        
        threading.Thread(target=self._play_with_fade, args=(song_name,), daemon=True).start()
    
    def _play_with_fade(self, song_name):
        if self.current_song:
            self._crossfade(song_name)
        else:
            self._start_song(song_name)
    
    def _start_song(self, song_name):
        self.current_song = song_name
        song_path = self.songs[song_name]
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.set_volume(0.0)
        pygame.mixer.music.play(loops=-1)
        self._fade_in()
    
    def _fade_in(self):
        for i in range(10):
            pygame.mixer.music.set_volume(i / 10.0)
            time.sleep(self.fade_duration / 10)
    
    def _fade_out(self):
        for i in range(10, -1, -1):
            pygame.mixer.music.set_volume(i / 10.0)
            time.sleep(self.fade_duration / 10)
        pygame.mixer.music.stop()
    
    def _crossfade(self, new_song):
        self._fade_out()
        self._start_song(new_song)
    
    def toggle_play_pause(self):
        if pygame.mixer.music.get_busy():
            threading.Thread(target=self._fade_out_pause, daemon=True).start()
            self.is_paused = True
        else:
            threading.Thread(target=self._fade_in_resume, daemon=True).start()
            self.is_paused = False
    
    def _fade_out_pause(self):
        for i in range(10, -1, -1):
            pygame.mixer.music.set_volume(i / 10.0)
            time.sleep(self.fade_duration / 10)
        pygame.mixer.music.pause()
    
    def _fade_in_resume(self):
        pygame.mixer.music.unpause()
        for i in range(10):
            pygame.mixer.music.set_volume(i / 10.0)
            time.sleep(self.fade_duration / 10)

if __name__ == "__main__":
    root = tk.Tk()
    player = MP3Player(root)
    root.mainloop()
