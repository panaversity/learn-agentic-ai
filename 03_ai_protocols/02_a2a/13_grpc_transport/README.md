# gRPC Transport - Implementing A2A Communication with gRPC 🚀

**Build an agent that communicates using the gRPC transport protocol as defined in the A2A specification. This involves setting up a gRPC server and client to handle agent-to-agent interactions, supporting tasks like message sending, task management, and artifact exchange.**

> **🎯 Learning Goal**: Learn how to implement A2A communication using gRPC, including defining services with Protocol Buffers, handling task lifecycles, and ensuring functional equivalence with other A2A transports (e.g., JSON-RPC). Understand how to leverage gRPC’s high-performance, low-latency features for efficient agent interactions.

## 🧠 Why This Matters for Learning

### **Why gRPC for A2A?**
- **High Performance**: gRPC uses HTTP/2 and Protocol Buffers for efficient, low-latency communication, ideal for scalable agent systems.
- **Strong Typing**: Protocol Buffers provide strict data contracts, ensuring reliable message exchange between agents.
- **Interoperability**: gRPC is one of A2A’s core transport protocols, ensuring compatibility with other A2A-compliant agents.
- **Streaming Support**: gRPC’s server streaming enables real-time task updates, aligning with A2A’s `message/stream` and `tasks/resubscribe` methods.

### **Keeping It Practical**
- **Functional Equivalence**: Implement gRPC methods that mirror JSON-RPC methods (e.g., `message/send`, `tasks/get`), ensuring consistent behavior across transports.
- **Agent Card Integration**: Declare gRPC support in the Agent Card for discovery and transport negotiation.
- **Task Management**: Handle task lifecycles (e.g., `submitted`, `working`, `completed`) and artifacts using gRPC’s structured messages.

## 🚀 How to Build gRPC-Based A2A Agents

