import os
import subprocess
import sys

def convert_to_wmp_compatible(input_folder):
    output_folder = os.path.join(input_folder, "converted_for_WMP")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Target extensions: include mp4
    valid_extensions = ('.mp4', '.mkv', '.mov', '.avi', '.wmv')

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(valid_extensions):
            input_path = os.path.join(input_folder, filename)
            
            # Output filename (keep extension as .mp4 to distinguish from original)
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(output_folder, f"{base_name}_wmp.mp4")

            print(f"Converting: {filename}...")

            # Settings for highest WMP compatibility (H.264 + AAC + YUV420P)
            cmd = [
                'ffmpeg', '-i', input_path,
                '-c:v', 'libx264',      # Convert video to H.264
                '-pix_fmt', 'yuv420p',  # Set pixel format to YUV420P (critical for compatibility)
                '-c:a', 'aac',          # Convert audio to AAC
                '-b:a', '192k',         # Audio bitrate
                '-y', output_path
            ]

            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                print(f"Finished: {output_path}")
            except subprocess.CalledProcessError:
                print(f"Error occurred: {filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py [folder_path]")
    else:
        convert_to_wmp_compatible(sys.argv[1])