from fastapi import FastAPI


app  = FastAPI()

@app.get("/")
def index():
    return {"Hello": "world"}

@app.get("/piaic/")
def piaic():
    return {"organization": "piaic"}



