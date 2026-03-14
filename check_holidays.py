#!/usr/bin/env python3

"""
This script lists the public holidays for Japan and Singapore for the current year
using the 'holidays' package.
"""

import datetime
import holidays
import csv
import os


def main():
    """
    Main function to get holidays and write them to a CSV file.
    """
    current_year = datetime.date.today().year
    countries_to_check = {
        "JP": "Japan",
        "SG": "Singapore",
    }
    all_holidays = []

    # 祝日データを収集
    print("Fetching holiday data...")
    for code, name in countries_to_check.items():
        try:
            country_holidays = holidays.country_holidays(code, years=current_year)
            for date, holiday_name in country_holidays.items():
                all_holidays.append(
                    {
                        "date": date,
                        "country_code": code,
                        "holiday_name": holiday_name,
                    }
                )
            print(f"-> Found {len(country_holidays)} holidays for {name}")
        except KeyError:
            print(f"Could not find holidays for country code: {code}")

    # 日付順に並べ替え
    all_holidays.sort(key=lambda x: x["date"])

    # CSVファイルに書き出し
    output_filename = f"holidays_{current_year}.csv"
    weekdays_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    header = ['Date', 'Day of the week', 'Country code', 'Name']

    try:
        with open(output_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)

            for holiday in all_holidays:
                date_obj = holiday["date"]
                row = [
                    date_obj.strftime("%Y-%m-%d"),
                    weekdays_en[date_obj.weekday()],
                    holiday["country_code"],
                    holiday["holiday_name"],
                ]
                writer.writerow(row)
        
        print(f"\n✅ Successfully created: {os.path.abspath(output_filename)}")

    except IOError as e:
        print(f"\n❌ Error writing to file: {e}")


if __name__ == "__main__":
    main()