import os
import random
import sys
import xml.etree.ElementTree as ET
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


def generate_mp4(target_dir, output_dir="/mnt/d/Youtube", segment_time=3600):
    """
    ffmpegのconcat機能とsegment機能を組み合わせ、
    メモリを消費せずに指定時間（デフォルト3600秒＝1時間）ごとに分割してMP4を出力する関数
    """
    if not os.path.isdir(target_dir):
        print(f"Error: Directory '{target_dir}' not found.")
        return None

    media_files = [f for f in sorted(os.listdir(target_dir)) if f.lower().endswith(".mp4")]
    if not media_files:
        print("No .mp4 files found in the directory.")
        return None

    # シャッフル処理
    rng = random.SystemRandom()
    rng.shuffle(media_files)
    rng.shuffle(media_files)

    print(f"Found {len(media_files)} MP4 files. Concatenating and segmenting ({segment_time}s each) with ffmpeg...")

    prefix = get_output_prefix(target_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # 出力ファイル名のパターン（例: MontaEnglish_part001.mp4, MontaEnglish_part002.mp4）
    output_pattern = os.path.join(output_dir, f"{prefix}_part%03d.mp4")

    # 一時テキストファイルを作成して結合リストを書き込む
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        list_file_path = f.name
        for filename in media_files:
            file_path = os.path.abspath(os.path.join(target_dir, filename))
            # シングルクォーテーションのエスケープ処理
            escaped_path = file_path.replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")

    try:
        # ffmpegを無再劣化・超高速・低メモリモード（-c copy）かつ分割出力（segment）で実行
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-fflags", "+genpts",                  # タイムスタンプを修正して再生ズレを予防
            "-f", "concat",
            "-safe", "0",
            "-i", list_file_path,
            "-c", "copy",
            "-avoid_negative_ts", "make_zero",     # タイムスタンプの基準を0に揃える
            "-f", "segment",                        # セグメント分割機能を使用
            "-segment_time", str(segment_time),    # 分割する秒数（例: 3600）
            "-reset_timestamps", "1",               # 各パーツの時間を0秒スタートにリセット
            output_pattern
        ]

        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error executing ffmpeg:\n{result.stderr}")
            return None

        print(f"\nSuccessfully created segmented MP4 files in: {os.path.abspath(output_dir)}")
        print(f"File pattern: {prefix}_part001.mp4, {prefix}_part002.mp4 ...")
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
        print("Usage: python make_mp4.py [directory_path]")
        return 1

    generate_mp4(argv[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
