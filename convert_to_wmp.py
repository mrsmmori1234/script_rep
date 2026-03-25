import os
import subprocess
import sys

def convert_to_wmp_compatible(input_folder):
    output_folder = os.path.join(input_folder, "converted_for_WMP")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 変換対象：mp4も含める
    valid_extensions = ('.mp4', '.mkv', '.mov', '.avi', '.wmv')

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(valid_extensions):
            input_path = os.path.join(input_folder, filename)
            
            # 出力ファイル名（元のファイルと区別するため拡張子はそのまま .mp4）
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(output_folder, f"{base_name}_wmp.mp4")

            print(f"変換中: {filename}...")

            # WMPで最も互換性が高い設定 (H.264 + AAC + YUV420P)
            cmd = [
                'ffmpeg', '-i', input_path,
                '-c:v', 'libx264',      # 映像をH.264に変換
                '-pix_fmt', 'yuv420p',  # 色空間をWMP互換にする（重要！）
                '-c:a', 'aac',          # 音声をAACに変換
                '-b:a', '192k',         # 音質設定
                '-y', output_path
            ]

            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                print(f"完了: {output_path}")
            except subprocess.CalledProcessError:
                print(f"エラー発生: {filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用法: python script.py [フォルダのパス]")
    else:
        convert_to_wmp_compatible(sys.argv[1])