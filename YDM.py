import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import yt_dlp
import time
import webbrowser

# Global control flags
download_thread = None
is_paused = False
is_cancelled = False
current_url = ""
current_path = ""

def download_video():
    global is_paused, is_cancelled, download_thread, current_url, current_path
    url = url_entry.get()
    choice = format_choice.get()

    if not url:
        messagebox.showwarning("Warning", "Please enter a YouTube URL.")
        return

    save_path = filedialog.askdirectory()
    if not save_path:
        return

    is_paused = False
    is_cancelled = False
    current_url = url
    current_path = save_path
    progress_var.set(0)
    progress_label.config(text="Starting download...")

    def progress_hook(d):
        global is_paused, is_cancelled
        if is_cancelled:
            raise Exception("Download cancelled by user.")
        while is_paused:
            progress_label.config(text="Paused...")
            time.sleep(0.5)
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '').strip()
            progress_label.config(text=f"{percent}")
            try:
                progress = float(percent.replace('%', ''))
                progress_var.set(progress)
                progress_bar.update_idletasks()
            except ValueError:
                pass
        elif d['status'] == 'finished':
            progress_label.config(text="Download complete.")
            progress_var.set(100)
            progress_bar.update_idletasks()

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
            if str(e) == "Download cancelled by user.":
                progress_label.config(text="Download cancelled.")
            else:
                messagebox.showerror("Error", f"Download failed: {str(e)}")
                progress_label.config(text="Download failed.")

    download_thread = threading.Thread(target=run_download)
    download_thread.start()

def pause_download():
    global is_paused
    if is_paused:
        is_paused = False
        pause_btn.config(text="Pause")
        progress_label.config(text="Resuming...")
    else:
        is_paused = True
        pause_btn.config(text="Resume")
        progress_label.config(text="Paused. Click Resume to continue.")

def cancel_download():
    global is_cancelled
    is_cancelled = True
    progress_label.config(text="Cancelling download...")

def open_link(event):
    webbrowser.open_new("https://github.com/Ahamed-Shojib") 

# UI Setup
app = tk.Tk()
app.title("YouTube Video Downloader")
app.geometry("400x380")
app.resizable(False, False)

# Style for progress bar
style = ttk.Style(app)
style.theme_use('clam')
style.configure("green.Horizontal.TProgressbar", troughcolor='lightgray', background='green')

tk.Label(app, text="YouTube Video URL:").pack(pady=10)
url_entry = tk.Entry(app, width=50)
url_entry.pack(padx=10)

tk.Label(app, text="Download Format:").pack(pady=5)
format_choice = tk.StringVar(value='Video (MP4)')
tk.OptionMenu(app, format_choice, 'Video (MP4)', 'Audio (MP3)').pack()

tk.Button(app, text="Download", command=download_video, bg="#28a745", fg="white", width=23).pack(pady=5)

button_frame = tk.Frame(app)
button_frame.pack(pady=5)
pause_btn = tk.Button(button_frame, text="Pause", command=pause_download, bg="#ffc107", width=10)
pause_btn.pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Cancel", command=cancel_download, bg="#dc3545", fg="white", width=10).pack(side=tk.LEFT)

progress_label = tk.Label(app, text="")
progress_label.pack(pady=(10, 0))

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(app, length=300, variable=progress_var, maximum=100, style="green.Horizontal.TProgressbar")
#progress_bar.pack(pady=5)

# Developer Info and Link
ttk.Separator(app, orient='horizontal').pack(fill='x', padx=10, pady=10)
tk.Label(app, text="Developed by Ahamed_Shojib", font=("Arial", 9)).pack(pady=(15, 0))
link_label = tk.Label(app, text="Visit GitHub Profile", fg="blue", cursor="hand2", font=("Arial", 9, "underline"))
link_label.pack()
link_label.bind("<Button-1>", open_link)

app.mainloop()
