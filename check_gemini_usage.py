import os
import sys
import warnings

# Suppress dependency warnings before they are triggered by importing requests.
warnings.filterwarnings("ignore", message=".*urllib3.*")
warnings.filterwarnings("ignore", message=".*chardet.*")
warnings.filterwarnings("ignore", message=".*charset_normalizer.*")
warnings.filterwarnings("ignore", message=".*RequestsDependencyWarning.*")



def check_gemini_usage(api_key=None):
    api_key = api_key or os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("Error: 'GOOGLE_API_KEY' is not set in environment variables.")
        return None

    limits = {
        "Gemini 1.5 Flash": {
            "RPM": "15 (Requests Per Minute)",
            "RPD": "1,500 (Requests Per Day)",
            "TPM": "1 million (Tokens Per Minute)",
        },
        "Gemini 1.5 Pro": {
            "RPM": "2 (Requests Per Minute)",
            "RPD": "50 (Requests Per Day)",
            "TPM": "32,000 (Tokens Per Minute)",
        },
    }

    print(f"\n{'='*45}")
    print("      Gemini API (Free Tier) Information")
    print(f"{'='*45}")

    for model, info in limits.items():
        print(f"[{model}]")
        print(f"  - Rate Limit : {info['RPM']}")
        print(f"  - Daily Limit: {info['RPD']}")
        print(f"  - Token Limit: {info['TPM']}")
        print("-" * 45)

    import requests

    print("Checking API Key validity...")
    test_url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"

    try:
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            print("API Key is ACTIVE and reachable.")
        elif response.status_code == 429:
            print("Quota Exceeded (429): You have hit the rate limit.")
        else:
            print(f"API Error: {response.status_code}")
            print(response.text)
        status_code = response.status_code
    except Exception as e:
        print(f"Connection Error: {e}")
        status_code = None

    print(f"{'='*45}")
    print("To check detailed usage history, visit:")
    print("https://aistudio.google.com/app/plan_info")
    print(f"{'='*45}\n")
    return status_code


def main(argv=None):
    _ = argv
    check_gemini_usage()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))