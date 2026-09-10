import sys

import requests

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
house = {"size": 100, "nb_rooms": 3, "garden": 1}

r = requests.get(f"{BASE_URL}/predict", params=house, timeout=10)
print("GET  :", r.status_code, r.json())

r = requests.post(f"{BASE_URL}/predict", json=house, timeout=10)
print("POST :", r.status_code, r.json())

r = requests.post(f"{BASE_URL}/predict", json={**house, "garden": 5}, timeout=10)
print("POST invalide :", r.status_code, r.json()["detail"][0]["msg"])