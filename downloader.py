import spotipy
from spotipy.oauth2 import SpotifyOAuth
import yt_dlp
import os
import sys
import re
import requests
import logging
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, error
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(filename='download_log.txt', level=logging.INFO,
                    format='%(asctime)s %(message)s')

DOWNLOAD_FOLDER = "Spotify_Liked_Playlist"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")

if not client_id or not client_secret:
    print("❌ Ошибка: Убедитесь, что SPOTIFY_CLIENT_ID и SPOTIFY_CLIENT_SECRET заполнены в файле .env")
    sys.exit(1)

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="user-library-read"
))

def get_liked_tracks():
    tracks = []
    results = sp.current_user_saved_tracks(limit=50)
    while results:
        for item in results['items']:
            track = item['track']
            tracks.append({
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'album': track['album']['name'],
                'cover_url': track['album']['images'][0]['url'] if track['album']['images'] else None
            })
        results = sp.next(results)
    return tracks

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def download_song(track):
    song_query = f"{track['name']} {track['artist']} audio"
    
    safe_artist = sanitize_filename(track['artist'])
    safe_name = sanitize_filename(track['name'])
    output_template = os.path.join(DOWNLOAD_FOLDER, f"{safe_artist} - {safe_name}.%(ext)s")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}],
        'quiet': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"ytsearch:{song_query}"])
        
    mp3_path = output_template.replace("%(ext)s", "mp3")
    add_metadata(track, mp3_path)

def add_metadata(track, mp3_path):
    if not os.path.exists(mp3_path):
        logging.error(f"Файл не найден после скачивания: {mp3_path}")
        return

    try:
        audio = EasyID3(mp3_path)
    except error.ID3NoHeaderError:
        tag = ID3()
        tag.save(mp3_path)
        audio = EasyID3(mp3_path)
        
    audio['title'] = track['name']
    audio['artist'] = track['artist']
    audio['album'] = track['album']
    audio.save()
    
    if track['cover_url']:
        try:
            album_cover = requests.get(track['cover_url'], timeout=10).content
            audio = ID3(mp3_path)
            audio.add(APIC(mime='image/jpeg', type=3, desc='Cover', data=album_cover))
            audio.save()
        except Exception as e:
            logging.error(f"Не удалось скачать обложку для {track['name']} - {e}")

def main():
    try:
        tracks = get_liked_tracks()
    except spotipy.exceptions.SpotifyException as e:
        print(f"❌ Ошибка Spotify: {e}. Возможно, неверные ключи или токен.")
        return

    print(f"Найдено {len(tracks)} треков. Начинаю скачивание...")
    for i, track in enumerate(tracks, 1):
        try:
            print(f"[{i}/{len(tracks)}] {track['artist']} - {track['name']}")
            download_song(track)
            logging.info(f"Downloaded: {track['name']} by {track['artist']}")
        except Exception as e:
            logging.error(f"Failed: {track['name']} by {track['artist']} - {e}")
            print(f"  Ошибка: {e}")

if __name__ == "__main__":
    main()
