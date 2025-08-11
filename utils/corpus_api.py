import requests

API_URL = "https://api.corpus.swecha.org/api/v1/categories/"
BEARER_TOKEN = "YOUR_BEARER_TOKEN"

def fetch_categories():
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to fetch categories: {e}")
        return None
