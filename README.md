# 🎵 Spotify Liked Downloader

Скачивает все лайкнутые треки из Spotify как MP3 через YouTube (yt-dlp) с вшитыми метаданными и обложками.
Downloads liked tracks from Spotify and saves them as MP3 files with metadata and album art.

## Зависимости

Нужен установленный **ffmpeg** (для конвертации в MP3):
- Windows: `winget install ffmpeg` или скачать с [ffmpeg.org](https://ffmpeg.org)
- Linux: `sudo apt install ffmpeg`

## Запуск

```bash
pip install -r requirements.txt
cp .env.example .env  # заполнить CLIENT_ID и CLIENT_SECRET !!
python downloader.py
```

Получить `CLIENT_ID` и `CLIENT_SECRET`: [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) → Create App.

При первом запуске откроется браузер для авторизации. Токен сохранится в `.spotify_cache`.

## Результат

Треки сохраняются в папку `Spotify_Liked_Playlist/` в формате `Artist - Title.mp3` с тегами и обложкой.
