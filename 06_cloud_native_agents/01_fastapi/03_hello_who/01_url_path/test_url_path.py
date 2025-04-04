import requests

r = requests.get("http://localhost:8000/hi/Mom")

print(r.json())