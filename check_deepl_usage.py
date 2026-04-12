import os
import requests

def check_usage():
    api_key = os.getenv('DEEPL_API_KEY')
    
    if not api_key:
        print("Error: 環境変数 'DEEPL_API_KEY' が設定されていません。")
        return

    url = "https://api-free.deepl.com/v2/usage"
    headers = {
        "Authorization": f"DeepL-Auth-Key {api_key}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        count = data.get("character_count", 0)
        limit = data.get("character_limit", 0)
        remaining = limit - count

        print(f"--- DeepL API Usage ---")
        print(f"Used:      {count:,} characters")
        print(f"Limit:     {limit:,} characters")
        print(f"Remaining: {remaining:,} characters")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_usage()