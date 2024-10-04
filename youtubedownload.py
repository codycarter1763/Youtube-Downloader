import yt_dlp
import customtkinter 
from tkinter import filedialog, messagebox, StringVar
import os

def list_formats(url):
    try:
        ydl_opts = {
            'quiet': True,  # Suppress output
            'format': 'best',  # Just to ensure it extracts information without download
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', None)
            if formats:
                format_list = "Available formats:\n"
                for f in formats:
                    format_list += f"Format ID: {f['format_id']}, Extension: {f['ext']}, Quality: {f['quality']}, Size: {f.get('filesize', 'unknown')} bytes\n"
                messagebox.showinfo("Available Formats", format_list)
            else:
                messagebox.showwarning("Warning", "No formats available.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to list formats: {e}")

def download_video(url):
    global destination_folder
    if not destination_folder:
        messagebox.showerror("Error", "Please select a destination folder!")
        return
    
    try:
        ydl_opts = {
            'format': 'best',  
            'outtmpl': os.path.join(destination_folder, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Download completed!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download video: {e}")

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', 'N/A')
        total_bytes = d.get('total_bytes_estimate', 'N/A')
        speed = d.get('_speed_str', 'N/A')

        percent_var.set(f"Downloaded: {percent}")
        progress_var.set(f"Speed: {speed}, Total: {total_bytes} bytes")
        print(f"Downloading: {percent} of {total_bytes} bytes at {speed}")

def set_destination_folder():
    global destination_folder
    destination_folder = filedialog.askdirectory(title="Set Destination Folder")

    if destination_folder:
        messagebox.showinfo("Success", f"Destination folder set to: {destination_folder}")
    else:
        messagebox.showwarning("Warning", "No folder selected!")
    
def gui():
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")

    root = customtkinter.CTk()
    root.geometry("500x350")
    root.title("Youtube Video Downloader")

    global percent_var, progress_var
    percent_var = StringVar()
    progress_var = StringVar()

    label = customtkinter.CTkLabel(master=root, text="Youtube Video Downloader", font=("Roboto", 24))
    label.pack(pady=12, padx=10)

    frame = customtkinter.CTkFrame(master=root)
    frame.pack(pady=20, padx=60, fill="both", expand=True)

    #Entry for URL
    url_entry = customtkinter.CTkEntry(master=frame, placeholder_text="Enter YouTube URL")
    url_entry.pack(pady=12, padx=10)

    #Button for destination folder
    folder_button = customtkinter.CTkButton(master=frame, text="Set Destination Folder", command=set_destination_folder)
    folder_button.pack(pady=12, padx=10)

    download_button = customtkinter.CTkLabel(master=frame, textvariable=percent_var, font=("Roboto", 12))
    download_button.pack(pady=12, padx=10)

    speed_label = customtkinter.CTkLabel(master=frame, textvariable=progress_var, font=("Roboto", 12))
    speed_label.pack(pady=5, padx=10)
    
    def start_download():
        url = url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL!")
        else:
            download_video(url)

    download_button = customtkinter.CTkButton(master=frame, text="Download Video", command=start_download)
    download_button.pack(pady=12, padx=10)
    
    mode_checkbox = customtkinter.CTkCheckBox(master=frame, text="Switch to Light Mode")
    mode_checkbox.pack(pady=12, padx=10)

    def toggle_mode():
        if mode_checkbox.get():  # If checked
            customtkinter.set_appearance_mode("dark")
            mode_checkbox.configure(text="Switch to Light Mode")  # Update checkbox text
        else:  # If unchecked
            customtkinter.set_appearance_mode("light")
            mode_checkbox.configure(text="Switch to Dark Mode")  # Update checkbox text

    # Bind checkbox toggle function to checkbox click
    mode_checkbox.configure(command=toggle_mode)
    root.mainloop()

if __name__ == "__main__":
    gui()
    
