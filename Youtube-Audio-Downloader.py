import yt_dlp
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext

def download_youtube_as_audio(youtube_url):
    failed_downloads = []
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        progress_label.config(text="Starting download...")

        def progress_hook(d):
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', '').strip()
                progress_label.config(text=f"Downloading: {percent}")
                root.update_idletasks()
            elif d['status'] == 'finished':
                progress_label.config(text="Processing...")
                root.update_idletasks()

        info_opts = {
            'quiet': True,
            'extract_flat': False,
            'noplaylist': False,
            'skip_download': True,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            'ignoreerrors': True
        }

        # Try getting playlist/video info
        with yt_dlp.YoutubeDL(info_opts) as info_ydl:
            try:
                info = info_ydl.extract_info(youtube_url, download=False)
            except Exception as e:
                failed_downloads.append((youtube_url, f"Failed to retrieve info: {e}"))
                show_failed_downloads(failed_downloads)
                return

        def choose_best_format(formats):
            for f in formats:
                if f.get('ext') == 'm4a' and not f.get('has_drm'):
                    return f['format_id']
            for f in formats:
                if f.get('ext') == 'webm' and not f.get('has_drm'):
                    return f['format_id']
            for f in formats:
                if f.get('acodec') != 'none' and not f.get('has_drm'):
                    return f['format_id']
            return None

        ydl_opts = {
            'noplaylist': False,
            'ignoreerrors': True,
            'ignore_no_formats_error': True,
            'quiet': True,
            'no_warnings': True,
            'overwrites': False,
            'continuedl': True,
            'concurrent_fragment_downloads': 1,
            'progress_hooks': [progress_hook],
            'geo_bypass': True,
            'geo_bypass_country': 'US',
        }

        # Determine if playlist or single video
        if 'entries' in info:
            playlist_title = info.get('title', 'playlist')
            playlist_folder = os.path.join(base_path, playlist_title)
            os.makedirs(playlist_folder, exist_ok=True)
            ydl_opts['outtmpl'] = os.path.join(playlist_folder, '%(title)s.%(ext)s')
            urls = [entry['url'] for entry in info['entries'] if entry]
        else:
            ydl_opts['outtmpl'] = os.path.join(base_path, '%(title)s.%(ext)s')
            urls = [youtube_url]

        # Download each video individually
        for url in urls:
            try:
                with yt_dlp.YoutubeDL(info_opts) as temp_ydl:
                    try:
                        video_info = temp_ydl.extract_info(url, download=False)
                    except yt_dlp.utils.DownloadError as e:
                        if "Private video" in str(e):
                            failed_downloads.append((url, "Private video - skipped"))
                            continue
                        failed_downloads.append((url, f"Info retrieval failed: {e}"))
                        continue

                if not video_info:
                    failed_downloads.append((url, "No metadata available"))
                    continue

                best_format_id = choose_best_format(video_info.get('formats', []))
                if not best_format_id:
                    failed_downloads.append((video_info.get('title', 'Unknown'), "No suitable format found"))
                    continue

                ydl_opts['format'] = best_format_id

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    result = ydl.download([url])
                    if result != 0:
                        failed_downloads.append((video_info.get('title', 'Unknown'), "Download failed"))

            except Exception as e:
                failed_downloads.append((video_info.get('title', 'Unknown'), str(e)))
                continue

        progress_label.config(text="Done!")
        if failed_downloads:
            show_failed_downloads(failed_downloads)
        else:
            messagebox.showinfo("Download Complete", "All downloads finished successfully!")
    except Exception as e:
        progress_label.config(text="Error")
        messagebox.showerror("Error", str(e))

def show_failed_downloads(failed_list):
    fail_window = tk.Toplevel(root)
    fail_window.title("Failed Downloads")
    fail_window.geometry("600x400")
    tk.Label(fail_window, text="Some videos could not be downloaded:").pack(pady=5)

    text_area = scrolledtext.ScrolledText(fail_window, wrap=tk.WORD, width=70, height=20)
    text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    for title, reason in failed_list:
        text_area.insert(tk.END, f"Title/URL: {title}\nReason: {reason}\n\n")
    text_area.config(state=tk.DISABLED)

def on_download_click():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Input Needed", "Please enter a YouTube URL.")
        return
    root.after(100, lambda: download_youtube_as_audio(url))

root = tk.Tk()
root.title("YouTube Music/Audio Downloader")
root.geometry("500x230")

tk.Label(root, text="YouTube Video or Playlist URL:").pack(pady=5)
url_entry = tk.Entry(root, width=60)
url_entry.pack()

progress_label = tk.Label(root, text="Idle")
progress_label.pack(pady=5)

tk.Label(root, text="Files will be saved in the same directory as this script.").pack(pady=5)
tk.Label(root, text="A new folder will be created using the playlist name if it's a playlist.").pack(pady=0)
tk.Button(root, text="Download", command=on_download_click, bg="green", fg="white").pack(pady=20)

root.mainloop()
