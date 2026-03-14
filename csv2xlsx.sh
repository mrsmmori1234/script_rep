#!/usr/bin/env bash
# csv2xlsx -- CSV を XLSX に変換 (pyenv scripts-env 使用)

# 仮想環境を pyenv で指定
export PYENV_VERSION=scripts-env

python3 - <<'EOF' "$@"
import sys
import csv
from openpyxl import Workbook
import os

def csv_to_xlsx(csv_file, xlsx_file):
    wb = Workbook()
    ws = wb.active
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            ws.append(row)
    wb.save(xlsx_file)

if len(sys.argv) < 2:
    print("使い方: csv2xlsx <input.csv> [output.xlsx]")
    sys.exit(1)

csv_file = sys.argv[1]
xlsx_file = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(csv_file)[0] + ".xlsx"

csv_to_xlsx(csv_file, xlsx_file)
print(f"✅ 変換完了: {xlsx_file}")
EOF

