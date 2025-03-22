from fastapi import FastAPI

app = FastAPI(title="UIT Fast API", version="0.0.0")

@app.get("/")
def index():
    return {"Hello": "World"}