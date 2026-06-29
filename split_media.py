import glob
import os
import subprocess
import sys



def find_matching_srt(video_path):
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    directory = os.path.dirname(video_path) or "."

    for filename in os.listdir(directory):
        if filename.startswith(base_name) and filename.lower().endswith(".srt"):
            return os.path.join(directory, filename)
    return None


def expand_video_patterns(input_patterns):
    video_files = []
    for pattern in input_patterns:
        matched = glob.glob(pattern)
        if matched:
            video_files.extend(matched)
        else:
            video_files.append(pattern)
    return video_files


def split_mp4_and_srt(video_path, srt_path=None, num_splits=2):
    from moviepy.video.io.VideoFileClip import VideoFileClip
    import pysrt

    video = VideoFileClip(video_path)
    total_duration = video.duration
    split_duration = total_duration / num_splits
    video.close()

    subs = pysrt.open(srt_path, encoding="utf-8") if srt_path and os.path.exists(srt_path) else None
    base_name, _ = os.path.splitext(video_path)
    created_files = []

    for i in range(num_splits):
        start_time = i * split_duration
        end_time = (i + 1) * split_duration if i < num_splits - 1 else total_duration
        duration_to_cut = end_time - start_time
        part_num = i + 1

        print(f"\n--- Processing Part {part_num}/{num_splits} ({start_time:.2f}s - {end_time:.2f}s) ---")

        output_video_path = f"{base_name}_part{part_num}.mp4"
        print(f"Exporting video: {output_video_path}")

        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(start_time),
            "-i",
            video_path,
            "-t",
            str(duration_to_cut),
            "-c",
            "copy",
            "-loglevel",
            "error",
            output_video_path,
        ]
        subprocess.run(ffmpeg_cmd, check=True)
        created_files.append(output_video_path)

        if subs:
            output_srt_path = f"{base_name}_part{part_num}.srt"
            start_srt_time = pysrt.SubRipTime(milliseconds=int(start_time * 1000))
            end_srt_time = pysrt.SubRipTime(milliseconds=int(end_time * 1000))
            part_subs = subs.slice(starts_after=start_srt_time, ends_before=end_srt_time)

            for sub in part_subs:
                sub.start -= start_srt_time
                sub.end -= start_srt_time

            print(f"Saving subtitles: {output_srt_path}")
            part_subs.save(output_srt_path, encoding="utf-8")
            created_files.append(output_srt_path)

    print("\n==========================================")
    print("Success! All files have been split and saved.")
    print("==========================================")
    return created_files


def split_media_files(video_files, num_splits, detect_srt=True):
    created_files = []
    for video_file in video_files:
        if not os.path.exists(video_file):
            print(f"Skipping: {video_file} (File not found)")
            continue

        srt_file = find_matching_srt(video_file) if detect_srt else None
        print(f"\n>>> Starting process for: {video_file}")
        if srt_file:
            print(f"Detected SRT: {srt_file}")

        created_files.extend(split_mp4_and_srt(video_file, srt_file, num_splits))
    return created_files


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv

    if len(argv) < 1:
        print("Usage: python split_media.py <video_file> [num_splits]")
        print("Example: python split_media.py 'video.mp4' 3")
        return 1

    last_arg = argv[-1]
    if last_arg.isdigit() and not os.path.exists(last_arg):
        num_splits_arg = int(last_arg)
        input_patterns = argv[:-1]
    else:
        num_splits_arg = None
        input_patterns = argv

    video_files = expand_video_patterns(input_patterns)
    if not video_files:
        print("Error: No valid video files found.")
        return 1

    if num_splits_arg is None:
        while True:
            try:
                user_input = input(f"Found {len(video_files)} files. How many parts do you want to split them into?: ")
                num_splits = int(user_input)
                if num_splits > 1:
                    break
                print("Please enter a number greater than 1.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
    else:
        num_splits = num_splits_arg

    split_media_files(video_files, num_splits)
    return 0


if __name__ == "__main__":
    sys.exit(main())