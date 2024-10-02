import yt_dlp

def download_video(url):
    try:
        ydl_opts = {
            'format': 'best',  # Download the best available quality
            'progress_hooks': [progress_hook],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Download completed!")
    except Exception as e:
        print(f"Error: {e}")

def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"Downloading: {d['_percent_str']} of {d['total_bytes_estimate']} bytes at {d['_speed_str']}")

if __name__ == "__main__":
    video_url = input("Enter the YouTube video URL: ")
    download_video(video_url)