import os
import sys
import subprocess
from moviepy.video.io.VideoFileClip import VideoFileClip
import pysrt

def split_mp4_and_srt(video_path, srt_path, num_splits):
    # 1. Load video via MoviePy just to get the accurate duration
    video = VideoFileClip(video_path)
    total_duration = video.duration  # in seconds
    split_duration = total_duration / num_splits
    video.close() # Close it immediately to free the file lock
    
    # 2. Load subtitles
    subs = pysrt.open(srt_path, encoding='utf-8') if srt_path and os.path.exists(srt_path) else None
    
    base_name, _ = os.path.splitext(video_path)
    
    for i in range(num_splits):
        start_time = i * split_duration
        end_time = (i + 1) * split_duration if i < num_splits - 1 else total_duration
        duration_to_cut = end_time - start_time
        
        part_num = i + 1
        print(f"\n--- Processing Part {part_num}/{num_splits} ({start_time:.2f}s - {end_time:.2f}s) ---")
        
        # --- Video Splitting (Using Lightning-Fast FFmpeg Stream Copy) ---
        output_video_path = f"{base_name}_part{part_num}.mp4"
        print(f"Exporting video: {output_video_path}")
        
        # ffmpeg -ss [start] -i [input] -t [duration] -c copy [output]
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',                # Overwrite output files without asking
            '-ss', str(start_time),
            '-i', video_path,
            '-t', str(duration_to_cut),
            '-c', 'copy',        # Stream copy video and audio (No re-encoding!)
            '-loglevel', 'error', # Keep the terminal clean
            output_video_path
        ]
        
        # Execute the fast cut
        subprocess.run(ffmpeg_cmd, check=True)
        
        # --- Subtitle Splitting and Time Shifting ---
        if subs:
            output_srt_path = f"{base_name}_part{part_num}.srt"
            
            start_srt_time = pysrt.SubRipTime(milliseconds=int(start_time * 1000))
            end_srt_time = pysrt.SubRipTime(milliseconds=int(end_time * 1000))
            
            part_subs = subs.slice(starts_after=start_srt_time, ends_before=end_srt_time)
            
            for sub in part_subs:
                sub.start -= start_srt_time
                sub.end -= start_srt_time
                
            print(f"Saving subtitles: {output_srt_path}")
            part_subs.save(output_srt_path, encoding='utf-8')
        
    print("\n==========================================")
    print("Success! All files have been split and saved.")
    print("==========================================")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python split_media.py <video_file> [num_splits]")
        print("Example: python split_media.py 'video.mp4' 3")
        sys.exit(1)

    video_file = sys.argv[1]

    if not os.path.exists(video_file):
        print(f"Error: Video file '{video_file}' not found.")
        sys.exit(1)

    # --- SRTファイルの高度な自動検出 ---
    # Get the base name of the video (without extension)
    base_name = os.path.splitext(os.path.basename(video_file))[0]
    directory = os.path.dirname(video_file) or "."
    
    srt_file = None
    # Search directory for a file starting with the base name and ending in .srt
    for f in os.listdir(directory):
        if f.startswith(base_name) and f.lower().endswith(".srt"):
            srt_file = os.path.join(directory, f)
            break

    if srt_file:
        print(f"Detected SRT file: {srt_file}")
    else:
        print("Notice: No matching SRT file found. Only the video will be split.")

    # Get the number of splits (use 2nd argument if provided, otherwise prompt)
    if len(sys.argv) >= 3:
        try:
            num_splits = int(sys.argv[2])
        except ValueError:
            print("Error: num_splits must be a number.")
            sys.exit(1)
    else:
        while True:
            try:
                user_input = input("How many parts do you want to split it into?: ")
                num_splits = int(user_input)
                if num_splits > 1:
                    break
                else:
                    print("Please enter a number greater than 1.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    split_mp4_and_srt(video_file, srt_file, num_splits)