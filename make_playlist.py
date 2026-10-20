#!/usr/bin/env python3
import argparse
import os
import random
import sys
import urllib.parse
import xml.etree.ElementTree as ET

# 無視するフォルダ名（大文字小文字無視）
IGNORE_DIRS = {"old", "archive"}


def get_target_media_files(folder_path):
    """指定されたフォルダの直下にある .mp3, .mp4 ファイルを取得する（再帰的に潜らない）"""
    media_files = []
    try:
        for f in os.listdir(folder_path):
            if f.lower().endswith((".mp3", ".mp4")):
                full_path = os.path.join(folder_path, f)
                if os.path.isfile(full_path):
                    media_files.append(full_path)
    except OSError:
        pass
    return media_files


def generate_playlist_for_category(category_dir, output_dir="/mnt/d/Youtube", shuffle=False):
    """
    /mnt/d/Youtube/フォルダ名 に対して、
    - フォルダ名直下の .mp3/.mp4
    - フォルダ名/Shorts 直下の .mp3/.mp4
    を集めて 「フォルダ名.xspf」 を作成する
    """
    abs_category = os.path.abspath(category_dir)
    folder_name = os.path.basename(abs_category)

    # フォルダ名が ignore 対象ならスキップ
    if folder_name.lower() in IGNORE_DIRS:
        return None

    all_media_files = []

    # 1. フォルダ名直下のファイルを集める
    all_media_files.extend(get_target_media_files(abs_category))

    # 2. Shorts フォルダ直下のファイルがあれば集める（Shortsフォルダ自体が ignore 対象でない場合）
    shorts_dir = os.path.join(abs_category, "Shorts")
    if os.path.isdir(shorts_dir):
        all_media_files.extend(get_target_media_files(shorts_dir))

    # 重複排除とソート
    all_media_files = sorted(list(set(all_media_files)))

    if not all_media_files:
        print(f"スキップ: '{folder_name}' に対象ファイルがありません")
        return None

    if shuffle:
        rng = random.SystemRandom()
        rng.shuffle(all_media_files)

    # XML (XSPF) の構築
    playlist = ET.Element("playlist", version="1", xmlns="http://xspf.org/ns/0/")
    playlist.set("xmlns:vlc", "http://www.videolan.org/vlc/playlist/ns/0/")

    ET.SubElement(playlist, "title").text = folder_name
    track_list = ET.SubElement(playlist, "trackList")
    extension = ET.SubElement(playlist, "extension", application="http://www.videolan.org/vlc/playlist/0")

    for i, full_path in enumerate(all_media_files):
        filename = os.path.basename(full_path)

        if full_path.startswith("/mnt/"):
            parts = full_path.split("/")
            drive = parts[2].upper()
            win_path = f"{drive}:/" + "/".join(parts[3:])
            loc_text = "file:///" + urllib.parse.quote(win_path, safe=":/")
        else:
            loc_text = "file://" + urllib.parse.quote(full_path)

        track = ET.SubElement(track_list, "track")
        ET.SubElement(track, "location").text = loc_text
        ET.SubElement(track, "title").text = filename

        track_ext = ET.SubElement(track, "extension", application="http://www.videolan.org/vlc/playlist/0")
        ET.SubElement(track_ext, "vlc:id").text = str(i)
        ET.SubElement(extension, "vlc:item", tid=str(i))

    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(output_dir, f"{folder_name}.xspf")

    tree = ET.ElementTree(playlist)
    ET.indent(tree, space="    ")

    try:
        tree.write(output_filename, encoding="utf-8", xml_declaration=True)
        print(f"作成完了: {folder_name}.xspf ({len(all_media_files)}曲)")
        return output_filename
    except IOError:
        print(f"エラー: {output_filename} の書き込みに失敗しました。")
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate XSPF playlists for category folders including their Shorts.")
    parser.add_argument("directory", help="The root directory containing category folders (e.g., /mnt/d/Youtube).")
    parser.add_argument("-r", "--random", action="store_true", help="Shuffle the playlist order.")
    parser.add_argument("-o", "--output", default="/mnt/d/Youtube", help="Output directory for xspf files.")

    args = parser.parse_args(argv)
    root_dir = os.path.abspath(args.directory)

    if not os.path.isdir(root_dir):
        print(f"エラー: {root_dir} は有効なディレクトリではありません。")
        return 1

    print(f"=== プレイリスト作成開始: {root_dir} ===")

    success_count = 0
    folder_count = 0

    # ルートディレクトリ直下のフォルダ（例: Mind_fullness など）だけを対象にする
    try:
        entries = sorted(os.listdir(root_dir))
    except OSError as e:
        print(f"エラー: ディレクトリを読み込めません: {e}")
        return 1

    for entry in entries:
        sub_path = os.path.join(root_dir, entry)
        
        # ディレクトリであり、かつ old / archive でなければ処理対象とする
        if os.path.isdir(sub_path):
            if entry.lower() in IGNORE_DIRS:
                continue

            folder_count += 1
            res = generate_playlist_for_category(sub_path, output_dir=args.output, shuffle=args.random)
            if res:
                success_count += 1

    print(f"\n=== 処理完了: 対象フォルダ数 {folder_count} / 作成プレイリスト数 {success_count} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
