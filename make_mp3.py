import os
import sys
import datetime
try:
    from moviepy.editor import AudioFileClip, concatenate_audioclips
except ImportError:
    from moviepy import AudioFileClip, concatenate_audioclips

def combine_audio_files(target_dir):
    # 1. ディレクトリの確認
    if not os.path.isdir(target_dir):
        print(f"Error: Directory '{target_dir}' not found.")
        return

    # 2. .mp3 と .mp4 ファイルの一覧を取得（アルファベット順）
    media_files = [f for f in sorted(os.listdir(target_dir)) if f.lower().endswith(('.mp3', '.mp4'))]

    if not media_files:
        print("No .mp3 or .mp4 files found in the directory.")
        return

    print(f"Found {len(media_files)} files. Processing...")

    clips = []
    final_audio = None
    try:
        for filename in media_files:
            file_path = os.path.join(target_dir, filename)
            # オーディオファイルとして読み込む (mp4の場合は音声部分が抽出される)
            clip = AudioFileClip(file_path)
            clips.append(clip)

        if clips:
            # 3. 音声を結合
            final_audio = concatenate_audioclips(clips)

            # 4. mp3として書き出し
            date_str = datetime.date.today().strftime("%Y%m%d")
            target_folder_name = os.path.basename(os.path.normpath(target_dir))
            output_filename = f"{target_folder_name}_{date_str}.mp3"
            output_path = output_filename  # カレントディレクトリに出力
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