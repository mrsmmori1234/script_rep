import datetime
import os
import sys
import warnings

# Suppress dependency warnings before they are triggered by importing requests.
warnings.filterwarnings("ignore", message=".*urllib3.*")
warnings.filterwarnings("ignore", message=".*chardet.*")
warnings.filterwarnings("ignore", message=".*charset_normalizer.*")



def get_color(pct):
    if not sys.stdout.isatty():
        return "", ""
    if pct >= 80:
        return "\033[91m\033[1m", "\033[0m"
    if pct >= 60:
        return "\033[93m", "\033[0m"
    return "\033[92m", "\033[0m"


def get_progress_bar(pct, width=20):
    filled = int(width * pct / 100)
    return "[" + "#" * filled + "." * (width - filled) + "]"


def check_usage(api_key=None):
    api_key = api_key or os.getenv("DEEPL_API_KEY")

    if not api_key:
        print("Error: 'DEEPL_API_KEY' is not set")
        return None

    import requests

    url = "https://api-free.deepl.com/v2/usage"
    headers = {"Authorization": f"DeepL-Auth-Key {api_key}"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        count = data.get("character_count", 0)
        limit = data.get("character_limit", 0)
        remaining = limit - count
        usage_pct = (count / limit * 100) if limit > 0 else 0

        today = datetime.date.today()
        if today.month == 12:
            next_reset = datetime.date(today.year + 1, 1, 1)
        else:
            next_reset = datetime.date(today.year, today.month + 1, 1)

        days_left = (next_reset - today).days
        color_start, color_end = get_color(usage_pct)
        bar = get_progress_bar(usage_pct)

        print(f"\n{'='*40}")
        print("      DeepL API Usage Status")
        print(f"{'='*40}")
        print(f"Progress:  {color_start}{bar} {usage_pct:.1f}%{color_end}")
        print(f"Used:      {count:10,} / {limit:,} chars")
        print(f"Remaining: {color_start}{remaining:10,}{color_end} chars")
        print(f"Next Reset: {next_reset.strftime('%Y/%m/%d')} ({days_left} days left)")
        print(f"{'='*40}")
        print("Note: Reset date is estimated (1st of month).\n")
        return data

    except Exception as e:
        print(f"Error: {e}")
        return None


def main(argv=None):
    _ = argv
    check_usage()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))