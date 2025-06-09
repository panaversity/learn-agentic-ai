from fastapi import FastAPI
from json_rpc_models import Request, Response

app = FastAPI()

@app.post("/")
def rpc(req: Request):
    """Hello World JSON-RPC Server"""
    
    if req.method == "hello":
        name = req.params or "World"
        return Response(result=f"Hello, {name}!", id=req.id)
    
    elif req.method == "add":
        a, b = req.params
        return Response(result=a + b, id=req.id)
        
    else:
        return Response(
            error={"code": -32601, "message": "Method not found"},
            id=req.id
        )

if __name__ == "__main__":
    import uvicorn
    print("Hello World JSON-RPC: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)