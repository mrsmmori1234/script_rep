import os
import random
import sys
import json
import xml.etree.ElementTree as ET
import subprocess
import tempfile
from collections import Counter
from datetime import datetime as dt


def get_output_prefix(target_dir):
    """ターゲットディレクトリのパスから、適切な出力ファイル名用のプレフィックスを取得する。"""
    normalized_path = os.path.normpath(target_dir)
    folder_name = os.path.basename(normalized_path)

    if folder_name.lower() == "shorts":
        parent_dir = os.path.dirname(normalized_path)
        return os.path.basename(parent_dir)

    return folder_name


def get_video_specs(file_path):
    """ffprobeを使って動画の(width, height, v_codec, a_codec)を取得する"""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "stream=index,codec_type,codec_name,width,height",
        "-of", "json",
        file_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        v_codec = None
        a_codec = None
        width = None
        height = None

        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video" and not v_codec:
                v_codec = stream.get("codec_name")
                width = stream.get("width")
                height = stream.get("height")
            elif stream.get("codec_type") == "audio" and not a_codec:
                a_codec = stream.get("codec_name")

        if width and height and v_codec:
            return (width, height, v_codec, a_codec or "none")
        return None
    except Exception:
        return None


def generate_mp4(target_dir, output_dir="/mnt/d/Youtube"):
    """
    大量のファイルを安全かつ高速に結合する方式。
    1. 各動画を同一規格（30fps, 44.1kHz, 音声同期補正）に標準化して一時フォルダに保存 (.mp4)
    2. concat demuxer で全ファイルを無劣化・超高速結合 (DTSズレ完全防止)
    """
    if not os.path.isdir(target_dir):
        print(f"Error: Directory '{target_dir}' not found.")
        return None

    all_files = [f for f in sorted(os.listdir(target_dir)) if f.lower().endswith(".mp4")]
    if not all_files:
        print("No .mp4 files found in the directory.")
        return None

    print(f"Checking video specs for {len(all_files)} files...")

    file_spec_map = {}
    spec_list = []
    for f in all_files:
        path = os.path.abspath(os.path.join(target_dir, f))
        spec = get_video_specs(path)
        if spec:
            file_spec_map[f] = spec
            spec_list.append(spec)

    if not spec_list:
        print("❌ No valid video files could be read.")
        return None

    # 最も多い解像度を取得
    target_spec, count = Counter(spec_list).most_common(1)[0]
    w, h, _, _ = target_spec
    print(f"Target Resolution: {w}x{h} (Found {count} matching files)")

    # 解像度が一致するファイルのみ選択
    valid_files = [f for f in all_files if file_spec_map.get(f) and file_spec_map[f][0] == w and file_spec_map[f][1] == h]

    # シャッフル処理
    rng = random.SystemRandom()
    rng.shuffle(valid_files)
    rng.shuffle(valid_files)

    prefix = get_output_prefix(target_dir)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{prefix}.mp4")

    print(f"\nProcessing {len(valid_files)} videos in temporary storage...")

    # 一時ディレクトリの作成
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_mp4_files = []

        # Step 1: 各ファイルを標準化 (.mp4形式で各パーツのPTS/DTSを完全にゼロリセット)
        for idx, f in enumerate(valid_files):
            input_path = os.path.abspath(os.path.join(target_dir, f))
            temp_output = os.path.join(temp_dir, f"part_{idx:05d}.mp4")

            cmd_norm = [
                "ffmpeg", "-y", "-loglevel", "error",
                "-i", input_path,
                "-vf", "fps=30,settb=AVTB",
                "-af", "aresample=44100:async=1:first_pts=0,aformat=sample_fmts=fltp:channel_layouts=stereo,asettb=AVTB",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23", "-g", "30", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k",
                "-avoid_negative_ts", "make_zero",
                temp_output
            ]

            try:
                subprocess.run(cmd_norm, check=True)
                temp_mp4_files.append(temp_output)
                print(f"[{idx + 1}/{len(valid_files)}] Normalized: {f}", end="\r")
            except subprocess.CalledProcessError:
                print(f"\n⚠️ Skipping problematic file: {f}")

        if not temp_mp4_files:
            print("\n❌ Failed to process any videos.")
            return None

        # Step 2: Concat リストを作成
        concat_list_path = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_list_path, "w", encoding="utf-8") as file_list:
            for mp4_file in temp_mp4_files:
                file_list.write(f"file '{mp4_file}'\n")

        print(f"\n\nConcatenating normalized clips into final MP4...")

        # Step 3: Concat Demuxer で結合 (-segment_time_metadata でストリームタイムスタンプを強制接続)
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-segment_time_metadata", "1",
            "-i", concat_list_path,
            "-c", "copy",
            "-movflags", "+faststart",
            output_path
        ]

        try:
            subprocess.run(ffmpeg_cmd, check=True)
            print(f"\n✅ Successfully created 100% clean MP4: {os.path.abspath(output_path)}")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"\n❌ An error occurred during final concatenation: {e}")
            return None


def generate_xspf(target_dir, output_dir="/mnt/d/Youtube"):
    if not os.path.isdir(target_dir):
        print(f"Error: Directory '{target_dir}' not found.")
        return None

    media_files = [f for f in sorted(os.listdir(target_dir)) if f.lower().endswith((".mp3", ".mp4"))]
    if not media_files:
        print("No .mp3 or .mp4 files found in the directory.")
        return None

    playlist = ET.Element("playlist", version="1", xmlns="http://xspf.org/ns/0/")
    trackList = ET.SubElement(playlist, "trackList")

    for filename in media_files:
        file_path = os.path.join(target_dir, filename)
        track = ET.SubElement(trackList, "track")
        location = ET.SubElement(track, "location")
        location.text = f"file:///{file_path.replace(os.sep, '/')}"
        title = ET.SubElement(track, "title")
        title.text = filename

    date_str = dt.now().strftime("%Y%m%d_%H%M")
    prefix = get_output_prefix(target_dir)
    output_path = os.path.join(output_dir, f"{prefix}_{date_str}.xspf")

    os.makedirs(output_dir, exist_ok=True)
    tree = ET.ElementTree(playlist)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

    print(f"\nSuccessfully created XSPF: {os.path.abspath(output_path)}")
    return output_path


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    elif isinstance(argv, str):
        argv = [argv]

    if len(argv) < 1:
        print("Usage: python make_mp4.py [directory_path]")
        return 1

    generate_mp4(argv[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
