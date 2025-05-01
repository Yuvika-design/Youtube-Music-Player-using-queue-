# -*- coding: utf-8 -*-
from collections import deque
import pygame
import time
import os
from pytube import YouTube
from pydub import AudioSegment

import re
import yt_dlp

def clean_youtube_url(url):
    """
    Converts short links to full YouTube URLs and strips extra parameters.
    """
    # Convert youtu.be short link to full format
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"
   
    # For full links, remove extra query parameters
    match = re.search(r"(v=([a-zA-Z0-9_-]+))", url)
    if match:
        video_id = match.group(2)
        return f"https://www.youtube.com/watch?v={video_id}"
   
    raise ValueError("❌ Invalid YouTube URL")


class MusicPlayer:
    def __init__(self):
        self.queue = deque()
        pygame.mixer.init()

    def download_youtube_audio(self, url, output_folder="downloads"):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
   
        print("📥 Downloading from YouTube...")

        clean_url = clean_youtube_url(url)
        ydl_opts = {
          'format': 'bestaudio/best',
          'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
          'postprocessors': [{
              'key': 'FFmpegExtractAudio',
              'preferredcodec': 'mp3',
              'preferredquality': '192',
          }],
          'quiet': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
          info = ydl.extract_info(clean_url, download=True)
          mp3_file = os.path.join(output_folder, f"{info['title']}.mp3")
       

        print(f"✅ Downloaded and converted: {mp3_file}")
        return mp3_file

    def add_youtube_song(self, url):
        try:
            mp3_path = self.download_youtube_audio(url)
            self.queue.append(mp3_path)
            print(f"🎶 YouTube song added to queue: {mp3_path}")
        except Exception as e:
            print(f"❌ Error downloading YouTube song: {e}")

    def add_song(self, filepath):
        if os.path.exists(filepath):
            self.queue.append(filepath)
            print(f"🎶 '{filepath}' added to queue.")
        else:
            print("❌ File does not exist.")

    def play_song(self):
        if self.queue:
            current_song = self.queue[0]
            print(f"▶️ Now playing: '{current_song}'")
            pygame.mixer.music.load(current_song)
            pygame.mixer.music.play()
        else:
            print("🛑 No songs in queue.")

    def skip_song(self):
        if self.queue:
            skipped = self.queue.popleft()
            print(f"⏭️ Skipped: '{skipped}'")
            pygame.mixer.music.stop()
            self.play_song()
        else:
            print("❌ No songs to skip.")

    def show_queue(self):
        if self.queue:
            print("🎵 Songs in queue:")
            for idx, song in enumerate(self.queue, 1):
                print(f"{idx}. {song}")
        else:
            print("📭 The queue is empty.")

    def remove_song(self, song_name):
        found = None
        for song in self.queue:
            if song_name in song:
                found = song
                break
        if found:
            self.queue.remove(found)
            print(f"🗑️ Removed: '{found}'")
        else:
            print(f"❌ '{song_name}' not found in queue.")


if __name__ == "__main__":
    player = MusicPlayer()
    while True:
        print("\nOptions: add, youtube, play, skip, show, remove, exit")
        command = input("Enter command: ").strip().lower()

        if command == "add":
            path = input("Enter full path to song (e.g., C:\\Users\\You\\song.mp3): ")
            player.add_song(path)

        elif command == "youtube":
            yt_link = input("Enter YouTube song link: ")
            player.add_youtube_song(yt_link)

        elif command == "play":
            player.play_song()

        elif command == "skip":
            player.skip_song()

        elif command == "show":
            player.show_queue()

        elif command == "remove":
            name = input("Enter part of the filename to remove: ")
            player.remove_song(name)

        elif command == "exit":
            print("👋 Exiting music player.")
            pygame.mixer.music.stop()
            break

        else:
            print("❓ Unknown command.")

