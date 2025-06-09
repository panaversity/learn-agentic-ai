# Content of 11_JSON_RPC/json_rpc_models.py
from pydantic import BaseModel
from typing import Any

class Request(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Any = None
    id: Any = None

class Response(BaseModel):
    jsonrpc: str = "2.0"
    result: Any = None
    error: dict | None = None
    id: Any = None