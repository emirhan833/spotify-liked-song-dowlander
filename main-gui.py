import os
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import yt_dlp
import time
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

load_dotenv()

class SpotifyDownloaderApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Spotify beğenilen şarkı indirici")
        self.root.geometry("700x500")
        
        # Spotify Auth
        self.sp = None
        self.songs = []
        
        self.create_widgets()
    
    def create_widgets(self):
        # Başlık
        title = ctk.CTkLabel(self.root, text="🎵 Spotify Beğenilen Şarkılar İndirici", 
                           font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        # Butonlar
        self.login_btn = ctk.CTkButton(self.root, text="Spotify'a Giriş Yap", 
                                     command=self.login_spotify, width=300, height=40)
        self.login_btn.pack(pady=10)
        
        self.fetch_btn = ctk.CTkButton(self.root, text="Beğenilen Şarkıları Çek", 
                                     command=self.fetch_songs, state="disabled", width=300, height=40)
        self.fetch_btn.pack(pady=10)
        
        # Şarkı sayısı
        self.count_frame = ctk.CTkFrame(self.root)
        self.count_frame.pack(pady=10)
        
        ctk.CTkLabel(self.count_frame, text="İndirilecek şarkı sayısı:").pack(side="left", padx=10)
        self.song_count = ctk.CTkComboBox(self.count_frame, values=["5", "10", "25", "50", "100", "200", "300", "500", "Tümü"])
        self.song_count.set("5")
        self.song_count.pack(side="left", padx=10)
        
        self.download_btn = ctk.CTkButton(self.root, text="İndirmeye Başla", 
                                        command=self.start_download, state="disabled", width=300, height=40)
        self.download_btn.pack(pady=20)
        
        # Log alanı
        self.log_text = ctk.CTkTextbox(self.root, height=200, width=650)
        self.log_text.pack(pady=10, padx=20)
        
        self.status = ctk.CTkLabel(self.root, text="Hazır", text_color="gray")
        self.status.pack(pady=5)
    
    def log(self, message):
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.root.update()
    
    def login_spotify(self):
        try:
            self.log("Spotify girişi başlatılıyor...")
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
                redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
                scope="user-library-read",
                cache_path=".spotify_cache"
            ))
            self.log("✅ Spotify bağlantısı başarılı!")
            self.login_btn.configure(state="disabled")
            self.fetch_btn.configure(state="normal")
            messagebox.showinfo("Başarılı", "Spotify'a giriş yapıldı!")
        except Exception as e:
            messagebox.showerror("Hata", f"Giriş hatası: {e}")
    
    def fetch_songs(self):
        if not self.sp:
            messagebox.showwarning("Uyarı", "Önce Spotify'a giriş yapın!")
            return
        
        self.log("Beğenilen şarkılar çekiliyor...")
        try:
            self.songs = []
            results = self.sp.current_user_saved_tracks(limit=50)
            while results:
                for item in results['items']:
                    track = item['track']
                    if track:
                        self.songs.append({
                            'title': track['name'],
                            'artist': track['artists'][0]['name']
                        })
                results = self.sp.next(results)
                self.log(f"✅ {len(self.songs)} şarkı alındı...")
                time.sleep(0.5)
            
            self.log(f"🎉 Toplam {len(self.songs)} şarkı başarıyla çekildi.")
            self.download_btn.configure(state="normal")
        except Exception as e:
            self.log(f"❌ Hata: {e}")
    
    def download_song(self, song):
        query = f"{song['artist']} - {song['title']} lyrics"
        os.makedirs("downloads", exist_ok=True)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f"downloads/{song['artist']} - {song['title']}.%(ext)s",
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'noplaylist': True,
            'default_search': 'ytsearch',
            'restrictfilenames': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([query])
            self.log(f"✅ İndirildi: {song['artist']} - {song['title']}")
            return True
        except Exception as e:
            self.log(f"❌ Hata: {song['artist']} - {song['title']} → {e}")
            return False
    
    def start_download(self):
        if not self.songs:
            return
        
        # Seçilen sayı
        count_str = self.song_count.get()
        if count_str == "Tümü":
            to_download = self.songs
        else:
            to_download = self.songs[:int(count_str)]
        
        self.log(f"\n🚀 {len(to_download)} şarkı indirmeye başlanıyor...")
        self.download_btn.configure(state="disabled")
        
        # Arka planda indirme
        thread = threading.Thread(target=self.download_all, args=(to_download,))
        thread.daemon = True
        thread.start()
    
    def download_all(self, songs_list):
        for i, song in enumerate(songs_list, 1):
            self.log(f"[{i}/{len(songs_list)}] İndiriliyor...")
            self.download_song(song)
            time.sleep(2)  # YouTube limit koruması
        self.log("\n🎉 Tüm indirmeler tamamlandı!")
        self.download_btn.configure(state="normal")

# ====================== UYGULAMAYI BAŞLAT ======================
if __name__ == "__main__":
    app = SpotifyDownloaderApp()
    app.root.mainloop()