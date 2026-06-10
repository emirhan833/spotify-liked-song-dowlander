import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import yt_dlp
import time

load_dotenv()

# ====================== SPOTIFY BAĞLANTISI ======================
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope="user-library-read",
    cache_path=".spotify_cache"
))

# ====================== ŞARKI ÇEKME ======================
def get_liked_songs(limit=50, total_limit=1000):
    """Beğenilen şarkıları Spotify'dan çeker"""
    songs = []
    results = sp.current_user_saved_tracks(limit=limit)
    
    while results and len(songs) < total_limit:
        for item in results['items']:
            track = item['track']
            if track is None:
                continue
            songs.append({
                'title': track['name'],
                'artist': track['artists'][0]['name'],
                'album': track['album']['name']
            })
        
        print(f"✅ {len(songs)} şarkı alındı...")
        results = sp.next(results)
        time.sleep(1)  # Rate limit koruması
    
    print(f"🎉 Toplam {len(songs)} şarkı başarıyla alındı.")
    return songs

# ====================== İNDİRME ======================
def download_song(song):
    """YouTube'dan şarkıyı indirir"""
    query = f"{song['artist']} - {song['title']} lyrics"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f"downloads/{song['artist']} - {song['title']}.%(ext)s",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'noplaylist': True,
        'default_search': 'ytsearch',
        'restrictfilenames': True,   # Dosya isminde sorun çıkmasın
    }
    
    try:
        print(f"İndiriliyor → {song['artist']} - {song['title']}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([query])
        print("✅ Tamamlandı\n")
        return True
    except Exception as e:
        print(f"❌ Hata: {e}\n")
        return False

# ====================== ANA FONKSİYON ======================
def main():
    print("🎵 Spotify Liked Songs Downloader\n")
    print("İlk 5 şarkı indiriliyor...\n")
    
    # Tüm beğenilen şarkıları al
    songs = get_liked_songs(total_limit=1000)
    
    # Sadece ilk 5 şarkıyı seç
    selected_songs = songs[:5]
    
    print(f"Toplam {len(songs)} şarkı bulundu. İlk {len(selected_songs)} şarkı indirilecek.\n")
    
    os.makedirs("downloads", exist_ok=True)
    
    for i, song in enumerate(selected_songs, 1):
        print(f"[{i}/{len(selected_songs)}] ", end="")
        download_song(song)
        
        if i < len(selected_songs):
            time.sleep(3)  # YouTube ban yememek için ara
    
    print("✅ İlk 5 şarkı indirme işlemi tamamlandı!")


if __name__ == "__main__":
    main()