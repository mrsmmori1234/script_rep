#!/bin/bash

echo "==== MP4 → MP3 変換スクリプト ===="
echo "入力ファイルを指定してください:"
read -r INPUT

# 入力ファイルの存在確認
if [ ! -f "$INPUT" ]; then
  echo "エラー: ファイルが存在しません。"
  exit 1
fi

# ファイル名を分解
INPUT_DIR=$(dirname "$INPUT")
INPUT_BASE=$(basename "$INPUT")
INPUT_NAME="${INPUT_BASE%.*}"

# 出力ファイル名（先頭に mp3_ を追加）
OUTPUT="$INPUT_DIR/mp3_${INPUT_NAME}.mp3"

echo ""
echo "変換を開始します..."
ffmpeg -i "$INPUT" -vn -acodec libmp3lame -ab 192k "$OUTPUT"

if [ $? -eq 0 ]; then
  echo "✅ 変換完了: $OUTPUT"
else
  echo "❌ 変換に失敗しました。"
fi

