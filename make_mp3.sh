#!/bin/bash

# 1. 引数があるかチェック
if [ $# -eq 0 ]; then
    echo "使用法: ./make_mp3.sh [ディレクトリパス]"
    exit 1
fi

TARGET_DIR=$(realpath "$1")

if [ ! -d "$TARGET_DIR" ]; then
    echo "エラー: '$TARGET_DIR' は有効なディレクトリではありません。"
    exit 1
fi

PARENT_DIR=$(dirname "$TARGET_DIR")

# 2. Pythonがインストールされているかチェック
if ! command -v python3 &> /dev/null; then
    echo "エラー: python3 が見つかりません。インストールしてください。"
    exit 1
fi

# 3. Pythonスクリプトの実行
# combine.py が同じディレクトリにあることを想定しています
echo "処理を開始します: $TARGET_DIR"

# 親ディレクトリに移動してから実行することで、出力ファイルを親ディレクトリ配下に作成します
cd "$PARENT_DIR" || exit 1
"/home/mrsmmori/.pyenv/versions/scripts-env/bin/python" "/home/mrsmmori/scripts/make_mp3.py" "$TARGET_DIR"

# 4. 実行結果の確認
if [ $? -eq 0 ]; then
    echo "完了しました。"
else
    echo "エラーが発生しました。"
    exit 1
fi