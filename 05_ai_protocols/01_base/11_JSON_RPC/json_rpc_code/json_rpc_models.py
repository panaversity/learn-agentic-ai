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