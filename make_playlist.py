import os
import random
import sys
import subprocess
import tempfile
from datetime import datetime as dt


def get_output_prefix(target_dir):
    """ターゲットディレクトリのパスから、適切な出力ファイル名用のプレフィックスを取得する。"""
    normalized_path = os.path.normpath(target_dir)
    folder_name = os.path.basename(normalized_path)

    if folder_name.lower() == "shorts":
        parent_dir = os.path.dirname(normalized_path)
        return os.path.basename(parent_dir)

    return folder_name


def generate_media(target_dir, output_dir="/mnt/d/Youtube", ext=".mp4"):
    """
    指定したディレクトリ（およびサブディレクトリ）から指定された拡張子のファイルを
    再帰的に探索してシャッフル・結合し、1つのファイルとして出力する関数
    """
    ext = ext.lower()
    if not ext.startswith("."):
        ext = "." + ext

    if not os.path.isdir(target_dir):
        print(f"Error: Directory '{target_dir}' not found.")
        return None

    # os.walk を使ってサブディレクトリも含めてファイルを再帰的に収集する
    media_files = []
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith(ext):
                full_path = os.path.abspath(os.path.join(root, file))
                media_files.append(full_path)

    if not media_files:
        print(f"No {ext} files found in the directory or subdirectories.")
        return None

    # シャッフル処理
    rng = random.SystemRandom()
    rng.shuffle(media_files)
    rng.shuffle(media_files)

    print(f"Found {len(media_files)} {ext} files (including subdirectories). Concatenating into a single file with ffmpeg...")

    prefix = get_output_prefix(target_dir)
    os.makedirs(output_dir, exist_ok=True)

    # 出力ファイル名を1つのファイル用に固定（例: Alfred Cortot.mp3）
    output_file_path = os.path.join(output_dir, f"{prefix}{ext}")

    # 一時テキストファイルを作成して結合リストを書き込む
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        list_file_path = f.name
        for file_path in media_files:
            escaped_path = file_path.replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")

    try:
        # 拡張子に応じたffmpegコマンド（分割せず1つに出力）
        if ext == ".mp3":
            ffmpeg_cmd = [
                "ffmpeg",
                "-y",
                "-fflags", "+genpts",
                "-f", "concat",
                "-safe", "0",
                "-i", list_file_path,
                "-vn",                           # 映像ストリームを無視（音声のみ）
                "-c:a", "copy",                  # 再エンコードなしで高速コピー
                "-avoid_negative_ts", "make_zero",
                output_file_path
            ]
        else:
            ffmpeg_cmd = [
                "ffmpeg",
                "-y",
                "-fflags", "+genpts",
                "-f", "concat",
                "-safe", "0",
                "-i", list_file_path,
                "-c", "copy",
                "-avoid_negative_ts", "make_zero",
                output_file_path
            ]

        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error executing ffmpeg:\n{result.stderr}")
            return None

        print(f"\nSuccessfully created single {ext.upper()} file: {output_file_path}")
        return output_dir

    except subprocess.CalledProcessError as e:
        print(f"\nAn error occurred during ffmpeg execution: {e}")
        return None
    finally:
        # 一時ファイルの削除
        if os.path.exists(list_file_path):
            os.remove(list_file_path)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv

    if len(argv) < 1:
        print("Usage: python make_playlist.py [directory_path] [ext: .mp4 or .mp3]")
        print("Example (MP3): python make_playlist.py /mnt/d/Music/Alfred\\ Cortot .mp3")
        return 1

    target_dir = argv[0]
    ext = argv[1] if len(argv) > 1 else ".mp4"

    generate_media(target_dir, ext=ext)
    return 0


if __name__ == "__main__":
    sys.exit(main())
