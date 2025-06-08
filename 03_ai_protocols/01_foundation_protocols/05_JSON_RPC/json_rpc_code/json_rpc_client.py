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