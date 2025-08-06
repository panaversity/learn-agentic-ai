from fastapi import FastAPI

app = FastAPI()

# FastAPI endpoint to invoke the actor
@app.get("/")
async def greet():
    return {"message": f"Hello, World!"}