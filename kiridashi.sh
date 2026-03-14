#!/bin/bash

echo "==== FFmpeg Cut Script ===="
echo "入力ファイルを指定してください:"
read -r INPUT

if [ ! -f "$INPUT" ]; then
  echo "エラー: ファイルが存在しません。"
  exit 1
fi

# 入力ファイルのディレクトリと名前を分解
INPUT_DIR=$(dirname "$INPUT")
INPUT_BASE=$(basename "$INPUT")
INPUT_NAME="${INPUT_BASE%.*}"   # 拡張子を除いた名前

# prefix設定
PREFIX="out_"

while true; do
  echo ""
  echo "===== メニュー ====="
  echo "1) 開始・終了時間を指定して動画切り出し (mp4)"
  echo "q) 終了"
  echo "選択してください: "
  read -r CHOICE

  case "$CHOICE" in
    1)
      echo "開始時間を入力してください (例: 00:01:23): "
      read -r START
      echo "終了時間を入力してください (例: 00:02:34): "
      read -r END
      OUT="$INPUT_DIR/${PREFIX}trim_${INPUT_NAME}.mp4"
      ffmpeg -i "$INPUT" -ss "$START" -to "$END" -c copy "$OUT"
      echo "保存しました: $OUT"
      ;;
    q|Q)
      echo "終了します。"
      break
      ;;
    *)
      echo "無効な選択です。"
      ;;
  esac
done

