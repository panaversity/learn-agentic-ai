# gRPC

gRPC is a high-performance, open-source RPC framework developed by Google. It leverages HTTP/2 and Protocol Buffers to enable efficient, strongly-typed communication between microservices and distributed systems.

---

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

## Conceptual Overview

### What is gRPC?

gRPC is a modern, high-performance RPC framework that uses HTTP/2 for transport and Protocol Buffers for serialization. It enables strongly-typed, efficient, and scalable communication between distributed systems and microservices.

### Key Characteristics

- **HTTP/2 Transport:** Multiplexed streams, header compression, and binary framing.
- **Protocol Buffers:** Efficient, strongly-typed serialization.
- **Streaming:** Supports client, server, and bidirectional streaming.
- **Code Generation:** Generates client and server code from `.proto` files.

### Strengths

- **Performance:** Low latency, high throughput.
- **Strong Typing:** Compile-time checks and code generation.
- **Streaming:** Real-time, bidirectional communication.
- **Interoperability:** Multi-language support.

### Weaknesses

- **Complexity:** More setup than REST/JSON.
- **Learning Curve:** Requires understanding of Protocol Buffers and gRPC concepts.

### Use Cases in Agentic and Multi-Modal AI Systems

- **Microservices:** High-performance, strongly-typed service-to-service communication.
- **Streaming Data:** Real-time data feeds, logs, and telemetry.
- **APIs:** Efficient, scalable APIs for agentic systems.

### Place in the Protocol Stack

- **Layer:** Application Layer (OSI Layer 7)
- **Above:** Business logic, agent frameworks
- **Below:** HTTP/2, TCP

### Further Reading

