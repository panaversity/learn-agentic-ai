import requests # http/rest -> package -> requests, httpx

url = "http://localhost:8000/mcp/"

headers = {"Accept": "application/json,text/event-stream"}

def get_body(method: str, params: dict = {}, id: int = 1):
    return {
        "jsonrpc": "2.0",
        "method": method,
        "id": id,
        "params": params,
    }

response_list = requests.post(url, headers=headers, json=get_body("resources/list", id=1))
print("\nList Resources:", response_list.text)

response_read = requests.post(url, headers=headers, json=get_body("resources/read", {"uri": "docs://documents"}, id=2))
print("\nRead Resource:", response_read.text)

# Templated Resources

body_templates = get_body("resources/templates/list", id=3)
response_templates = requests.post(url, headers=headers, json=body_templates)
print("\nList Templates:", response_templates.text)

body_read = get_body("resources/read", {"uri": "docs://plan.md"}, id=4)
response_read = requests.post(url, headers=headers, json=body_read)
print("\nRead Resource:", response_read.text)