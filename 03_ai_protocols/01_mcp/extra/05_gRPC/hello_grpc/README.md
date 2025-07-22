## Working with gRPC in Python: grpcio

- [`grpcio`](https://grpc.io/docs/languages/python/) is the official Python library for gRPC.
- [`grpcio-tools`](https://pypi.org/project/grpcio-tools/) is used to generate Python code from `.proto` files.

### Installation

```bash
uv init hello_grpc
cd hello_grpc
uv add grpcio grpcio-tools
```

### Example 1: Basic gRPC Server & Client

#### 1. Define the Protocol Buffers schema (`helloworld.proto`):

```proto
syntax = "proto3";

package helloworld;

service Greeter {
  rpc SayHello (HelloRequest) returns (HelloReply) {}
}

message HelloRequest {
  string name = 1;
}

message HelloReply {
  string message = 1;
}
```

#### 2. Generate Python code:

```bash
uv run python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. helloworld.proto
```

#### 3. gRPC Server (`server.py`):

```python
import grpc
from concurrent import futures
import helloworld_pb2
import helloworld_pb2_grpc

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        return helloworld_pb2.HelloReply(message=f"Hello, {request.name}!")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server running on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
```

#### 4. gRPC Client (`client.py`):

```python
import grpc
import helloworld_pb2
import helloworld_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(helloworld_pb2.HelloRequest(name='Agentic AI'))
        print(f"Greeter client received: {response.message}")

if __name__ == "__main__":
    run()
```

---

```bash
uv run python server.py
uv run python client.py
```