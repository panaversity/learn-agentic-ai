# JSON-RPC: A Lightweight Remote Procedure Call Protocol

JSON-RPC is a stateless, light-weight remote procedure call (RPC) protocol. It allows for notifications (data sent to the server that does not require a response) and for multiple calls to be sent to the server which may be answered out of order. The protocol uses JSON (JavaScript Object Notation) for its data format, making it human-readable and easy to work with across many programming languages.

This guide covers both JSON-RPC 1.0 and the widely adopted JSON-RPC 2.0 specification, highlighting their structures, differences, and providing hands-on Python examples using FastAPI and Pydantic.

---

## Core JSON-RPC Concepts

Regardless of the version, JSON-RPC revolves around a few core ideas:

- **Request Object**: A message sent from a client to a server to invoke a specific method with certain parameters.
- **Response Object**: A message sent from the server back to the client, containing the result of a successful method execution or an error object if the execution failed.
- **Notification**: A special type of request that does not require a response from the server.
- **Method**: A string representing the name of the procedure/function to be invoked on the server.
- **Params**: A structured value (Array or Object) holding the arguments for the method.
- **ID**: A unique identifier established by the client for a request. It's used to correlate a response with its corresponding request. Notifications do not have an `id` in JSON-RPC 2.0, or often had a `null` ID in JSON-RPC 1.0.

---

## JSON-RPC 1.0

JSON-RPC 1.0 was the initial version of the protocol. While simpler, it had ambiguities, particularly around notifications and error structures.

### JSON-RPC 1.0 Request Object

A 1.0 request includes:

- `method`: A string with the name of the method to be invoked.
- `params`: An Array of objects to pass as arguments to the method. Named parameters were not supported.
- `id`: An identifier of any JSON scalar type (string, number, boolean, or `null`).

**Example 1.0 Request:**

```json
{
  "method": "add",
  "params": [5, 3],
  "id": "req-10-add"
}
```

**Example 1.0 Notification-Style Request (using `id: null`):**
The 1.0 specification was ambiguous on notifications. A common practice was to use `id: null`. The server might or might not send a response; if it did, the response would also have `id: null`.

```json
{
  "method": "log_message",
  "params": ["User logged in"],
  "id": null
}
```

### JSON-RPC 1.0 Response Object

A 1.0 response includes:

- `result`: The data returned by the invoked method on success. This member **MUST** be `null` if an error occurred.
- `error`: An error object if an error occurred during the invocation. This member **MUST** be `null` if no error occurred. The structure of this error object was not strictly defined but often included a message and/or code.
- `id`: The ID from the original request. It must be the same as the ID of the Request object it is responding to.

**Example 1.0 Response (Success):**

```json
{
  "result": 8,
  "error": null,
  "id": "req-10-add"
}
```

**Example 1.0 Response (Error):**

```json
{
  "result": null,
  "error": {
    "message": "Method not found"
  },
  "id": "req-10-nonexistent"
}
```

**Example 1.0 Response to a Notification-Style Request (id: null):**
If a server chose to respond to a request with `id: null`:

```json
{
  "result": null,
  "error": null,
  "id": null
}
```

---

## JSON-RPC 2.0

JSON-RPC 2.0 is the current, more robust version of the protocol. It clarifies many ambiguities of 1.0, introduces named parameters, a standardized error object, and explicit support for batch requests.

### JSON-RPC 2.0 Request Object

A 2.0 request **MUST** include:

- `jsonrpc: "2.0"`: A string specifying the version of the JSON-RPC protocol.
- `method`: A string containing the name of the method to be invoked.

It **MAY** include:

- `params`: A structured value that holds the parameter values to be used during the invocation of the method. This can be an Array (for positional parameters) or an Object (for named parameters).
- `id`: An identifier established by the client if a response is expected. The value can be a string, a number, or `null` (though `null` as an ID for a request expecting a response is discouraged due to potential confusion with 1.0 notifications). If the `id` member is omitted entirely, the request is treated as a notification.

