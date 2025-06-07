import logging

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hello Workflow")

@app.get("/")
async def root():
    return {"message": "Hello World"}