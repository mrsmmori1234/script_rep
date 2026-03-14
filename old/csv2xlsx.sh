#!/bin/bash
# csv2xlsx.sh for pyenv virtualenv

# pyenv 仮想環境を有効化
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv activate scripts-env

# csv2xlsx.py を実行
python "$HOME/scripts/csv2xlsx.py" "$@"

# 仮想環境を無効化
pyenv deactivate

