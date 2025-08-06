from fastapi import FastAPI
from dapr.clients import DaprClient
import json
app = FastAPI(title="Caller Service")

CALLEE_APP_ID = "callee-app"  # The Dapr app ID of the service to call


async def call_callee_greet(name_to_greet: str):
    with DaprClient() as client:
        response = await client.invoke_method_async(
            app_id=CALLEE_APP_ID,
            method_name=f"greet/{name_to_greet}?simulate_failure=True",
            data={},
        )
        return response.data.decode('utf-8')


@app.get("/call/{name}")
async def main(name: str):
    response = await call_callee_greet(name)
    print(f"Response from callee: {response}")
    return json.loads(response)
