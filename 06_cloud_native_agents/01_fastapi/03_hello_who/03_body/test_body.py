import requests

r = requests.post("http://localhost:8000/hi", json={"who": "Mom"})
print(r.json())