**Example 2.0 Request (Positional Params):**

```json
{
  "jsonrpc": "2.0",
  "method": "add",
  "params": [5, 3],
  "id": "req-20-add-pos"
}
```

**Example 2.0 Request (Named Params):**

```json
{
  "jsonrpc": "2.0",
  "method": "subtract",
  "params": { "minuend": 42, "subtrahend": 23 },
  "id": "req-20-sub-named"
}
```

### JSON-RPC 2.0 Notification Object

A notification is a request object without an `id` member.

- It **MUST** include `jsonrpc: "2.0"` and `method`.
- It **MAY** include `params`.
- It **MUST NOT** include an `id` member (i.e., the "id" key itself should be absent).

The server **MUST NOT** reply to a notification (e.g., an HTTP 204 No Content is appropriate).

**Example 2.0 Notification:**

```json
{
  "jsonrpc": "2.0",
  "method": "log_event",
  "params": { "level": "info", "message": "User action performed" }
}
```

### JSON-RPC 2.0 Response Object (Success)

When a method call is successful, the server **MUST** reply with a Response object containing:

- `jsonrpc: "2.0"`: Version string.
- `result`: The value returned by the invoked method. Its type is defined by the method.
- `id`: Must match the `id` of the request.

It **MUST NOT** contain an `error` member.

**Example 2.0 Response (Success):**

```json
{
  "jsonrpc": "2.0",
  "result": 19,
  "id": "req-20-sub-named"
}
```

### JSON-RPC 2.0 Response Object (Error)

When a method call results in an error, the server **MUST** reply with a Response object containing:

- `jsonrpc: "2.0"`: Version string.
- `error`: An Error object (see below).
- `id`: Must match the `id` of the request. If detecting the `id` in the request is impossible (e.g., Parse error), it must be `null`.

It **MUST NOT** contain a `result` member.

#### Error Object (JSON-RPC 2.0)

The `error` object **MUST** contain:

- `code`: An integer indicating the error type.
- `message`: A string providing a short description of the error.

It **MAY** contain:

- `data`: A primitive or structured value containing additional information about the error.

**Pre-defined Error Codes (JSON-RPC 2.0):**

- `-32700 Parse error`: Invalid JSON was received by the server. An error occurred on the server while parsing the JSON text.
- `-32600 Invalid Request`: The JSON sent is not a valid Request object.
- `-32601 Method not found`: The method does not exist / is not available.
- `-32602 Invalid params`: Invalid method parameter(s).
- `-32603 Internal error`: Internal JSON-RPC error.
- `-32000 to -32099 Server error`: Reserved for implementation-defined server-errors.

**Example 2.0 Response (Error):**

```json
{
  "jsonrpc": "2.0",
  "error": { "code": -32601, "message": "Method not found" },
  "id": "req-20-nonexistent"
}
```

### JSON-RPC 2.0 Batch Calls

To send multiple requests or notifications, the client can send an array of Request objects. The server processes each request in the batch and **SHOULD** return an array of corresponding Response objects.

- The server MAY process batch requests in parallel and respond out of order. The order of responses in the batch array does not need to match the order of requests.
- If all requests in a batch are notifications, the server **MUST NOT** return anything (an empty response or HTTP 204 No Content is appropriate).
- If the batch array itself is malformed (e.g., not an array, or an empty array), the server returns a single Response object error.

**Example 2.0 Batch Request:**

```json
[
  { "jsonrpc": "2.0", "method": "sum", "params": [1, 2, 4], "id": "1" },
  { "jsonrpc": "2.0", "method": "notify_hello", "params": [7] },
  { "jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": "2" }
]
```

**Example 2.0 Batch Response (order may vary):**

```json
[
  { "jsonrpc": "2.0", "result": 7, "id": "1" },
  { "jsonrpc": "2.0", "result": 19, "id": "2" }
]
```

