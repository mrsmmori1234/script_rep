#!/bin/bash

# --- 設定 ---
# スクリプトがあるディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# venvのPythonパス（ご自身の環境に合わせて修正してください）
PYTHON_BIN="/home/mrsmmori/.pyenv/versions/scripts-env/bin/python"
# Pythonスクリプトのパス
PY_SCRIPT="$SCRIPT_DIR/make_playlist.py"

# --- 1. 引数チェック ---
if [ $# -eq 0 ]; then
    echo "使用法: $0 [-r] [ターゲットディレクトリ]"
    exit 1
fi

SHUFFLE_OPT=""
TARGET_DIR_INPUT=""

for arg in "$@"; do
    case $arg in
        -r|--random)
            SHUFFLE_OPT="-r"
            ;;
        *)
            if [ -z "$TARGET_DIR_INPUT" ]; then
                TARGET_DIR_INPUT="$arg"
            fi
            ;;
    esac
done

if [ -z "$TARGET_DIR_INPUT" ]; then
    echo "使用法: $0 [-r] [ターゲットディレクトリ]"
    exit 1
fi
TARGET_DIR=$(realpath "$TARGET_DIR_INPUT") 2>/dev/null || { echo "エラー: パスを解決できません"; exit 1; }

# --- 2. バリデーション ---
if [ ! -d "$TARGET_DIR" ]; then
    echo "エラー: '$TARGET_DIR' は有効なディレクトリではありません。"
    exit 1
fi

if [ ! -f "$PYTHON_BIN" ]; then
    echo "エラー: Python環境が見つかりません: $PYTHON_BIN"
    exit 1
fi

PARENT_DIR=$(dirname "$TARGET_DIR")

# --- 3. 実行 ---
echo "プレイリストを作成中: $TARGET_DIR"

# 親ディレクトリに移動してから実行することで、出力ファイルを親ディレクトリ配下に作成します
cd "$PARENT_DIR" || { echo "エラー: ディレクトリを移動できませんでした: $PARENT_DIR"; exit 1; }

# Pythonスクリプトの実行（二重実行を解消し、結果を変数に格納）
"$PYTHON_BIN" "$PY_SCRIPT" "$TARGET_DIR" ${SHUFFLE_OPT}
EXIT_CODE=$?

# --- 4. 実行結果の確認とVLC起動オプション ---
if [ $EXIT_CODE -eq 0 ]; then
    PLAYLIST_FILE="$PARENT_DIR/$(basename "$TARGET_DIR").xspf"
    
    echo "---------------------------------------"
    echo "完了しました: $PLAYLIST_FILE"
    echo "---------------------------------------"
    
    # オプション: すぐにVLCで再生するか確認（不要なら削除してください）
    #read -p "今すぐVLCで再生しますか？ (y/N): " yn
    #case $yn in
    #    [Yy]* ) vlc "$PLAYLIST_FILE" & ;;
    #    * ) echo "終了します。";;
    #esac
else
    echo "エラーが発生しました。"
    exit 1
fi
exit $EXIT_CODE