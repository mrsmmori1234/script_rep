#!/bin/bash
# merge_mp4s_auto.sh
# MP4一括結合（再エンコード・安全リネーム）版

echo "==== MP4一括結合スクリプト（再エンコード・自動） ===="
echo "結合したいフォルダを入力してください:"
read -r TARGET_DIR

if [ ! -d "$TARGET_DIR" ]; then
    echo "エラー: フォルダが存在しません。"
    exit 1
fi

cd "$TARGET_DIR" || exit 1

echo "出力ファイル名を入力してください（例: merged.mp4）:"
read -r OUTPUT
OUTPUT=${OUTPUT:-merged.mp4}

TMP_DIR=$(mktemp -d)
LIST_FILE="$TMP_DIR/list.txt"

echo "🔍 MP4ファイルを検索中..."
COUNT=0
> "$LIST_FILE"
for f in *.mp4; do
    COUNT=$((COUNT+1))
    SAFE_NAME=$(printf "%04d.mp4" "$COUNT")
    echo "$f → $SAFE_NAME"
    # 再エンコードしてH.264に変換
    ffmpeg -y -i "$f" -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 192k "$TMP_DIR/$SAFE_NAME"
    printf "file '%s'\n" "$TMP_DIR/$SAFE_NAME" >> "$LIST_FILE"
done

echo ""
echo "🎬 FFmpegで結合中..."
ffmpeg -f concat -safe 0 -i "$LIST_FILE" -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 192k "$OUTPUT"

if [ $? -eq 0 ]; then
    echo "✅ 結合完了: $TARGET_DIR/$OUTPUT"
else
    echo "❌ 結合に失敗しました。"
fi

rm -rf "$TMP_DIR"

