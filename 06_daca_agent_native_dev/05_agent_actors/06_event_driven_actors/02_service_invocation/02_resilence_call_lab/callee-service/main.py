import logging
from fastapi import FastAPI, HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_ID = "callee-app"
app = FastAPI(title="CalleeService")

# Counter to simulate temporary failures for retry demonstration
fail_count = 0
MAX_FAILS_BEFORE_SUCCESS = 2 # Will fail the first 2 times it\'s called

@app.get("/greet/{name}")
async def greet(name: str, simulate_failure: bool = False):
    global fail_count
    logger.info(f"Greet endpoint called with name: {name}. Current fail_count: {fail_count}")

    if simulate_failure and fail_count < MAX_FAILS_BEFORE_SUCCESS:
        fail_count += 1
        logger.warning(f"Simulating failure #{fail_count} for greet endpoint.")
        raise HTTPException(status_code=500, detail=f"Simulated temporary error from callee-service (attempt {fail_count})")

    # Reset fail_count after successful processing or if not simulating failure
    fail_count = 0
    message = f"Hello, {name} from {APP_ID}!"
    logger.info(f"Successfully processed greet request. Responding with: {message}")
    return {"message": message}