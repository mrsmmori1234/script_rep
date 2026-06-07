import os
import sys
import warnings

# Suppress dependency warnings before they are triggered by importing requests
warnings.filterwarnings("ignore", message=".*urllib3.*")
warnings.filterwarnings("ignore", message=".*chardet.*")
warnings.filterwarnings("ignore", message=".*charset_normalizer.*")
warnings.filterwarnings("ignore", message=".*RequestsDependencyWarning.*")

import requests

def check_gemini_usage():
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("Error: 'GOOGLE_API_KEY' is not set in environment variables.")
        return

    # Gemini 1.5 Flash / Pro Free Tier Limits (as of 2024/2025)
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
        }
    }

    print(f"\n{'='*45}")
    print(f"      Gemini API (Free Tier) Information")
    print(f"{'='*45}")
    
    for model, info in limits.items():
        print(f"[{model}]")
        print(f"  - Rate Limit : {info['RPM']}")
        print(f"  - Daily Limit: {info['RPD']}")
        print(f"  - Token Limit: {info['TPM']}")
        print("-" * 45)

    # API Connectivity Check
    print("Checking API Key validity...")
    test_url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
    
    try:
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            print("\033[92m✅ API Key is ACTIVE and reachable.\033[0m")
        elif response.status_code == 429:
            print("\033[91m⚠️  Quota Exceeded (429): You have hit the rate limit.\033[0m")
        else:
            print(f"\033[91m❌ API Error: {response.status_code}\033[0m")
            print(response.text)
    except Exception as e:
        print(f"❌ Connection Error: {e}")

    print(f"{'='*45}")
    print("To check detailed usage history, visit:")
    print("https://aistudio.google.com/app/plan_info")
    print(f"{'='*45}\n")

if __name__ == "__main__":
    # 必要に応じて環境変数を読み込む（.bashrcに記述されている想定）
    # os.environ['GOOGLE_API_KEY'] = 'YOUR_KEY_HERE' 
    check_gemini_usage()
