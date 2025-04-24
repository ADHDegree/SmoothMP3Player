import tkinter as tk
from tkinter import filedialog
import pygame
import threading
import time

class DualTrackPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Dual Track Player")

        pygame.mixer.init()

        self.vocals_path = None
        self.instrumental_path = None
        self.vocals = None
        self.instrumental = None

        self.channel_vocals = pygame.mixer.Channel(0)
        self.channel_instr = pygame.mixer.Channel(1)

        self.is_paused = False
        self.fade_duration = 1.5  # seconds

        # Buttons to load
        self.load_instr_button = tk.Button(root, text="Load Instrumental", command=self.load_instrumental)
        self.load_instr_button.pack(pady=5)

        self.load_vocals_button = tk.Button(root, text="Load Vocals", command=self.load_vocals)
        self.load_vocals_button.pack(pady=5)

        # slider
        self.slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, length=300,
                               label="Instrumental <--> Vocals", command=self.adjust_mix)
        self.slider.set(0)  # Start on instrumental
        self.slider.pack(pady=20)

        # Play/Pause
        self.play_pause_button = tk.Button(root, text="Play", command=self.toggle_play_pause)
        self.play_pause_button.pack(pady=10)

    def load_instrumental(self):
        path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        if path:
            self.instrumental_path = path
            self.instrumental = pygame.mixer.Sound(path)
            self.try_play()

    def load_vocals(self):
        path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        if path:
            self.vocals_path = path
            self.vocals = pygame.mixer.Sound(path)
            self.try_play()

    def try_play(self):
        if self.vocals and self.instrumental:
            self.channel_vocals.play(self.vocals, loops=-1)
            self.channel_instr.play(self.instrumental, loops=-1)
            self.adjust_mix(self.slider.get())
            self.is_paused = False
            self.play_pause_button.config(text="Pause")

    def adjust_mix(self, val):
        val = int(val)
        vocals_volume = val / 100.0
        instr_volume = 1.0 - vocals_volume
        self.channel_vocals.set_volume(vocals_volume)
        self.channel_instr.set_volume(instr_volume)

    def toggle_play_pause(self):
        if not self.vocals or not self.instrumental:
            return

        if not self.is_paused:
            threading.Thread(target=self._fade_out_pause, daemon=True).start()
            self.is_paused = True
            self.play_pause_button.config(text="Play")
        else:
            threading.Thread(target=self._fade_in_resume, daemon=True).start()
            self.is_paused = False
            self.play_pause_button.config(text="Pause")

    def _fade_out_pause(self):
        for i in range(10, -1, -1):
            volume = i / 10.0
            self.channel_vocals.set_volume(volume * (self.slider.get() / 100.0))
            self.channel_instr.set_volume(volume * (1.0 - self.slider.get() / 100.0))
            time.sleep(self.fade_duration / 10)
        self.channel_vocals.pause()
        self.channel_instr.pause()

    def _fade_in_resume(self):
        self.channel_vocals.unpause()
        self.channel_instr.unpause()
        for i in range(10):
            volume = i / 10.0
            self.channel_vocals.set_volume(volume * (self.slider.get() / 100.0))
            self.channel_instr.set_volume(volume * (1.0 - self.slider.get() / 100.0))
            time.sleep(self.fade_duration / 10)

    def stop(self):
        self.channel_vocals.stop()
        self.channel_instr.stop()
        pygame.mixer.quit()


if __name__ == "__main__":
    root = tk.Tk()
    player = DualTrackPlayer(root)

    def on_close():
        player.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