This is a standalone example demonstrating how to build an A2A-compliant agent using gRPC as the transport protocol, based on the A2A specification ([gRPC Transport](https://a2a-protocol.org/latest/specification/#322-grpc-transport)). The agent handles text-based tasks (e.g., answering queries) and supports the core A2A methods (`message/send`, `tasks/get`, `tasks/cancel`) via gRPC.

### Task Lifecycle Explained Simply
1. **Client Sends Message**: Using the gRPC `SendMessage` method (equivalent to JSON-RPC `message/send`) with a `Message` object containing `TextPart` data.
2. **Agent Processes Input**:
   - Validates the input and creates a task with a unique `taskId` and `contextId`.
   - Maps gRPC request fields to A2A data structures using `json_name` annotations for compatibility.
3. **Task States**:
   - **Submitted**: Task is queued for execution.
   - **Working**: Agent is processing the task (e.g., generating a response).
   - **Input-Needed**: Agent pauses for user clarification (e.g., ambiguous query).
   - **Completed**: Task finishes, returning artifacts (e.g., a text response).
   - **Failed/Canceled**: Task fails or is canceled by the client.
4. **Returning Results**: Agent responds with a `Task` object containing artifacts, using gRPC’s structured response format.
5. **Follow-Ups**: Clients send follow-up requests with the same `contextId` but new `taskId` for related tasks.
6. **Streaming**: For methods like `message/stream`, gRPC server streaming delivers real-time task updates.

This example uses a **Simple Query Agent** that answers user questions (e.g., "What’s the capital of France?") via gRPC, returning responses as text artifacts and supporting task state management.

### Key Files
1. **a2a.proto**: Protocol Buffers definition for the A2A gRPC service, based on the normative `specification/grpc/a2a.proto` from the A2A spec.
2. **query_agent.py**: Defines the Simple Query Agent, which processes text queries and generates text-based artifacts (e.g., answers to questions).
3. **agent_executor.py**: Custom AgentExecutor that bridges A2A task logic to the gRPC service, handling task persistence, state updates, and artifact generation.
4. **server.py**: gRPC server implementing the `A2AService` from `a2a.proto`, using `InMemoryTaskStore` (or SQLite) for task persistence.
5. **client.py**: gRPC client script to simulate interactions, sending queries and receiving task updates via gRPC methods.
6. **conversations.db**: SQLite database for persisting task and session states (managed by `SQLiteSession`).

### How to Demo
- **Scenario**: User asks, "What’s the capital of France?" via the gRPC `SendMessage` method.
- **Agent Response**: Creates a task, processes the query, and returns a `completed` task with a text artifact ("The capital of France is Paris").
- **Follow-Up**: User asks, "Tell me about Paris," using the same `contextId` but a new `taskId`.

### Setup and Running
1. **Install Dependencies**:
   ```bash
   uv sync
   ```
   Installs `a2a-sdk[grpc]`, `grpcio`, `grpcio-tools`, and other dependencies.
2. **Generate gRPC Code**:
   ```bash
   python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. a2a.proto
   ```
   Generates `a2a_pb2.py` and `a2a_pb2_grpc.py` from `a2a.proto`.
3. **Run the Server**:
   ```bash
   uv run server.py
   ```
   Starts the gRPC server at `localhost:50051` (or as specified in the Agent Card).
4. **Simulate Client Interactions**:
   - Initial query:
     ```bash
     uv run client.py --query "What’s the capital of France?"
     ```
     Agent responds with a `Task` containing the answer.
   - Follow-up query:
     ```bash
     uv run client.py --query "Tell me about Paris" --context-id <contextId>
     ```
5. **Monitor Logs**: Check task state transitions (e.g., `submitted` → `working` → `completed`) and artifact updates in the server logs.

### Code Highlights
#### a2a.proto (Protocol Buffers Definition)
```proto
syntax = "proto3";

package a2a;

service A2AService {
  rpc SendMessage (MessageSendParams) returns (Task) {}
  rpc GetTask (TaskQueryParams) returns (Task) {}
  rpc CancelTask (TaskIdParams) returns (Task) {}
  rpc SendStreamingMessage (MessageSendParams) returns (stream SendStreamingMessageResponse) {}
}

message MessageSendParams {
  Message message = 1 [(google.api.field_behavior) = REQUIRED];
  MessageSendConfiguration configuration = 2;
  map<string, google.protobuf.Any> metadata = 3;
}

message Task {
  string id = 1 [(google.api.field_behavior) = REQUIRED];
  string context_id = 2 [(google.api.field_behavior) = REQUIRED];
  TaskStatus status = 3 [(google.api.field_behavior) = REQUIRED];
  repeated Message history = 4;
  repeated Artifact artifacts = 5;
  map<string, google.protobuf.Any> metadata = 6;
  string kind = 7 [(google.api.field_behavior) = REQUIRED, (json_name) = "kind"];
}

message Message {
  string role = 1 [(google.api.field_behavior) = REQUIRED];
  repeated Part parts = 2 [(google.api.field_behavior) = REQUIRED];
  map<string, google.protobuf.Any> metadata = 3;
  repeated string extensions = 4;
  repeated string reference_task_ids = 5;
  string message_id = 6 [(google.api.field_behavior) = REQUIRED];
  string task_id = 7;
  string context_id = 8;
  string kind = 9 [(google.api.field_behavior) = REQUIRED, (json_name) = "kind"];
}

// Additional message definitions for Part, TaskStatus, Artifact, etc.
```

#### agent_executor.py (Handling gRPC Requests)
```python
from a2a_pb2 import Task, TaskStatus, Artifact, Part, TextPart
from a2a_pb2_grpc import A2AServiceServicer
from a2a_sdk import TaskUpdater, InMemoryTaskStore

class A2AServiceImpl(A2AServiceServicer):
    def __init__(self):
        self.task_store = InMemoryTaskStore()
        self.agent = QueryAgent()

    async def SendMessage(self, request, context):
        task_id = str(uuid.uuid4())
        context_id = request.message.context_id or str(uuid.uuid4())
        updater = TaskUpdater(self.task_store, task_id, context_id)

        # Start task
        await updater.start_work()
        
        # Process user input
        user_input = next((part.text for part in request.message.parts if part.kind == "text"), "")
        if not user_input:
            await updater.update_status(
                state="input-required",
                message=Message(
                    role="agent",
                    parts=[Part(kind="text", text="Please provide a valid query.")],
                    message_id=str(uuid.uuid4()),
                    task_id=task_id,
                    context_id=context_id
                )
            )

        # Process query
        result = await self.agent.process_query(user_input)
        await updater.add_artifact(
            parts=[Part(kind="text", text=result)],
            name="query_response"
        )
        await updater.complete()
```

#### client.py (Sending gRPC Requests)
```python
import grpc
from a2a_pb2 import MessageSendParams, Message, Part, TextPart
from a2a_pb2_grpc import A2AServiceStub
import uuid

async def send_query(query, context_id=None):
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = A2AServiceStub(channel)
        request = MessageSendParams(
            message=Message(
                role="user",
                parts=[Part(kind="text", text=query)],
                message_id=str(uuid.uuid4()),
                context_id=context_id or str(uuid.uuid4())
            )
        )
        response = await stub.SendMessage(request)
        print(f"Task ID: {response.id}, Status: {response.status.state}")
        for artifact in response.artifacts:
            for part in artifact.parts:
                if part.kind == "text":
                    print(f"Response: {part.text}")

# Example usage
asyncio.run(send_query("What’s the capital of France?"))
```

### Example Interaction
1. **Client Request (SendMessage)**:
   ```proto
   message {
     role: "user"
     parts: [
       { kind: "text", text: "What’s the capital of France?" }
     ]
     message_id: "msg-001"
     context_id: "ctx-001"
   }
   ```
2. **Agent Response (Task)**:
   ```proto
   id: "task-001"
   context_id: "ctx-001"
   status: { state: "completed", timestamp: "2025-08-15T16:52:00Z" }
   artifacts: [
     {
       artifact_id: "artifact-001"
       name: "query_response"
       parts: [
         { kind: "text", text: "The capital of France is Paris." }
       ]
     }
   ]
   kind: "task"
   ```

---

## 📖 Key Takeaway

**Remember**: gRPC enables high-performance, strongly-typed A2A communication, making it ideal for scalable, efficient agent interactions. By mastering gRPC transport, you can build robust, interoperable agents that align with A2A’s core principles! 🚀

### Concepts Demonstrated
- **gRPC Transport**: Implement A2A methods (`SendMessage`, `GetTask`, etc.) using gRPC services defined in Protocol Buffers.
- **Task Lifecycle**: Manage task states (`submitted`, `working`, `completed`) and artifacts in gRPC responses.
- **Functional Equivalence**: Ensure gRPC methods mirror JSON-RPC behavior for interoperability.
- **Agent Card**: Declare gRPC support in the Agent Card for transport discovery.

### Ideas Shown
- **Protocol Buffers**: Define A2A services and messages with strict typing.
- **gRPC Server/Client**: Set up a gRPC server for task processing and a client for sending requests.
- **Streaming**: Support real-time updates with gRPC server streaming for `SendStreamingMessage`.
- **Task Persistence**: Store task states to support multi-turn interactions.

### Resources to Learn More
- [A2A Specification: gRPC Transport](https://a2a-protocol.org/latest/specification/#322-grpc-transport)
- [A2A Task Lifecycle](https://a2a-protocol.org/latest/topics/life-of-a-task/)
- [gRPC Python Documentation](https://grpc.io/docs/languages/python/)
- [Protocol Buffers](https://developers.google.com/protocol-buffers)