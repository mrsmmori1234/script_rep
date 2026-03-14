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
    echo "使用法: $0 [ターゲットディレクトリ]"
    exit 1
fi

TARGET_DIR=$(realpath "$1")

# --- 2. バリデーション ---
if [ ! -d "$TARGET_DIR" ]; then
    echo "エラー: '$TARGET_DIR' は有効なディレクトリではありません。"
    exit 1
fi

if [ ! -f "$PYTHON_BIN" ]; then
    echo "エラー: Python環境が見つかりません: $PYTHON_BIN"
    exit 1
fi

# --- 3. 実行 ---
echo "プレイリストを作成中: $TARGET_DIR"
"$PYTHON_BIN" "$PY_SCRIPT" "$TARGET_DIR"

# --- 4. 実行結果の確認とVLC起動オプション ---
if [ $? -eq 0 ]; then
    # 作成されたはずのファイル名（ディレクトリ名.xspf）を推測
    PLAYLIST_FILE="$(basename "$TARGET_DIR").xspf"
    
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