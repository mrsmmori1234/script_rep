#!/usr/bin/env python3
"""List public holidays for Japan and Singapore."""

import argparse
import csv
import datetime
import os
import sys



DEFAULT_COUNTRIES = {
    "JP": "Japan",
    "SG": "Singapore",
}


def collect_holidays(year=None, countries=None):
    year = year or datetime.date.today().year
    countries = countries or DEFAULT_COUNTRIES
    all_holidays = []

    import holidays

    print("Fetching holiday data...")
    for code, name in countries.items():
        try:
            country_holidays = holidays.country_holidays(code, years=year)
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

    all_holidays.sort(key=lambda x: x["date"])
    return all_holidays


def write_holidays_csv(all_holidays, output_filename):
    weekdays_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    header = ["Date", "Day of the week", "Country code", "Name"]

    with open(output_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)

        for holiday in all_holidays:
            date_obj = holiday["date"]
            writer.writerow(
                [
                    date_obj.strftime("%Y-%m-%d"),
                    weekdays_en[date_obj.weekday()],
                    holiday["country_code"],
                    holiday["holiday_name"],
                ]
            )


def create_holidays_csv(year=None, output_filename=None, countries=None):
    year = year or datetime.date.today().year
    output_filename = output_filename or f"holidays_{year}.csv"
    all_holidays = collect_holidays(year=year, countries=countries)

    try:
        write_holidays_csv(all_holidays, output_filename)
        print(f"\nSuccessfully created: {os.path.abspath(output_filename)}")
        return output_filename
    except IOError as e:
        print(f"\nError writing to file: {e}")
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(description="Create a CSV of Japan and Singapore public holidays.")
    parser.add_argument("--year", type=int, default=None, help="Year to check. Defaults to the current year.")
    parser.add_argument("--output", default=None, help="Output CSV path.")
    args = parser.parse_args(argv)

    return 0 if create_holidays_csv(year=args.year, output_filename=args.output) else 1


if __name__ == "__main__":
    sys.exit(main())