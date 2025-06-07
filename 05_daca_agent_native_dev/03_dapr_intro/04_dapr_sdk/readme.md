# [Dapr SDKs Hands On](https://docs.dapr.io/developing-applications/sdks/python/)

We have tried using APIs to interact with Dapr Sidecar from our container. In last module we did it for State Management and PubSub.

Dapr supports both HTTP and gRPC APIs for interacting with its building blocks and we can invoke them with Dapr API or SDKs. The Dapr SDKs are the easiest way for you to get Dapr into your application. 
- Client: The Dapr client allows you to invoke Dapr building block APIs and perform each building block’s actions
- Server extensions: The Dapr service extensions allow you to create services that can be invoked by other services and subscribe to topics
- Actor: The Dapr Actor SDK allows you to build virtual actors with methods, state, timers, and persistent reminders
- Workflow: Dapr Workflow makes it easy for you to write long running business logic and integrations in a reliable way

**Here we will get hands on Dapr SDK and you will complete a challenge project skills you have acquired from 01_agents_first and the first three modules of 05_daca_agent_native_dev**

## Shall we use [Dapr SDKs](https://docs.dapr.io/developing-applications/sdks/) vs [APIs](https://docs.dapr.io/getting-started/get-started-api/) directly?

Using Dapr SDKs offers a more developer-friendly experience compared to directly interacting with the Dapr APIs. SDKs provide typed language APIs, simplifying the interaction with Dapr's building blocks and abstracting away the need to directly handle HTTP or gRPC calls. While direct API calls are possible, SDKs streamline the development process by providing language-specific libraries and helper functions. 

### Dapr SDKs

### Benefits:
- Abstraction: SDKs abstract away the low-level details of interacting with the Dapr sidecar (daprd). 
- Language-Specific APIs: SDKs provide typed language APIs, making it easier to work with Dapr's building blocks in your preferred language. 
- Simplified Development: SDKs reduce the complexity of writing Dapr-aware applications by providing helper functions and libraries for common tasks. 
- Cross-Language Support: Dapr SDKs support multiple languages, allowing developers to use their preferred language while leveraging Dapr's functionalities. 
- Examples: Dapr provides SDKs for popular languages like .NET, Java, Python, Go, and more. 
- Improved developer productivity by reducing boilerplate code and simplifying API usage. 
- Enhanced code readability and maintainability due to the use of language-specific APIs. 
- Easier integration with existing applications and frameworks. 

## Direct API Calls (HTTP/gRPC):

- Lower-Level Interaction: Direct API calls require developers to interact directly with the Dapr sidecar via HTTP or gRPC. 
- No Language-Specific Abstraction: Developers need to handle the details of constructing HTTP/gRPC requests and parsing responses. 
- More Control:Direct API calls offer more control over the interaction with Dapr, allowing for fine-grained customization. 

## When to use which:
- SDKs: Recommended for most developers, especially when starting with Dapr or when a specific language is preferred. 

Direct API Calls Useful when:
- Fine-grained control over the interaction with Dapr is needed. 
- Performance is critical, and gRPC is preferred. 
- Interacting with Dapr from a language that doesn't have an official SDK. 
- Testing or debugging Dapr's internal workings. 
- Hit bottlenecks due to some internal problem with SDK.

In essence, Dapr SDKs simplify the development process by providing language-specific APIs and abstractions, while direct API calls offer more control and flexibility. Choosing the right approach depends on the specific needs of the project and the preferences of the development team

## Hands On Dapr SDK

### Setup 
Take the code from 03_module last step as starter code

### Install DAPR SDK

Open hello_fastapi project in shell and run:

```bash
uv add dapr
```

### Update main.py

```python
from fastapi import FastAPI, HTTPException
from dapr.clients import DaprClient
import json

app = FastAPI(title="Dapr FastAPI Hello World")


@app.get("/")
async def root():
    return {"message": "Hello from Live AGI and Dapr SDK!"}


@app.post("/messages")
async def save_message(user_id: str, message: str):
    try:
        with DaprClient() as client:
            # Save state
            state_data = {"user_id": user_id, "message": message}
            client.save_state(store_name="statestore", key=user_id, value=json.dumps(state_data))

            # Publish event
            event_data = {"user_id": user_id, "message": message}
            client.publish_event(pubsub_name="pubsub", topic_name="message-updated", data=json.dumps(event_data))

        return {"status": f"Stored and published message for {user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/messages/{user_id}")
async def get_message(user_id: str):
    try:
        with DaprClient() as client:
            # Get state
            response = client.get_state(store_name="statestore", key=user_id)
            if response.data:
                return json.loads(response.data.decode('utf-8'))
            else:
                raise HTTPException(status_code=404, detail="Message not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/subscribe")
async def subscribe_message(data: dict):
    event_data = data.get("data", {})
    user_id = event_data.get("user_id", "unknown")
    message = event_data.get("message", "no message")
    print(f"Received event: User {user_id} updated message to '{message}'")
    return {"status": "Event processed"}

```

### Run and Test

```
tilt up
```

Open in Browser
- Tilt UI: http://localhost:10350/overview
- Dapr Dashboard: http://localhost:8080/overview
- FastAPI Docs: http://localhost:8000/docs#/

Test them and final clean up

```bash
tilt down
```

### Challenge

Now install agents sdk and create an Agent with the Dapr SDK features we have used. Use all concepts your have learned in 01_agents_first
