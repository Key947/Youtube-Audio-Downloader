import yt_dlp
import os
import tkinter as tk
from tkinter import messagebox

def download_youtube_as_m4a(youtube_url):
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))

        info_opts = {
            'quiet': True,
            'extract_flat': False,
            'noplaylist': False,
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(info_opts) as info_ydl:
            info = info_ydl.extract_info(youtube_url, download=False)

        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',  
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
                'preferredquality': '0',
            }],
            'noplaylist': False,
            'ignoreerrors': True,
            'ignore_no_formats_error': True,  
            'quiet': False,
            'no_warnings': True,  
            'overwrites': False,
            'merge_output_format': 'm4a',
            'continuedl': True,
        }

        if 'entries' in info:
            playlist_title = info.get('title', 'playlist')
            playlist_folder = os.path.join(base_path, playlist_title)
            os.makedirs(playlist_folder, exist_ok=True)
            ydl_opts['outtmpl'] = os.path.join(playlist_folder, '%(title)s.%(ext)s')
        else:
            ydl_opts['outtmpl'] = os.path.join(base_path, '%(title)s.%(ext)s')

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        messagebox.showinfo("Download Complete", "Download finished successfully!")

    except yt_dlp.utils.DownloadError as e:
        if 'nsig' in str(e):
            messagebox.showerror(
                "Signature Extraction Failed",
                "YouTube has changed something. Please update yt-dlp:\n\npip install -U yt-dlp"
            )
        else:
            messagebox.showerror("Download Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", str(e))

def on_download_click():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Input Needed", "Please enter a YouTube URL.")
        return
    download_youtube_as_m4a(url)

root = tk.Tk()
root.title("YouTube Music/Audio Downloader")
root.geometry("500x200")

tk.Label(root, text="YouTube Video or Playlist URL:").pack(pady=5)
url_entry = tk.Entry(root, width=60)
url_entry.pack()

tk.Label(root, text="Files will be saved in the same directory as this script.").pack(pady=5)
tk.Label(root, text="A new folder will be created using the playlist name if it's a playlist.").pack(pady=0)

tk.Button(root, text="Download", command=on_download_click, bg="green", fg="white").pack(pady=20)

root.mainloop()