(No response object for the `notify_hello` notification is included in the batch response array.)

---

## Key Differences: JSON-RPC 1.0 vs 2.0

| Feature              | JSON-RPC 1.0                                                                                | JSON-RPC 2.0                                                                                                         |
| :------------------- | :------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------- |
| **Versioning**       | Implicit (no `jsonrpc` member)                                                              | Explicit (`"jsonrpc": "2.0"` member is mandatory)                                                                    |
| **Notification**     | Ambiguous: Often `id: null` in request. Server might respond with `id: null` or not at all. | Explicit: Request object **MUST NOT** contain an `id` key. Server **MUST NOT** reply.                                |
| **Parameters**       | Positional only (Array `params`)                                                            | Positional (Array `params`) or Named (Object `params`)                                                               |
| **Error Object**     | Loosely defined. `result` must be `null`.                                                   | Standardized: `code` (integer), `message` (string), optional `data`. `result` member MUST NOT exist.                 |
| **Success Object**   | `error` must be `null`.                                                                     | `error` member MUST NOT exist.                                                                                       |
| **Batch Requests**   | Not officially specified.                                                                   | Supported (client sends an array of request objects).                                                                |
| **`id` in Request**  | Any JSON scalar (string, number, boolean, `null`).                                          | String, number, or `null`. If `id` key is absent, it's a notification.                                               |
| **`id` in Response** | Same as request. For `id: null` request, response (if any) has `id: null`.                  | Same as request. `null` if request `id` couldn't be determined (e.g. parse error). Not applicable for notifications. |

---

## Hands-on Python Examples

These examples use FastAPI for the server and HTTPX for the client to demonstrate JSON-RPC 1.0 and 2.0 interactions. We use Pydantic models for clear data structure definition and validation.

**Prerequisites:**
Install the necessary libraries:

```bash
uv add "fastapi[standard]"
```

### 1. Pydantic Models (`11_JSON_RPC/json_rpc_models.py`)

This file defines Pydantic models for JSON-RPC 1.0 and 2.0 requests, responses, and error objects.

```python
# Content of 11_JSON_RPC/json_rpc_models.py
from typing import Any
from pydantic import BaseModel, Field, field_validator, model_validator

JsonRpcIdType = str | int | None

class JsonRpcErrorObject_V2(BaseModel):
    code: int
    message: str
    data: Any | None = None

class JsonRpcRequest_V2(BaseModel):
    jsonrpc: str = Field("2.0")
    method: str
    params: list[Any] | dict[str, Any] | None = None
    id: JsonRpcIdType | None = Field(default=None)

    @field_validator('jsonrpc')
    @classmethod
    def check_jsonrpc_version_2_0(cls, v: str) -> str:
        if v != "2.0":
            raise ValueError('jsonrpc version for V2 request must be "2.0"')
        return v

class JsonRpcResponse_V2(BaseModel):
    jsonrpc: str = Field("2.0")
    result: Any | None = None
    error: JsonRpcErrorObject_V2 | None = None
    id: JsonRpcIdType

    @field_validator('jsonrpc')
    @classmethod
    def check_jsonrpc_version_2_0_response(cls, v: str) -> str:
        if v != "2.0":
            raise ValueError('jsonrpc version for V2 response must be "2.0"')
        return v

    @model_validator(mode='before')
    @classmethod
    def check_result_or_error_v2(cls, values: dict[str, Any]) -> dict[str, Any]:
        result_present = 'result' in values and values['result'] is not None
        error_present = 'error' in values and values['error'] is not None
        if result_present and error_present:
            raise ValueError('Both "result" and "error" cannot be present in a JSON-RPC 2.0 response.')
        if not result_present and not error_present:
            raise ValueError('Either "result" or "error" must be present in a JSON-RPC 2.0 response.')
        return values
```

### 2. JSON-RPC Server (`11_JSON_RPC/json_rpc_server.py`)

