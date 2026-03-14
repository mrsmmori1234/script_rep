#!/bin/bash

echo "==== FFmpeg Silence Removal Script (interactive) ===="
echo "入力ファイルを指定してください (mp4/mp3):"
read -r INPUT

if [ ! -f "$INPUT" ]; then
  echo "エラー: ファイルが存在しません。"
  exit 1
fi

INPUT_DIR=$(dirname "$INPUT")
INPUT_BASE=$(basename "$INPUT")
INPUT_NAME="${INPUT_BASE%.*}"

# prefix設定
PREFIX="muon_"

# デフォルト値
DEFAULT_THRESHOLD="-50dB"   # 無音しきい値（負の値）。もっと負にすると判定が厳しくなる。
DEFAULT_MINLEN="0.5"        # 最小無音長（秒）0.5
DEFAULT_DETECT="rms"        # detection: rms or peak

echo ""
echo "---- 無音判定パラメータ ----"
read -p "無音しきい値を指定してください（例 -50dB） [デフォルト: ${DEFAULT_THRESHOLD}]: " THRESH
THRESH=${THRESH:-$DEFAULT_THRESHOLD}

read -p "最小無音長を秒で指定してください（例 0.5） [デフォルト: ${DEFAULT_MINLEN}]: " MINLEN
MINLEN=${MINLEN:-$DEFAULT_MINLEN}

read -p "検出方法 detection を選択してください (rms/peak) [デフォルト: ${DEFAULT_DETECT}]: " DET
DET=${DET:-$DEFAULT_DETECT}
if [ "$DET" != "rms" ] && [ "$DET" != "peak" ]; then
  echo "無効な detection 指定。rms を使用します。"
  DET="rms"
fi

OUT="$INPUT_DIR/${PREFIX}${INPUT_NAME}_nosilence.mp3"

echo ""
echo "無音部分を除去して音声(mp3)を抽出します..."
echo "しきい値: $THRESH, 最小長: ${MINLEN}s, detection: $DET"
ffmpeg -y -i "$INPUT" -vn -af "silenceremove=stop_periods=-1:stop_duration=${MINLEN}:stop_threshold=${THRESH}:detection=${DET}" -q:a 0 "$OUT"

if [ $? -eq 0 ]; then
  echo "✅ 保存しました: $OUT"
else
  echo "❌ エラー: 処理に失敗しました。"
fi

echo ""
echo "ヒント:"
echo "  ・判定をより厳しく（削りすぎを防ぐ）→ しきい値をもっと負に（例 -60dB）"
echo "  ・もっと多く除去したい → しきい値を less negative（例 -40dB）または minlen を短く"

