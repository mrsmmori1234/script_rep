import os
import re

# 対象のディレクトリ
TARGET_DIR = "/mnt/d/Youtube/Movie_Pool"

def has_japanese(text):
    # ひらがな、カタカナ、漢字、全角記号が含まれているか判定する正規表現
    ja_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u3000-\u303F]')
    return bool(ja_pattern.search(text))

def process_srt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # SRTの各ブロック（空行で区切られた単位）に分割
    blocks = content.strip().split('\n\n')
    new_blocks = []

    for block in blocks:
        lines = block.split('\n')
        if len(lines) < 3:
            # ブロックの行数が足りない場合はそのまま保持（インデックスやタイムスタンプのみ等）
            new_blocks.append(block)
            continue
        
        # 最初の2行は「番号」と「タイムスタンプ」なのでそのまま保持
        new_lines = [lines[0], lines[1]]
        
        # 3行目以降の字幕テキストをループ
        for line in lines[2:]:
            # 日本語が含まれていない行（英語など）だけを残す
            if not has_japanese(line):
                # 空行でなければ追加
                if line.strip():
                    new_lines.append(line)
        
        # 字幕テキストが残った場合のみブロックを再構成
        if len(new_lines) > 2:
            new_blocks.append('\n'.join(new_lines))

    # 上書き保存
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(new_blocks) + '\n\n')
    print(f"Processed: {os.path.basename(file_path)}")

def main():
    if not os.path.exists(TARGET_DIR):
        print(f"Error: Directory {TARGET_DIR} does not exist.")
        return

    # ディレクトリ内の.srtファイルを全て処理
    for filename in os.listdir(TARGET_DIR):
        if filename.endswith('.srt'):
            file_path = os.path.join(TARGET_DIR, filename)
            process_srt(file_path)

if __name__ == "__main__":
    main()
