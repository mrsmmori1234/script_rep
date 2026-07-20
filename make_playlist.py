#!/usr/bin/env python3
import argparse
import os
import random
import sys
import urllib.parse
import xml.etree.ElementTree as ET


def generate_xspf(target_dir, shuffle=False, output_dir="/mnt/d/Youtube"):
    abs_target = os.path.abspath(target_dir)

    if not os.path.isdir(abs_target):
        print(f"Error: {abs_target} is not a directory.")
        return None

    media_files = [f for f in sorted(os.listdir(abs_target)) if f.lower().endswith((".mp3", ".mp4"))]
    if not media_files:
        print("No media files found.")
        return None

    if shuffle:
        rng = random.SystemRandom()
        rng.shuffle(media_files)

    # --- ここから名前判定の修正 ---
    # 末尾のディレクトリ名を取得
    last_dir = os.path.basename(os.path.normpath(abs_target))
    
    if last_dir == "Shorts":
        # 1つ上の親ディレクトリのパスから名前を取得
        parent_dir = os.path.dirname(os.path.normpath(abs_target))
        playlist_name = os.path.basename(parent_dir)
    else:
        playlist_name = last_dir
    # --- ここまで ---

    playlist = ET.Element("playlist", version="1", xmlns="http://xspf.org/ns/0/")
    playlist.set("xmlns:vlc", "http://www.videolan.org/vlc/playlist/ns/0/")

    # 取得した playlist_name をタイトルに設定
    ET.SubElement(playlist, "title").text = playlist_name
    track_list = ET.SubElement(playlist, "trackList")
    extension = ET.SubElement(playlist, "extension", application="http://www.videolan.org/vlc/playlist/0")

    for i, filename in enumerate(media_files):
        full_path = os.path.join(abs_target, filename)

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

    # 取得した playlist_name を出力ファイル名に設定
    output_filename = os.path.join(output_dir, f"{playlist_name}.xspf")
    tree = ET.ElementTree(playlist)
    ET.indent(tree, space="    ")

    try:
        tree.write(output_filename, encoding="utf-8", xml_declaration=True)
        print(f"Playlist created for Windows VLC: {output_filename}")
        return output_filename
    except IOError:
        print(f"Error: Could not write to {output_filename}. The file might be locked by another application.")
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate an XSPF playlist from a directory.")
    parser.add_argument("directory", help="The directory containing media files.")
    parser.add_argument("-r", "--random", action="store_true", help="Shuffle the playlist order.")

    args = parser.parse_args(argv)
    return 0 if generate_xspf(args.directory, shuffle=args.random) else 1


if __name__ == "__main__":
    sys.exit(main())
