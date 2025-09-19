from fastapi import FastAPI

app = FastAPI(title="Dapr FastAPI Hello World")

@app.get("/")
async def root():
    return {"message": "Hello from Live AGI!"}

@app.get("/name")
async def root_user():
    return {"user": "admin!"}

@app.get("/name/{name}")
async def root_user(name: str):
    return {"user": name}