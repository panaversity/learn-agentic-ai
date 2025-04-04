import requests

r = requests.get("http://localhost:8000/hi")
print(r.json())