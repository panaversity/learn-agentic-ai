import requests

params = {"who": "Mom"}
r = requests.get("http://localhost:8000/hi", params=params)
print(r.json())