#!/usr/bin/env python3
import os
import sys
import xml.etree.ElementTree as ET
import urllib.parse

def generate_xspf(target_dir):
    # 絶対パスを取得
    abs_target = os.path.abspath(target_dir)
    
    if not os.path.isdir(abs_target):
        print(f"Error: {abs_target} is not a directory.")
        return

    media_files = [f for f in sorted(os.listdir(abs_target)) if f.lower().endswith(('.mp3', '.mp4'))]
    
    if not media_files:
        print("No media files found.")
        return

    # XMLの構築
    playlist = ET.Element("playlist", version="1", xmlns="http://xspf.org/ns/0/")
    ET.SubElement(playlist, "title").text = os.path.basename(os.path.normpath(abs_target))
    trackList = ET.SubElement(playlist, "trackList")

    for f in media_files:
        full_path = os.path.join(abs_target, f)
        
        # --- WSLパス (/mnt/x/...) を Windowsパス (X:/...) に変換 ---
        if full_path.startswith('/mnt/'):
            parts = full_path.split('/')
            # parts[2] がドライブ文字 (d や c)
            drive = parts[2].upper()
            # 残りのパスを結合
            win_path = f"{drive}:/" + "/".join(parts[3:])
            # VLCが確実に認識するよう、再度URLエンコード（ただしスラッシュは残す）
            loc_text = "file:///" + urllib.parse.quote(win_path, safe=':/')
        else:
            # WSL内のネイティブ領域にある場合はそのまま（Windows版VLCからは見えない可能性あり）
            loc_text = "file://" + urllib.parse.quote(full_path)

        track = ET.SubElement(trackList, "track")
        loc = ET.SubElement(track, "location")
        loc.text = loc_text
        
        title = ET.SubElement(track, "title")
        title.text = f

    # 保存
    output_filename = f"{os.path.basename(os.path.normpath(abs_target))}.xspf"
    tree = ET.ElementTree(playlist)
    ET.indent(tree, space="    ")
    tree.write(output_filename, encoding="utf-8", xml_declaration=True)
    print(f"Playlist created for Windows VLC: {output_filename}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_xspf(sys.argv[1])
    else:
        print("Usage: python3 make_playlist.py [directory]")