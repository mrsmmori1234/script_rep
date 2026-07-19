import sys
import shutil
from pathlib import Path

TARGET_DIR = Path("/mnt/d/Youtube/Switching_Movie")
ORIGINAL_SUBDIR = "original"

def _find_subtitle_source(mp4_path: Path, choice: str) -> Path | None:
    """動画に対応する指定言語の字幕ソースを探す"""
    target_dir = mp4_path.parent
    base_name = mp4_path.stem
    
    # 言語に応じた拡張子候補
    suffixes = [".en.srt"] if choice == "en" else [".en_JP.srt", "_JP.srt", ".ja.srt", ".jp.srt"]
    
    candidates = []
    # 1. original フォルダ内の候補
    for suf in suffixes:
        candidates.append(target_dir / ORIGINAL_SUBDIR / f"{base_name}{suf}")
    # 2. 同じフォルダ内の候補
    for suf in suffixes:
        candidates.append(target_dir / f"{base_name}{suf}")
    # 3. _partN を除外した original フォルダ内の候補
    if '_part' in base_name:
        stripped = base_name.rsplit('_part', 1)[0]
        for suf in suffixes:
            candidates.append(target_dir / ORIGINAL_SUBDIR / f"{stripped}{suf}")

    return next((p for p in candidates if p.exists()), None)


def switch_subtitles(choice: str) -> None:
    """外部から直接呼び出せる字幕切り替えのメイン関数"""
    choice = choice.strip().lower()
    if choice not in ["en", "ja"]:
        print("エラー: en または ja を指定してください。")
        return

    mp4_files = list(TARGET_DIR.glob("*.mp4"))
    if not mp4_files:
        print(f"動画ファイル（.mp4）が見つかりませんでした: {TARGET_DIR}")
        return

    success_count = 0
    for mp4_path in mp4_files:
        src_srt = _find_subtitle_source(mp4_path, choice)
        dest_srt = mp4_path.with_suffix(".srt")

        if not src_srt:
            print(f"警告: 字幕なし: {mp4_path.name}")
            continue

        # コピー先が存在し、かつ中身が同じならスキップ（エラー防止）
        if dest_srt.exists() and src_srt.samefile(dest_srt):
            print(f"スキップ (適用済み): {dest_srt.name}")
        else:
            shutil.copy2(src_srt, dest_srt)
            print(f"適用完了: {dest_srt.name} <-- {src_srt.name}")
        
        success_count += 1

    print(f"\n完了: [{choice.upper()}] 字幕を {success_count} 件に適用しました。")


def main():
    if len(sys.argv) < 2:
        print("エラー: en または ja を指定してください。")
        print("使い方: python switch_subtitle.py en")
        return 1
        
    switch_subtitles(sys.argv[1])
    return 0

if __name__ == "__main__":
    sys.exit(main())
