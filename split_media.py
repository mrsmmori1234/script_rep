import os
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
    print("=== Interactive Video & SRT Splitter ===\n")
    
    video_file = input("Enter the MP4 file name (e.g., video.mp4): ").strip()
    
    if not os.path.exists(video_file):
        print(f"Error: Video file '{video_file}' not found.")
    else:
        # 動画ファイル名から拡張子を除いたベース名を取得し、.srt を自動検出する
        base_path, _ = os.path.splitext(video_file)
        srt_file = base_path + ".srt"

        if os.path.exists(srt_file):
            print(f"Detected SRT file: {srt_file}")
        else:
            print("Notice: No matching SRT file found. Only the video will be split.")
            srt_file = None

        while True:
            try:
                user_input = input("How many parts do you want to split it into?: ")
                num_splits = int(user_input)
                if num_splits > 1:
                    break
                else:
                    print("Please enter a number greater than 1.")
            except ValueError:
                print("Invalid input. Please enter a valid whole number.")
        
        split_mp4_and_srt(video_file, srt_file, num_splits)