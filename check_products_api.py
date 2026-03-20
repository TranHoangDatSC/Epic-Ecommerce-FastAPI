import requests
import json

try:
    r = requests.get("http://localhost:8000/api/v1/products")
    print(f"Status: {r.status_code}")
    print(f"Products: {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
