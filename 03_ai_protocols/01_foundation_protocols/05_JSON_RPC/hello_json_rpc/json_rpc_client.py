import httpx

def call_rpc(method: str, params=None, id=1):
    """Call JSON-RPC method"""
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": id
    }
    
    response = httpx.post("http://127.0.0.1:8000/", json=request)
    return response.json()

# Try it out
if __name__ == "__main__":
    print("=== Hello World JSON-RPC ===\n")
    
    # Hello World
    result = call_rpc("hello")
    print(f"hello() -> {result['result']}")
    
    # Hello with name
    result = call_rpc("hello", "Alice")
    print(f"hello('Alice') -> {result['result']}")
    
    # Add numbers
    result = call_rpc("add", [5, 3])
    print(f"add([5, 3]) -> {result['result']}")
    
    # Error case
    result = call_rpc("unknown")
    print(f"unknown() -> Error: {result['error']['message']}")