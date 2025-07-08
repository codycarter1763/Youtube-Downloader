import yt_dlp
import customtkinter
from tkinter import filedialog, messagebox, StringVar
import os
import threading
from PIL import Image, ImageTk
import requests
from io import BytesIO
from tkinter import PhotoImage
import sys

def list_formats(url):
    try:
            ydl_opts = {
            'quiet': True,
            'noplaylist': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                formats = info_dict.get('formats', None)
            if formats:
                format_list = "Available formats:\n"
                for f in formats:
                    format_list += (f"Format ID: {f['format_id']}, "
                                    f"Extension: {f['ext']}, "
                                    f"Resolution: {f.get('resolution', 'N/A')}, "
                                    f"Size: {f.get('filesize', 'unknown')} bytes\n")
                messagebox.showinfo("Available Formats", format_list)
            else:
                messagebox.showwarning("Warning", "No formats available.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to list formats: {e}")

def download_video(url):
    global destination_folder, selected_format
    if not destination_folder:
        messagebox.showerror("Error", "Please select a destination folder!")
        return

    try:
        chosen_format = selected_format.get()
        chosen_quality = selected_quality.get()
        height = chosen_quality.replace('p', '')

        ydl_opts = {
            'outtmpl': os.path.join(destination_folder, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'noplaylist': True,
        }

        audio_formats = ['wav', 'mp3', 'm4a', 'aac']

        if chosen_format in audio_formats:
            # Audio-only download
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': chosen_format,
                }],
            })
        else:
            # Video + audio download with enforced quality
            if chosen_format in ['mp4', 'webm']:
                ydl_opts['format'] = (
                    f"bestvideo[height<={height}][ext={chosen_format}]+"
                    f"bestaudio[ext=m4a]/best[height<={height}][ext={chosen_format}]"
                )
                ydl_opts['merge_output_format'] = chosen_format
            else:
                ydl_opts['format'] = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print("Download completed!")
        messagebox.showinfo("Success", f"{chosen_format.upper()} downloaded successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to download: {e}")

def progress_hook(d):
    if d['status'] == 'downloading':
        # Get the number of downloaded and total bytes
        downloaded_bytes = d.get('downloaded_bytes', None)
        total_bytes = d.get('total_bytes', d.get('total_bytes_estimate', None))  # Fallback to total_bytes_estimate
        
        if downloaded_bytes is not None and total_bytes is not None and total_bytes > 0:
            # Calculate progress percentage only if both values are present
            percent = (downloaded_bytes / total_bytes) * 100
            speed = d.get('_speed_str', 'N/A')

            # Schedule the update on the main thread
            root.after(0, update_progress, percent, speed)
        else:
            # Handle the case where total_bytes is None or zero
            root.after(0, update_progress, 0, "Unknown")
                 
def update_progress(percent, speed):
    # Update the progress bar and label
    progress_bar.set(percent / 100)  # Set the progress bar value as a fraction (0.0 to 1.0)
    percent_var.set(f"Downloaded: {int(percent)}%")  # Display the percentage correctly
    speed_var.set(f"Speed: {speed}")
    root.update_idletasks()

def set_destination_folder():
    global destination_folder
    destination_folder = filedialog.askdirectory(title="Set Destination Folder")

    if destination_folder:
        messagebox.showinfo("Success", f"Destination folder set to: {destination_folder}")
    else:
        messagebox.showwarning("Warning", "No folder selected!")

def download_thread_init(url):
    # Show progress elements
    root.after(0, lambda: progress_bar.pack(pady=12, padx=10))
    root.after(0, lambda: download_label.pack(pady=12, padx=10))
    root.after(0, lambda: speed_label.pack(pady=5, padx=10))

    # Start download in thread
    download_thread = threading.Thread(target=download_video, args=(url,))
    download_thread.start()


def load_thumbnail_and_title(url):
    global video_title_label
    try:
        # Setup yt_dlp for metadata extraction
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', 'No Title Found')
            video_id = info_dict.get('id')

        # Update the video title label
        video_title_label.configure(text=title)

        # Construct the thumbnail URL and download the image
        thumb_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        response = requests.get(thumb_url)
        img_data = response.content

        # Open and resize the image
        img = Image.open(BytesIO(img_data))
        img.thumbnail((320, 180))

        # Convert for tkinter
        global thumbnail_image
        thumbnail_image = ImageTk.PhotoImage(img)

        # Display the thumbnail
        thumbnail_label.configure(image=thumbnail_image, text="")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load thumbnail/title: {e}")

