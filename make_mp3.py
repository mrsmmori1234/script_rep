import os
import sys
import datetime
import random
try:
    from moviepy.editor import AudioFileClip, concatenate_audioclips
except ImportError:
    from moviepy import AudioFileClip, concatenate_audioclips

def combine_audio_files(target_dir):
    # 1. Check directory
    if not os.path.isdir(target_dir):
        print(f"Error: Directory '{target_dir}' not found.")
        return

    # 2. Get list of .mp3 and .mp4 files (alphabetical order)
    media_files = [f for f in sorted(os.listdir(target_dir)) if f.lower().endswith(('.mp3', '.mp4'))]

    if not media_files:
        print("No .mp3 or .mp4 files found in the directory.")
        return

    # Use OS-level random number generator and shuffle twice for high randomness
    rng = random.SystemRandom()
    rng.shuffle(media_files)
    rng.shuffle(media_files)

    print(f"Found {len(media_files)} files. Processing...")

    clips = []
    final_audio = None
    try:
        for filename in media_files:
            file_path = os.path.join(target_dir, filename)
            # Load as audio clip (extracts audio from mp4)
            clip = AudioFileClip(file_path)
            clips.append(clip)

        if clips:
            # 3. Concatenate clips
            final_audio = concatenate_audioclips(clips)

            # 4. Write as mp3
            date_str = datetime.date.today().strftime("%Y%m%d")
            target_folder_name = os.path.basename(os.path.normpath(target_dir))
            output_filename = f"/mnt/d/Youtube/{target_folder_name}_{date_str}.mp3"
            output_path = output_filename  # Output to current directory
            final_audio.write_audiofile(output_path)
            print(f"\nSuccessfully created: {os.path.abspath(output_path)}")

    except Exception as e:
        print(f"\nAn error occurred: {e}")

    finally:
        # メモリ解放
        for clip in clips:
            clip.close()
        if final_audio:
            final_audio.close()

if __name__ == "__main__":
    # Jupyter上のセルで実行する場合は、引数の代わりにパスを直接指定も可能
    # 例: combine_audio_files("./my_audio_folder")
    if len(sys.argv) < 2:
        print("Usage: python script.py [directory_path]")
    else:
        combine_audio_files(sys.argv[1])
