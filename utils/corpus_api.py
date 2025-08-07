import requests

API_URL = "https://api.corpus.swecha.org/api/v1/categories/"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTQ2NzAwNTEsInN1YiI6ImZkZjgzMzExLTJlYzctNDc2Mi04OWQxLTMzNzI0NGM4YWYwZiJ9.6N9_R1d4mAWDZmiZ4Lv2rCtAAIcdq0u8ZYIcnhujvqQ"

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
