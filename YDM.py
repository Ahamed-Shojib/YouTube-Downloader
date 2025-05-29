#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import yt_dlp

def download_video():
    url = url_entry.get()
    choice = format_choice.get()

    if not url:
        messagebox.showwarning("Warning", "Please enter a YouTube URL.")
        return

    save_path = filedialog.askdirectory()
    if not save_path:
        return

    progress_var.set(0)
    progress_label.config(text="Starting download...")

    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0.0%').strip()
            eta = d.get('eta', '?')
            speed = d.get('_speed_str', '?')
            size = d.get('_total_bytes_str', '?')
            progress_label.config(text=f"Downloading: {percent} | ETA: {eta}s | Speed: {speed}")
            try:
                progress = float(percent.replace('%', ''))
                progress_var.set(progress)
            except ValueError:
                pass
        elif d['status'] == 'finished':
            progress_label.config(text="Download complete.")

    ydl_opts = {
        'outtmpl': f'{save_path}/%(title)s.%(ext)s',
        'progress_hooks': [progress_hook],
        'quiet': True,
        'noprogress': True,
    }

    if choice == 'Audio (MP3)':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        })
    elif choice == 'Video (MP4)':
        ydl_opts['format'] = 'bestvideo+bestaudio/best'

    def run_download():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            messagebox.showinfo("Success", "Download completed!")
        except Exception as e:
            messagebox.showerror("Error", f"Download failed: {str(e)}")
            progress_label.config(text="Download failed.")

    threading.Thread(target=run_download).start()

# UI Setup
app = tk.Tk()
app.title("YouTube Video Downloader")
app.geometry("400x280")
app.resizable(False, False)

tk.Label(app, text="YouTube Video URL:").pack(pady=10)
url_entry = tk.Entry(app, width=50)
url_entry.pack(padx=10)

tk.Label(app, text="Download Format:").pack(pady=5)
format_choice = tk.StringVar(value='Video (MP4)')
tk.OptionMenu(app, format_choice, 'Video (MP4)', 'Audio (MP3)').pack()

tk.Button(app, text="Download", command=download_video, bg="#28a745", fg="white", width=20).pack(pady=5)

progress_label = tk.Label(app, text="")
progress_label.pack(pady=(10, 0))

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(app, length=300, variable=progress_var, maximum=100)
progress_bar.pack(pady=5)

app.mainloop()
