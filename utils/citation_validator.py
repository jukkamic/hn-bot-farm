import requests
import sys

def validate_hn_id(item_id):
    """Checks the official HN API to see if the ID exists."""
    url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and response.json() is not None:
            return True
    except Exception:
        pass
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python utils/citation_validator.py <item_id>")
        sys.exit(1)
    
    item_id = sys.argv[1]
    if validate_hn_id(item_id):
        print(f"VALID: {item_id}")
    else:
        print(f"INVALID: {item_id}")
        sys.exit(1)