- [gRPC Python Docs](https://grpc.io/docs/languages/python/)
- [Protocol Buffers Docs](https://developers.google.com/protocol-buffers)
- [gRPC Tutorials](https://grpc.io/docs/)

---

# Tutorial: Using Protocol Buffers and gRPC in Python with uv

This tutorial provides a comprehensive guide to using Protocol Buffers (protobuf) and gRPC in Python, leveraging `uv` as a modern Python package manager and runner for efficient dependency management and project setup. By the end, you'll have a working client-server application using gRPC for communication and Protocol Buffers for data serialization.

gRPC adoption has grown significantly since its 2015 release, driven by its high performance, HTTP/2 transport, and Protocol Buffers, making it ideal for microservices, cloud-native applications, and IoT. Major adopters include Google, Netflix, Uber, and financial/gaming sectors, using gRPC for low-latency communication, streaming, and cross-language support. Its integration with Kubernetes and service meshes boosts its cloud appeal. While REST remains dominant for public APIs, gRPC excels in internal services. Future growth is expected with improved tooling, web support, and cloud integrations, but it's unlikely to replace REST entirely.

## Note: Dapr uses both HTTP and GRPC Protocols. To [enable GRPC for communication](https://docs.dapr.io/operations/configuration/grpc/) you can following this config guide.

## Prerequisites

- **Python**: Version 3.12 or higher.
- **uv**: A fast Python package manager and project runner (install via `curl -LsSf https://astral.sh/uv/install.sh | sh` or follow instructions at [astral.sh/uv](https://astral.sh/uv)).
- **Basic Knowledge**: Familiarity with Python and command-line tools.
- **Protobuf Compiler**: `protoc` for generating Python code from `.proto` files.
- **gRPC Tools**: Python packages for gRPC communication.

---

## Step 1: Project Setup with uv

`uv` simplifies Python project setup by managing dependencies, virtual environments, and scripts efficiently. Let's create a new project.

1. **Initialize the Project**:

   ```bash
   mkdir grpc-tutorial
   cd grpc-tutorial
   uv init
   ```

   This creates a basic project structure with a `pyproject.toml` file.

2. **Add Dependencies**:
   Add the required Python packages for gRPC and Protocol Buffers:

   ```bash
   uv add grpcio grpcio-tools
   ```

   This updates `pyproject.toml` and installs `grpcio` (gRPC runtime) and `grpcio-tools` (for generating Python code from `.proto` files) into a virtual environment managed by `uv`.

3. **Verify Setup**:
   Check the installed packages:

   ```bash
   uv pip list
   ```

   You should see `grpcio` and `grpcio-tools` listed.

4. **Install `protoc`**:
   The Protocol Buffers compiler (`protoc`) is required to compile `.proto` files. Install it based on your operating system:

   - **Linux**:
     ```bash
     sudo apt-get install protobuf-compiler
     ```
   - **macOS**:
     ```bash
     brew install protobuf
     ```
   - **Windows**:
     Download the binary from [GitHub](https://github.com/protocolbuffers/protobuf/releases) and add it to your PATH.

   Verify installation:

   ```bash
   protoc --version
   ```

---

## Step 2: Define the Protocol Buffers Schema

Protocol Buffers define the structure of your data in a `.proto` file. We'll create a simple service for managing user information.

1. **Create a `.proto` File**:
   Create a directory for proto files and define the schema:

   ```bash
   mkdir proto
   touch proto/user.proto
   ```

   Edit `proto/user.proto` with the following content:

   ```proto
   syntax = "proto3";

   package user;

   // User message defines the structure of a user
   message User {
       int32 id = 1;
       string name = 2;
       string email = 3;
   }

   // Request message for getting a user
   message GetUserRequest {
       int32 id = 1;
   }

   // Response message for getting a user
   message GetUserResponse {
       User user = 1;
   }

   // UserService defines the gRPC service
   service UserService {
       // GetUser retrieves a user by ID
       rpc GetUser(GetUserRequest) returns (GetUserResponse);
   }
   ```

   This defines:

   - A `User` message with `id`, `name`, and `email` fields.
   - A `GetUserRequest` message to specify a user ID.
   - A `GetUserResponse` message to return a `User`.
   - A `UserService` with a `GetUser` RPC method.

Note: The numbers in proto file are field numbers (also called tags) and do not specify the sequence or order of fields in the serialized data. Instead, they serve as unique identifiers for each field in the message.

2. **Compile the `.proto` File**:
   Use `protoc` to generate Python code:

   ```bash
   uv run python -m grpc_tools.protoc -Iproto --python_out=. --grpc_python_out=. proto/user.proto
   ```

   This generates two files in the project root:

   - `user_pb2.py`: Contains Python classes for the messages (e.g., `User`, `GetUserRequest`).
   - `user_pb2_grpc.py`: Contains gRPC service stubs and server classes.

   **Note**: The `-Iproto` flag specifies the input directory for `.proto` files, `--python_out` generates message classes, and `--grpc_python_out` generates gRPC service code.

---

## Step 3: Implement the gRPC Server

Create a server that implements the `UserService` defined in the `.proto` file.

1. **Create the Server File**:

   ```bash
   touch server.py
   ```

   Edit `server.py` with the following content:

   ```python
   import grpc
   from concurrent import futures
   import user_pb2
   import user_pb2_grpc

   class UserService(user_pb2_grpc.UserServiceServicer):
       def GetUser(self, request, context):
           # Simulate fetching a user from a database
           user_id = request.id
           if user_id == 1:
               user = user_pb2.User(
                   id=1,
                   name="John Doe",
                   email="john@example.com"
               )
               return user_pb2.GetUserResponse(user=user)
           else:
               context.set_code(grpc.StatusCode.NOT_FOUND)
               context.set_details("User not found")
               return user_pb2.GetUserResponse()

   def serve():
       server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
       user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
       server.add_insecure_port('[::]:50051')
       print("Server started on port 50051")
       server.start()
       server.wait_for_termination()

   if __name__ == "__main__":
       serve()
   ```

   This code:

   - Defines a `UserService` class that inherits from `user_pb2_grpc.UserServiceServicer`.
   - Implements the `GetUser` method to return a hardcoded user for ID 1 or a "not found" error for other IDs.
   - Sets up a gRPC server listening on port 50051.

2. **Run the Server**:
   Use `uv` to run the server:

   ```bash
   uv run python server.py
   ```

   The server starts and listens on `localhost:50051`. Keep it running.

---

## Step 4: Implement the gRPC Client

Create a client to interact with the server.

1. **Create the Client File**:

   ```bash
   touch client.py
   ```

   Edit `client.py` with the following content:

   ```python
   import grpc
   import user_pb2
   import user_pb2_grpc

   def main():
       # Create a gRPC channel
       with grpc.insecure_channel('localhost:50051') as channel:
           # Create a stub (client)
           stub = user_pb2_grpc.UserServiceStub(channel)

           # Make a GetUser request
           request = user_pb2.GetUserRequest(id=1)
           try:
               response = stub.GetUser(request)
               if response.user.id:
                   print(f"User found: ID={response.user.id}, Name={response.user.name}, Email={response.user.email}")
               else:
                   print("User not found")
           except grpc.RpcError as e:
               print(f"Error: {e.details()}")

   if __name__ == "__main__":
       main()
   ```

   This code:

   - Connects to the server at `localhost:50051`.
   - Creates a stub for the `UserService`.
   - Sends a `GetUserRequest` for user ID 1 and prints the response.

2. **Run the Client**:
   In a new terminal (with the server still running), activate the virtual environment and run the client:

   ```bash
   uv run python client.py
   ```

   **Output**:

   ```
   User found: ID=1, Name=John Doe, Email=john@example.com
   ```

   Try modifying the client to request a different ID (e.g., `request = user_pb2.GetUserRequest(id=2)`) and run again:

   ```
   Error: User not found
   ```

---

## Step 5: Enhance the Project

Let's add more functionality to make the service more realistic.

1. **Update the `.proto` File**:
   Add a `ListUsers` RPC to retrieve multiple users. Edit `proto/user.proto`:

   ```proto
   syntax = "proto3";

   package user;

   message User {
       int32 id = 1;
       string name = 2;
       string email = 3;
   }

   message GetUserRequest {
       int32 id = 1;
   }

   message GetUserResponse {
       User user = 1;
   }

   // New message for listing users
   message ListUsersRequest {}

   message ListUsersResponse {
       repeated User users = 1;
   }

   service UserService {
       rpc GetUser(GetUserRequest) returns (GetUserResponse);
       // New RPC for listing users
       rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
   }
   ```

   The `repeated` keyword in `ListUsersResponse` indicates a list of `User` objects.

2. **Recompile the `.proto` File**:

   ```bash
   uv run python -m grpc_tools.protoc -Iproto --python_out=. --grpc_python_out=. proto/user.proto
   ```

   This updates `user_pb2.py` and `user_pb2_grpc.py`.

3. **Update the Server**:
   Modify `server.py` to implement `ListUsers`:

   ```python
   import grpc
   from concurrent import futures
   import user_pb2
   import user_pb2_grpc

   class UserService(user_pb2_grpc.UserServiceServicer):
       def GetUser(self, request, context):
           user_id = request.id
           if user_id == 1:
               user = user_pb2.User(
                   id=1,
                   name="John Doe",
                   email="john@example.com"
               )
               return user_pb2.GetUserResponse(user=user)
           else:
               context.set_code(grpc.StatusCode.NOT_FOUND)
               context.set_details("User not found")
               return user_pb2.GetUserResponse()

       def ListUsers(self, request, context):
           # Simulate a list of users
           users = [
               user_pb2.User(id=1, name="John Doe", email="john@example.com"),
               user_pb2.User(id=2, name="Jane Smith", email="jane@example.com"),
           ]
           return user_pb2.ListUsersResponse(users=users)

   def serve():
       server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
       user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
       server.add_insecure_port('[::]:50051')
       print("Server started on port 50051")
       server.start()
       server.wait_for_termination()

   if __name__ == "__main__":
       serve()
   ```

4. **Update the Client**:
   Modify `client.py` to test `ListUsers`:

   ```python
   import grpc
   import user_pb2
   import user_pb2_grpc

   def main():
       with grpc.insecure_channel('localhost:50051') as channel:
           stub = user_pb2_grpc.UserServiceStub(channel)

           # Test GetUser
           print("Testing GetUser:")
           request = user_pb2.GetUserRequest(id=1)
           try:
               response = stub.GetUser(request)
               if response.user.id:
                   print(f"User found: ID={response.user.id}, Name={response.user.name}, Email={response.user.email}")
               else:
                   print("User not found")
           except grpc.RpcError as e:
               print(f"Error: {e.details()}")

           # Test ListUsers
           print("\nTesting ListUsers:")
           request = user_pb2.ListUsersRequest()
           try:
               response = stub.ListUsers(request)
               for user in response.users:
                   print(f"User: ID={user.id}, Name={user.name}, Email={user.email}")
           except grpc.RpcError as e:
               print(f"Error: {e.details()}")

   if __name__ == "__main__":
       main()
   ```

5. **Test the Updated Service**:
   Restart the server:

   ```bash
   uv run python server.py
   ```

   Run the client:

   ```bash
   uv run python client.py
   ```

   **Output**:

   ```
   Testing GetUser:
   User found: ID=1, Name=John Doe, Email=john@example.com

   Testing ListUsers:
   User: ID=1, Name=John Doe, Email=john@example.com
   User: ID=2, Name=Jane Smith, Email=jane@example.com
   ```

---

## Step 6: Best Practices and Optimizations

1. **Use `uv` Scripts**:
   Add scripts to `pyproject.toml` for convenience:

   ```toml
   [project]
   name = "grpc-tutorial"
   version = "0.1.0"
   dependencies = [
       "grpcio",
       "grpcio-tools",
   ]

   [project.scripts]
   start-server = "python server.py"
   start-client = "python client.py"
   compile-proto = "python -m grpc_tools.protoc -Iproto --python_out=. --grpc_python_out=. proto/user.proto"
   ```

   Now you can run:

   ```bash
   uv run start-server
   uv run start-client
   uv run compile-proto
   ```

2. **Error Handling**:
   Enhance error handling in the server by adding validation:

   ```python
   def GetUser(self, request, context):
       if request.id <= 0:
           context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
           context.set_details("Invalid user ID")
           return user_pb2.GetUserResponse()
       # ... rest of the code
   ```

3. **Secure gRPC**:
   For production, use SSL/TLS:

   - Generate certificates and configure the server with `server.add_secure_port`.
   - Update the client to use `grpc.secure_channel`.

4. **Performance**:

   - Use connection pooling for clients in production.
   - Optimize the thread pool size in `futures.ThreadPoolExecutor` based on your workload.

5. **Organize Code**:
   Move generated `.py` files to a `generated` directory and update imports:

   ```bash
   mkdir generated
   mv user_pb2*.py generated/
   ```

   Update `server.py` and `client.py`:

   ```python
   import grpc
   from concurrent import futures
   from generated import user_pb2
   from generated import user_pb2_grpc
   ```

   Update the `compile-proto` command in `pyproject.toml`:

   ```toml
   compile-proto = "python -m grpc_tools.protoc -Iproto --python_out=generated --grpc_python_out=generated proto/user.proto"
   ```

---

## Step 7: Deploying with uv

To package and deploy the application:

1. **Create a Wheel**:

   ```bash
   uv build
   ```

   This creates a `.whl` file in the `dist` directory.

2. **Install on Another Machine**:
   Copy the `.whl` file and install it:

   ```bash
   uv pip install grpc_tutorial-0.1.0-py3-none-any.whl
   ```

3. **Run in Production**:
   Use a process manager like `gunicorn` or `systemd` to manage the gRPC server. Ensure `protoc` and dependencies are installed.

---

## Conclusion

You've built a gRPC service with Protocol Buffers in Python, using `uv` for efficient project management. The tutorial covered:

- Setting up a project with `uv`.
- Defining and compiling a `.proto` file.
- Implementing a gRPC server and client.
- Adding new functionality and organizing code.
- Best practices for production.

Explore advanced gRPC features like streaming, authentication, or integrating with a database to enhance your application further.

**Resources**:

- [gRPC Python Documentation](https://grpc.io/docs/languages/python/)
- [Protocol Buffers Documentation](https://developers.google.com/protocol-buffers)
- [uv Documentation](https://docs.astral.sh/uv/)
