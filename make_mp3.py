import os
import random
import sys
from datetime import datetime as dt


def combine_audio_files(target_dir, output_dir="/mnt/d/Youtube"):
    try:
        from moviepy.editor import AudioFileClip, concatenate_audioclips
    except ImportError:
        from moviepy import AudioFileClip, concatenate_audioclips

    if not os.path.isdir(target_dir):
        print(f"Error: Directory '{target_dir}' not found.")
        return None

    media_files = [f for f in sorted(os.listdir(target_dir)) if f.lower().endswith((".mp3", ".mp4"))]
    if not media_files:
        print("No .mp3 or .mp4 files found in the directory.")
        return None

    rng = random.SystemRandom()
    rng.shuffle(media_files)
    rng.shuffle(media_files)

    print(f"Found {len(media_files)} files. Processing...")

    clips = []
    final_audio = None
    try:
        for filename in media_files:
            file_path = os.path.join(target_dir, filename)
            clip = AudioFileClip(file_path)
            clips.append(clip)

        final_audio = concatenate_audioclips(clips)
        
        # 時刻(HHMM)まで取得するように修正
        date_str = dt.now().strftime("%Y%m%d_%H%M")
        
        target_folder_name = os.path.basename(os.path.normpath(target_dir))
        output_path = os.path.join(output_dir, f"{target_folder_name}_{date_str}.mp3")
        final_audio.write_audiofile(output_path)
        print(f"\nSuccessfully created: {os.path.abspath(output_path)}")
        return output_path

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        return None

    finally:
        for clip in clips:
            clip.close()
        if final_audio:
            final_audio.close()


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv

    if len(argv) < 1:
        print("Usage: python make_mp3.py [directory_path]")
        return 1

    combine_audio_files(argv[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
