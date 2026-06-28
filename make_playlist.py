#!/usr/bin/env python3
import os
import sys
import xml.etree.ElementTree as ET
import urllib.parse
import random
import argparse

def generate_xspf(target_dir, shuffle=False):
    # 絶対パスを取得
    abs_target = os.path.abspath(target_dir)

    if not os.path.isdir(abs_target):
        print(f"Error: {abs_target} is not a directory.")
        return

    media_files = [f for f in sorted(os.listdir(abs_target)) if f.lower().endswith(('.mp3', '.mp4'))]

    if not media_files:
        print("No media files found.")
        return

    if shuffle:
        # Pythonのシャッフルはこれで完璧です
        rng = random.SystemRandom()
        rng.shuffle(media_files)

    # XMLの構築（VLC用の名前空間を追加）
    playlist = ET.Element("playlist", version="1", xmlns="http://xspf.org/ns/0/")
    playlist.set("xmlns:vlc", "http://www.videolan.org/vlc/playlist/ns/0/")
    
    ET.SubElement(playlist, "title").text = os.path.basename(os.path.normpath(abs_target))
    trackList = ET.SubElement(playlist, "trackList")

    # VLC用の拡張プレイリストノードを作成
    extension = ET.SubElement(playlist, "extension", application="http://www.videolan.org/vlc/playlist/0")

    for i, f in enumerate(media_files):
        full_path = os.path.join(abs_target, f)

        # --- Convert WSL path (/mnt/x/...) to Windows path (X:/...) ---
        if full_path.startswith('/mnt/'):
            parts = full_path.split('/')
            drive = parts[2].upper()
            win_path = f"{drive}:/" + "/".join(parts[3:])
            loc_text = "file:///" + urllib.parse.quote(win_path, safe=':/')
        else:
            loc_text = "file://" + urllib.parse.quote(full_path)

        # トラック情報の追加
        track = ET.SubElement(trackList, "track")
        loc = ET.SubElement(track, "location")
        loc.text = loc_text

        title = ET.SubElement(track, "title")
        title.text = f
        
        # VLCに順番を固定させるためのIDを付与
        track_ext = ET.SubElement(track, "extension", application="http://www.videolan.org/vlc/playlist/0")
        ET.SubElement(track_ext, "vlc:id").text = str(i)

        # 拡張ノード側にも同じIDでプレイリストのインデックスを登録
        ET.SubElement(extension, "vlc:item", tid=str(i))

    # 保存
    output_filename = f"/mnt/d/Youtube/{os.path.basename(os.path.normpath(abs_target))}.xspf"
    tree = ET.ElementTree(playlist)
    ET.indent(tree, space="    ")
    try:
        tree.write(output_filename, encoding="utf-8", xml_declaration=True)
        print(f"Playlist created for Windows VLC: {output_filename}")
    except IOError as e:
        print(f"Error: Could not write to {output_filename}. The file might be locked by another application.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an XSPF playlist from a directory.")
    parser.add_argument("directory", help="The directory containing media files.")
    parser.add_argument("-r", "--random", action="store_true", help="Shuffle the playlist order.")

    args = parser.parse_args()
    generate_xspf(args.directory, shuffle=args.random)
