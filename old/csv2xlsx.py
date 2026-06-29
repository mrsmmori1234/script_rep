#!/usr/bin/env python3
import csv
import sys



def csv_to_xlsx(csv_file, xlsx_file=None):
    from openpyxl import Workbook

    xlsx_file = xlsx_file or csv_file.replace(".csv", ".xlsx")
    wb = Workbook()
    ws = wb.active

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            ws.append(row)

    wb.save(xlsx_file)
    return xlsx_file


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv

    if len(argv) < 1:
        print("Usage: python csv2xlsx.py input.csv [output.xlsx]")
        return 1

    csv_file = argv[0]
    xlsx_file = argv[1] if len(argv) > 1 else None
    output_path = csv_to_xlsx(csv_file, xlsx_file)
    print(f"Converted: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())