def resource_path(relative_path):
    try:
        return os.path.join(sys._MEIPASS, relative_path)
    except Exception:
        return os.path.join(os.path.abspath("."), relative_path)
    
def gui():
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")

    global root, percent_var, speed_var, selected_format, progress_bar, download_label, speed_label
    global thumbnail_label, thumbnail_image, selected_quality, video_title_label

    root = customtkinter.CTk()
    root.geometry("700x700")
    root.title("YouTube Video Downloader")

    # ------------------ ICON SETUP ------------------
    icon_path = resource_path("YouTube.ico")
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
        except Exception:
            try:
                icon = PhotoImage(file=icon_path)
                root.iconphoto(True, icon)
            except Exception as e:
                print(f"Failed to set window icon: {e}")
    # ---------------- END ICON SETUP ----------------

    percent_var = StringVar()
    speed_var = StringVar()
    selected_format = StringVar(value="mp4")
    selected_quality = StringVar(value="1080p")

    label = customtkinter.CTkLabel(master=root, text="YouTube Video Downloader", font=("Roboto", 24))
    label.pack(pady=12, padx=10)

    label = customtkinter.CTkLabel(master=root, text="By Cody Carter", font=("Roboto", 18))
    label.pack(pady=12, padx=10)

    frame = customtkinter.CTkFrame(master=root)
    frame.pack(pady=20, padx=60, fill="both", expand=True)

    global video_title_label
    video_title_label = customtkinter.CTkLabel(master=frame, text="", font=("Roboto", 16))
    video_title_label.pack(pady=5)

    thumbnail_label = customtkinter.CTkLabel(master=frame, text="")
    thumbnail_label.pack(pady=10)

    url_entry = customtkinter.CTkEntry(master=frame, placeholder_text="Enter YouTube URL")
    url_entry.pack(pady=12, padx=10)

    folder_button = customtkinter.CTkButton(master=frame, text="Set Destination Folder", command=set_destination_folder)
    folder_button.pack(pady=12, padx=10)

    progress_bar = customtkinter.CTkProgressBar(master=frame)
    progress_bar.set(0)

    speed_label = customtkinter.CTkLabel(master=frame, textvariable=speed_var, font=("Roboto", 12))
    download_label = customtkinter.CTkLabel(master=frame, textvariable=percent_var, font=("Roboto", 12))

    def start_download():
        url = url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL!")
        else:
            download_thread_init(url)
            load_thumbnail_and_title(url)

    # Combined frame for horizontal alignment
    selection_frame = customtkinter.CTkFrame(master=frame, fg_color="transparent")
    selection_frame.pack(pady=10)

    # Format section inside selection_frame
    format_frame = customtkinter.CTkFrame(master=selection_frame)
    format_frame.pack(side="left", padx=20)

    format_label = customtkinter.CTkLabel(master=format_frame, text="Select Format:", font=("Roboto", 14))
    format_label.pack(pady=5)

    format_options = ['mp4', 'webm', 'wav', 'mp3', 'm4a', 'aac']
    format_choose = customtkinter.CTkOptionMenu(master=format_frame, variable=selected_format, values=format_options)
    format_choose.pack(pady=5)

    # Quality section inside selection_frame
    quality_frame = customtkinter.CTkFrame(master=selection_frame)
    quality_frame.pack(side="left", padx=20)

    quality_label = customtkinter.CTkLabel(master=quality_frame, text="Select Resolution:", font=("Roboto", 14))
    quality_label.pack(pady=5)

    quality_options = ['360p', '480p', '720p', '1080p', '1440p', '2160p']
    quality_choose = customtkinter.CTkOptionMenu(master=quality_frame, variable=selected_quality, values=quality_options)
    quality_choose.pack(pady=5)

    download_button = customtkinter.CTkButton(master=frame, text="Download Media", command=start_download)
    download_button.pack(pady=12, padx=10)

    root.mainloop()


if __name__ == "__main__":
    gui()

