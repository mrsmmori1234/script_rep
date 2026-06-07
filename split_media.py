import os
import sys
import subprocess
from moviepy.video.io.VideoFileClip import VideoFileClip
import pysrt
import glob

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

    # --- 引数の解析 ---
    # 最後の引数が数値（かつファイルとして存在しない）なら分割数とみなす
    last_arg = sys.argv[-1]
    if last_arg.isdigit() and not os.path.exists(last_arg):
        num_splits_arg = int(last_arg)
        input_patterns = sys.argv[1:-1]
    else:
        num_splits_arg = None
        input_patterns = sys.argv[1:]

    # ワイルドカードの展開（念のためglobを使用）
    video_files = []
    for pattern in input_patterns:
        matched = glob.glob(pattern)
        if matched:
            video_files.extend(matched)
        else:
            video_files.append(pattern)

    if not video_files:
        print("Error: No valid video files found.")
        sys.exit(1)

    # 分割数が指定されていない場合は一度だけ質問する
    if num_splits_arg is None:
        while True:
            try:
                user_input = input(f"Found {len(video_files)} files. How many parts do you want to split them into?: ")
                num_splits = int(user_input)
                if num_splits > 1:
                    break
                else:
                    print("Please enter a number greater than 1.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
    else:
        num_splits = num_splits_arg

    # --- 各ファイルを順番に処理 ---
    for video_file in video_files:
        if not os.path.exists(video_file):
            print(f"Skipping: {video_file} (File not found)")
            continue

        # SRTファイルの自動検出
        base_name = os.path.splitext(os.path.basename(video_file))[0]
        directory = os.path.dirname(video_file) or "."
        
        srt_file = None
        for f in os.listdir(directory):
            if f.startswith(base_name) and f.lower().endswith(".srt"):
                srt_file = os.path.join(directory, f)
                break

        print(f"\n>>> Starting process for: {video_file}")
        if srt_file:
            print(f"Detected SRT: {srt_file}")
        
        split_mp4_and_srt(video_file, srt_file, num_splits)