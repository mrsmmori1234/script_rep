#!/bin/bash

# 1. 引数があるかチェック
if [ $# -eq 0 ]; then
    echo "使用法: ./combine.sh [ディレクトリパス]"
    exit 1
fi

TARGET_DIR=$1

# 2. Pythonがインストールされているかチェック
if ! command -v python3 &> /dev/null; then
    echo "エラー: python3 が見つかりません。インストールしてください。"
    exit 1
fi

# 3. Pythonスクリプトの実行
# combine.py が同じディレクトリにあることを想定しています
echo "処理を開始します: $TARGET_DIR"
/home/mrsmmori/.pyenv/versions/scripts-env/bin/python /home/mrsmmori/scripts/combine.py $TARGET_DIR


# 4. 実行結果の確認
if [ $? -eq 0 ]; then
    echo "完了しました。"
else
    echo "エラーが発生しました。"
    exit 1
fi