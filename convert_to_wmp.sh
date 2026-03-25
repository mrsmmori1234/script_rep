#!/bin/bash

# --- 設定 ---
# スクリプトがあるディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# pyenvのvenvパス（ご提示の環境に合わせています）
PYTHON_BIN="/home/mrsmmori/.pyenv/versions/scripts-env/bin/python"
# 変換スクリプトのパス
PY_SCRIPT="$SCRIPT_DIR/convert_to_wmp.py"

# --- 1. 引数チェック ---
if [ $# -eq 0 ]; then
    echo "使用法: $0 [動画が入っているディレクトリ]"
    exit 1
fi

# 相対パスを絶対パスに変換
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
echo "---------------------------------------"
echo "Windows Media Player用に変換を開始します"
echo "ターゲット: $TARGET_DIR"
echo "---------------------------------------"

# Pythonスクリプトの実行
"$PYTHON_BIN" "$PY_SCRIPT" "$TARGET_DIR"

# --- 4. 実行結果の確認 ---
if [ $? -eq 0 ]; then
    echo "---------------------------------------"
    echo "変換処理が正常に終了しました。"
    echo "出力先: $TARGET_DIR/converted_for_WMP/"
    echo "---------------------------------------"
else
    echo "エラーが発生しました。"
    exit 1
fi