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

response_list = requests.post(url, headers=headers, json=get_body("prompts/list", id=1))
print("\nList Prompts:", response_list.text)

response_read = requests.post(url, headers=headers, json=get_body("prompts/get", {"name": "format", "arguments": {"doc_content": "Agentic AI is a new paradigm in AI that is based on the idea that AI should be able to learn and adapt to new tasks and environments."}}, id=2))
print("\nRead Prompt:", response_read.text)