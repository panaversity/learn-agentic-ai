from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Any, Callable

import uvicorn
import time
import json

from json_rpc_models import JsonRpcRequest_V2, JsonRpcResponse_V2, JsonRpcErrorObject_V2

app = FastAPI(title="JSON-RPC Server (1.0 and 2.0)")

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