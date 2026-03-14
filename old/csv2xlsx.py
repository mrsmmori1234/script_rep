#!/usr/bin/env python3
import sys
import csv
from openpyxl import Workbook

def csv_to_xlsx(csv_file, xlsx_file):
    wb = Workbook()
    ws = wb.active

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            ws.append(row)

    wb.save(xlsx_file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: csv2xlsx.py input.csv [output.xlsx]")
        sys.exit(1)

    csv_file = sys.argv[1]
    xlsx_file = sys.argv[2] if len(sys.argv) > 2 else csv_file.replace(".csv", ".xlsx")

    csv_to_xlsx(csv_file, xlsx_file)
    print(f"✅ 変換完了: {xlsx_file}")