This FastAPI server handles JSON-RPC 1.0 and 2.0 requests on `/jsonrpc`. It uses a simple method registration system.

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Any, Callable

import uvicorn
import time
import json

from json_rpc_models import JsonRpcRequest_V2, JsonRpcResponse_V2, JsonRpcErrorObject_V2

app = FastAPI(title="JSON-RPC Server (1.0 and 2.0)", openapi_url=None)

RPC_METHODS_REGISTRY: dict[str, Callable[..., Any]] = {}

def rpc_method(name: str | None = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        method_name = name or func.__name__
        RPC_METHODS_REGISTRY[method_name] = func
        return func
    return decorator

@rpc_method()
async def echo(message: Any) -> Any:
    return message

@rpc_method()
async def add(a: int | float, b: int | float) -> int | float:
    return a + b

@rpc_method()
async def subtract(minuend: int | float, subtrahend: int | float) -> int | float:
    return minuend - subtrahend

@rpc_method()
async def get_server_time() -> str:
    return time.ctime()

@rpc_method()
async def trigger_error(message: str = "Default server error message from trigger_error method"):
    raise ValueError(message)

@rpc_method(name="notify_log")
async def handle_server_notification_log(message: str, source: str | None = "unknown_client_source") -> None:
    # This method is intended for notifications, so it returns None implicitly.
    print(f"[Server Notified] Source: {source}, Message: '{message}'")
    # For V1 id:null requests, server should respond with result:null, error:null, id:null
    # For V2 notifications, server doesn't respond. This return type helps clarify.

async def execute_rpc_method(func: Callable[..., Any], params: list[Any] | dict[str, Any] | None) -> Any:
    if isinstance(params, list):
        return await func(*params)
    elif isinstance(params, dict):
        return await func(**params)
    else: # No params
        return await func()

@app.post("/jsonrpc")
async def json_rpc_endpoint(request: Request) -> JSONResponse:
    raw_body = await request.body()
    try:
        payload_data = json.loads(raw_body)
    except json.JSONDecodeError:
        # Parse error, ID is unknown, respond with V2 error format
        err_v2 = JsonRpcErrorObject_V2(code=-32700, message="Parse error. Invalid JSON.")
        return JSONResponse(
            content=JsonRpcResponse_V2(error=err_v2, id=None).model_dump(exclude_none=True),
            status_code=200 # JSON-RPC errors are typically 200 OK with error in payload
        )

    if isinstance(payload_data, list): # Batch Request (JSON-RPC 2.0 style)
        responses: list[dict[str, Any]] = []
        if not payload_data: # Empty batch array
            err_v2 = JsonRpcErrorObject_V2(code=-32600, message="Invalid Request. Batch array was empty.")
            return JSONResponse(content=JsonRpcResponse_V2(error=err_v2, id=None).model_dump(exclude_none=True), status_code=200)

        is_all_v2_notifications = True
        for item_payload in payload_data:
            if not isinstance(item_payload, dict): # Non-dict item in batch
                err_v2 = JsonRpcErrorObject_V2(code=-32600, message="Invalid Request. Batch items must be objects.")
                responses.append(JsonRpcResponse_V2(error=err_v2, id=None).model_dump(exclude_none=True)) # Error for this item
                is_all_v2_notifications = False # Mark that we have something to respond with
                continue

            response_item_model = await process_single_rpc_call(item_payload)
            if response_item_model: # If not a V2 notification that shouldn't be responded to
                responses.append(response_item_model.model_dump(exclude_none=True))
                if not (item_payload.get("jsonrpc") == "2.0" and "id" not in item_payload):
                    is_all_v2_notifications = False
            elif not (item_payload.get("jsonrpc") == "2.0" and "id" not in item_payload):
                 # If process_single_rpc_call returned None, but it wasn't a V2 notification, it's an issue.
                 # This path should ideally not be hit if process_single_rpc_call is correct.
                 # For safety, consider it means something to respond about (e.g. an error in processing that became None)
                 is_all_v2_notifications = False


        if is_all_v2_notifications and not responses: # All were V2 notifications, and no errors added to responses
            return JSONResponse(content=responses, status_code=200)

    elif isinstance(payload_data, dict): # Single Request
        response_model = await process_single_rpc_call(payload_data)
        if response_model:
            return JSONResponse(content=response_model.model_dump(exclude_none=True), status_code=200)
        else: # V2 Notification processed, or an error occurred that resulted in None (should not happen)
              # This path implies a V2 notification was processed.
            return JSONResponse(content=[], status_code=200) # HTTP 204 No Content
    else: # Payload is not a list or dict
        err_fallback = JsonRpcErrorObject_V2(code=-32600, message="Invalid Request. Unrecognized RPC structure or missing required fields.")
        return JSONResponse(content=JsonRpcResponse_V2(error=err_fallback, id=None).model_dump(exclude_none=True), status_code=200)


async def process_single_rpc_call(payload: dict[str, Any]) -> JsonRpcResponse_V2:
    """Processes a single RPC call item. Returns a response model or None for V2 notifications."""

    req_id_from_payload = payload.get("id") # Get ID early for error responses or V1

    # --- JSON-RPC 2.0 Path ---
    if payload.get("jsonrpc") != "2.0":
        # Respond with V2 error format as it's more specific.
        err_fallback = JsonRpcErrorObject_V2(code=-32600, message="Invalid Request. Unrecognized RPC structure or missing required fields.")
        return JsonRpcResponse_V2(error=err_fallback, id=req_id_from_payload) # Use original ID if available, else None

    try:
        req = JsonRpcRequest_V2(**payload)
        # req.id will be None if "id" key was missing in payload (Pydantic default)
        # A true V2 notification has no "id" key in the raw payload.
        is_v2_notification = "id" not in payload

        if req.method not in RPC_METHODS_REGISTRY:
            if is_v2_notification: return None # No response for notifications
            err = JsonRpcErrorObject_V2(code=-32601, message=f"Method not found: {req.method}")
            return JsonRpcResponse_V2(error=err, id=req.id) # req.id will be correctly None or the value

        try:
            func = RPC_METHODS_REGISTRY[req.method]
            result = await execute_rpc_method(func, req.params)

            if is_v2_notification: return None
            return JsonRpcResponse_V2(result=result, id=req.id)

        except TypeError as e: # Mismatched arguments for the method
            if is_v2_notification: return None
            err = JsonRpcErrorObject_V2(code=-32602, message=f"Invalid params for method '{req.method}': {e}")
            return JsonRpcResponse_V2(error=err, id=req.id)
        except Exception as e: # Other errors during method execution
            if is_v2_notification: return None
            err = JsonRpcErrorObject_V2(code=-32000, message=f"Server error during method '{req.method}': {type(e).__name__} {e}")
            return JsonRpcResponse_V2(error=err, id=req.id)

    except Exception as ve_pydantic: # Pydantic validation error for JsonRpcRequest_V2
        # This indicates the request object itself was malformed per V2 spec (e.g. wrong jsonrpc version)
        err = JsonRpcErrorObject_V2(code=-32600, message=f"Invalid JSON-RPC 2.0 Request structure: {ve_pydantic}")
        # Use original payload's ID if possible for the response, even if request is invalid.
        # If "id" was part of the malformed request, use it. If not, id=None.
        return JsonRpcResponse_V2(error=err, id=req_id_from_payload)


if __name__ == "__main__":
    print("Starting JSON-RPC FastAPI server on http://127.0.0.1:8001/jsonrpc")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
```

**Run the server (ensure `json_rpc_models.py` is in the same directory or accessible via PYTHONPATH):**

```bash
uv run python json_rpc_server.py
```

### 3. JSON-RPC Client (`11_JSON_RPC/json_rpc_client.py`)

This client demonstrates sending various 1.0 and 2.0 requests. Ensure the server is running before executing the client.

```python
# Content of 11_JSON_RPC/json_rpc_client.py
import httpx
import asyncio
import json
import uuid
from typing import Any

SERVER_URL = "http://127.0.0.1:8001/jsonrpc"

async def send_rpc_request(payload: dict[str, Any] | list[dict[str, Any]], description: str = "") -> dict[str, Any] | list[dict[str, Any]] | None:
    print(f"\n--- Test: {description} ---")
    print(f"Client SENDING -> : {json.dumps(payload, indent=2)}")

    is_single_v2_notification = isinstance(payload, dict) and payload.get("jsonrpc") == "2.0" and "id" not in payload

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(SERVER_URL, json=payload)

            if is_single_v2_notification:
                if response.status_code == 204:
                    print(f"Client RECEIVED <- : V2 Notification OK (HTTP 204 No Content)")
                    return None
                else:
                    print(f"Client RECEIVED <- : UNEXPECTED for V2 Notification: Status {response.status_code}, Content: {response.text}")
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        return {"raw_response_text": response.text, "status_code": response.status_code}

            if response.status_code == 204:
                print(f"Client RECEIVED <- : HTTP 204 No Content (likely batch of notifications)")
                return None

            try:
                response_data = response.json()
                print(f"Client RECEIVED <- (Status {response.status_code}): {json.dumps(response_data, indent=2)}")
                return response_data
            except json.JSONDecodeError:
                print(f"Client RECEIVED <- (Status {response.status_code}, Non-JSON): {response.text}")
                return {"raw_response_text": response.text, "status_code": response.status_code}

    except httpx.HTTPStatusError as e:
        print(f"Client HTTPStatusError : {e.response.status_code} - {e.response.text}")
        try:
            return e.response.json()
        except json.JSONDecodeError:
            return {"error_detail": e.response.text, "status_code": e.response.status_code}
    except httpx.RequestError as e:
        print(f"Client RequestError : {e}")
        return {"error_type": type(e).__name__, "message": str(e)}
    except Exception as e:
        print(f"Client General Error: {type(e).__name__} - {e}")
        return {"error_type": type(e).__name__, "message": str(e)}

# --- Helper functions to create request payloads ---
def v2_req(method: str, params: list[Any] | dict[str, Any] | None = None, req_id: str | int | None = None) -> dict[str, Any]:
    payload_dict: dict[str, Any] = {"jsonrpc": "2.0", "method": method, "id": req_id if req_id is not None else str(uuid.uuid4())}
    if params is not None:
        payload_dict["params"] = params
    return payload_dict

def v2_not(method: str, params: list[Any] | dict[str, Any] | None = None) -> dict[str, Any]:
    payload_dict: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        payload_dict["params"] = params
    return payload_dict

async def main():
    print("--- JSON-RPC Client Demonstrations ---")

    # --- JSON-RPC 2.0 Examples ---
    print("\n=== JSON-RPC 2.0 Tests ===")
    await send_rpc_request(v2_req(method="echo", params=["Hello JSON-RPC 2.0!"], req_id="v2-echo-1"), "V2 Echo")
    await send_rpc_request(v2_req(method="add", params=[10, 5], req_id="v2-add-123"), "V2 Add")
    await send_rpc_request(v2_req(method="subtract", params={"minuend": 100, "subtrahend": 25}, req_id="v2-sub-456"), "V2 Subtract (Named Params)")
    await send_rpc_request(v2_req(method="get_server_time", req_id="v2-time-789"), "V2 Get Server Time")
    await send_rpc_request(v2_req(method="trigger_error", params=["Test V2 Error"], req_id="v2-error-000"), "V2 Trigger Server Error")
    await send_rpc_request(v2_req(method="non_existent_method", req_id="v2-notfound-111"), "V2 Non-existent Method")
    await send_rpc_request(v2_not(method="notify_log", params={"message": "Client V2 says hello!", "source": "ClientV2"}), "V2 Notification")

    # --- JSON-RPC 2.0 Batch Test ---
    print("\n--- JSON-RPC 2.0 Batch Test ---")
    batch_v2_payload = [
        v2_req(method="echo", params=["Batch V2 item 1 (echo)"], req_id="b-v2-1"),
        v2_not(method="notify_log", params={"message": "Batch V2 notification (notify_log)", "source": "BatchClient"}),
        v2_req(method="add", params=[99, 1], req_id="b-v2-2"),
        v2_req(method="non_existent_method", req_id="b-v2-error"),
        {"jsonrpc": "2.0", "method": "malformed_in_batch_no_id_request"}  # Malformed V2 (missing ID for a request)
    ]
    await send_rpc_request(batch_v2_payload, "V2 Batch Request")

    # --- Malformed / Edge Cases ---
    print("\n\n=== Malformed/Edge Case Tests ===")
    print("\n--- Test: Invalid JSON String ---")
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            raw_resp = await client.post(SERVER_URL, content="{this is not json...}", headers={"Content-Type": "application/json"})
            try:
                response_data = raw_resp.json()
                print(f"Client RECEIVED <- (Status {raw_resp.status_code}): {json.dumps(response_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Client RECEIVED <- (Status {raw_resp.status_code}, Non-JSON): {raw_resp.text}")
        except Exception as e:
            print(f"Client General Error sending invalid JSON: {e}")

    await send_rpc_request({"jsonrpc": "2.1", "method": "echo", "params": ["test bad version"], "id": "bad-v2.1-version"}, "V2 Request with incorrect jsonrpc version string (2.1)")
    await send_rpc_request({"method": "echo_weird_no_id_no_version", "params": ["test weird request"]}, "Request with no ID and no jsonrpc version string")
    await send_rpc_request([], "Empty Batch Array")

if __name__ == "__main__":
    # Ensure server `json_rpc_server.py` is running first.
    # Then run this client: `uv run python json_rpc_client.py`
    asyncio.run(main())

```

**Run the client (after starting the server):**

```bash
python 11_JSON_RPC/json_rpc_client.py
```

---

## Strengths of JSON-RPC

- **Simplicity & Readability**: JSON is human-readable and easy to parse, aiding debugging and development.
- **Lightweight**: Minimal overhead compared to more verbose formats like XML (used in SOAP).
- **Interoperability**: Widely supported across programming languages and platforms due to JSON's ubiquity.
- **Clear Structure for RPC**: Provides a well-defined way to express method calls, parameters, results, and errors, especially in version 2.0.
- **Supports Notifications**: Allows for fire-and-forget messages (clear in 2.0, ambiguous in 1.0).
- **Transport Agnostic**: JSON-RPC itself only defines the payload format. It can be transported over various protocols like HTTP, WebSockets, TCP, stdio, etc.
- **Batching (2.0)**: Allows multiple calls to be sent in a single request, reducing network latency.

## Weaknesses/Considerations

- **Schema and Typing**: JSON itself is schema-less. While the JSON-RPC structure defines field names like `method`, `params`, `result`, `error`, the types and structure of `params` and `result` are application-defined. Robust systems often use an additional schema definition language (like JSON Schema, OpenAPI, or Protocol Buffers for gRPC which is an alternative to JSON-RPC) to define service interfaces.
- **No Built-in Security Features**: JSON-RPC does not define security mechanisms like authentication or authorization. These must be handled by the transport layer (e.g., HTTPS, OAuth over HTTP) or the application layer.
- **Error Handling Specificity (Beyond Codes)**: While JSON-RPC 2.0 standardizes error codes, detailed application-specific error information needs to be structured within the `error.data` field or by using the reserved server error code range.
- **Stateless**: Each request is independent. For stateful interactions, session management needs to be handled by the application or transport.
- **Discovery**: JSON-RPC does not specify a standard way for clients to discover available methods or their signatures (unlike, e.g., WSDL for SOAP or gRPC reflection). Systems often provide separate documentation or a meta-method for this.

## General Use Cases

- **Web APIs**: As an alternative to REST, especially when the interaction model is more about actions (procedures) than resources.
- **Microservices Communication**: For lightweight, synchronous inter-service calls.
- **Blockchain Interaction**: Many blockchain nodes (like Ethereum with its Geth client) expose a JSON-RPC API for interacting with the blockchain (e.g., sending transactions, querying state).
- **Desktop and Mobile Application Backends**: For client-server communication where a simple RPC mechanism is needed.
- **System Integration**: For simple machine-to-machine communication.
- **IoT (Internet of Things)**: For device-to-server or device-to-device communication where bandwidth and processing power might be limited.
- **Language Server Protocol (LSP)**: Used by IDEs and code editors to communicate with language servers for features like autocompletion, linting, etc. LSP messages are based on JSON-RPC.

## Relevance to DACA / Agent-to-Agent (A2A)

JSON-RPC's principles and structure are highly relevant for agentic systems like those envisioned by DACA, particularly for Agent-to-Agent (A2A) communication:

- **Structured Agent Commands**: JSON-RPC 2.0 provides a clean, standardized way to define "methods" (agent capabilities or actions) and "params" (arguments for those actions). This allows one agent to clearly instruct another.
- **Clear Outcomes & Error Handling**: The `result` and `error` objects (especially the well-defined V2 error object) offer a standardized mechanism for an agent to report the outcome of processing a command, including detailed error information if necessary.
- **Payload Format**: For A2A communication within frameworks like DACA, JSON-RPC can serve as the payload format over various transports. Whether agents communicate via direct HTTP calls (potentially managed by Dapr service invocation), messages over a Dapr pub/sub system, or other event-driven mechanisms, JSON-RPC provides a consistent message structure.
- **Interoperability**: If different agents are developed by different teams or even in different languages, a shared understanding of JSON-RPC as the communication contract simplifies integration.
- **Notifications for Asynchronous Tasks**: Agents can use JSON-RPC notifications to send fire-and-forget signals or trigger asynchronous tasks in other agents without needing an immediate response, fitting well with event-driven architectures.
- **Batching for Efficiency**: When an agent needs to make multiple requests to another agent (or a group of agents via a proxy), batching can reduce network overhead and latency.

Adopting JSON-RPC (preferably 2.0) for A2A payloads can promote consistency, simplify development, and improve debugging in complex multi-agent systems by providing a shared, well-understood protocol for interaction.

---

## Further Reading

- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification) (Official 2.0 Specification)
- [JSON-RPC 1.0 Specification (historical)](https://www.jsonrpc.org/specification_v1)
- [Differences between 1.0 and 2.0 (simple-is-better.org)](https://www.simple-is-better.org/rpc/#differences-between-1-0-and-2-0)
- Python Libraries:
  - [`json` module (built-in)](https://docs.python.org/3/library/json.html)
  - For building servers/clients with manual JSON-RPC handling: `FastAPI`, `Flask`, `aiohttp` (server-side) and `requests`, `httpx` (client-side).
  - Dedicated JSON-RPC libraries:
    - Server: [`jsonrpcserver`](https://jsonrpcserver.readthedocs.io/en/latest/), [`python-jsonrpc-server`](https://pypi.org/project/python-jsonrpc-server/)
    - Client: [`jsonrpcclient`](https://jsonrpcclient.readthedocs.io/en/latest/)
- [Wallarm: What is JSON-RPC?](https://www.wallarm.com/what/what-is-json-rpc) (Provides general context and use cases)
- [Language Server Protocol (LSP) Specification](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/) (Example of JSON-RPC in a widely used protocol)
