from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
async def root(request: Request):
    print(f"--- Request headers: {request.headers} ---")
    http_version = request.scope.get('http_version', None)
    print(f"--- HTTP version: {http_version} ---")
    request_client = request.client
    
    client_host = None
    client_port = None
    
    if request_client:
        client_host = request_client.host
        client_port = request_client.port
    
    headers = dict(request.headers)
    return {
        "message": "Hello from FastAPI over HTTP/2 Cleartext (h2c)!",
        "http_version_detected": http_version,
        "client": f"{client_host}:{client_port}",
        "request_headers": headers
    }

@app.post("/data")
async def create_data(request: Request, payload: dict):
    request_client = request.client
    
    client_host = None
    client_port = None
    
    if request_client:
        client_host = request_client.host
        client_port = request_client.port
    
    http_version = request.scope.get('http_version', None)
    return {
        "message": "Data received successfully via h2c!",
        "http_version_detected": http_version,
        "received_payload": payload,
        "client": f"{client_host}:{client_port}"
    }