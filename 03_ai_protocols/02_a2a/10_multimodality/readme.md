# Multimodality - Handling Text and Files in A2A Interactions 📸📝

**Build an agent that can process and generate multiple data types, such as text and images, using A2A protocols. This involves handling file uploads (e.g., images), processing them, and returning results like modified files or text-based analysis, all within a multi-turn conversation.**

> **🎯 Learning Goal**: Learn how to implement multimodal interactions in A2A communication, enabling agents to handle diverse data types (text, images, etc.) seamlessly. Understand how to use `FilePart` for uploading and downloading files, manage tasks with artifacts, and maintain context across multimodal interactions for collaborative agent-human or agent-agent systems.

## 🧠 Why This Matters for Learning

### **How Multimodality Enhances A2A**
- **Diverse Data Handling**: Agents can process and generate multiple data types (e.g., text queries, image inputs, or file outputs), enabling richer interactions.
- **Task Lifecycle with Files**: Manage tasks that involve file uploads (e.g., images for analysis) and downloads (e.g., processed images), using A2A’s `FilePart` and artifact system.
- **Real-World Applications**: Multimodality is key for applications like image analysis, content generation, or cross-modal tasks (e.g., describing an image or modifying it based on text instructions).

### **Keeping It Practical**
- **File Exchange**: Use `FilePart` to upload files (e.g., base64-encoded images) and return results as artifacts (e.g., URIs or bytes for processed files).
- **Context Continuity**: Leverage `contextId` to link related tasks (e.g., analyzing an image and generating a modified version) in a conversation.
- **Human-Agent Collaboration**: Combine text and file inputs to support interactive workflows, such as clarifying image-based tasks with text.

## 🚀 How to Build Multimodal Agents

This is a standalone example demonstrating how to build an agent that handles multimodal inputs and outputs using A2A protocols. The agent processes a user’s text query and an uploaded file (e.g., an image), performs a task (e.g., analyzing or modifying the image), and returns results as artifacts (e.g., a processed image or text description). The example builds on the A2A file exchange specification ([A2A File Exchange](https://a2a-protocol.org/latest/specification/#96-file-exchange-upload-and-download)).

### Task Lifecycle Explained Simply
1. **Client Sends Message**: Using `message/send` with a `TextPart` (e.g., "Analyze this image") and a `FilePart` (e.g., an image file in base64).
2. **Agent Processes Input**:
   - Validates the input (e.g., checks if the image and text are valid).
   - Creates a task with a unique `taskId` and `contextId` for tracking.
3. **Task States**:
   - **Working**: Agent processes the input (e.g., analyzes the image).
   - **Input-Needed**: If clarification is needed (e.g., missing details like "Which part of the image to analyze?"), pause and request user input.
   - **Completed**: Task finishes, returning results as artifacts (e.g., a modified image or text analysis).
   - **Failed/Canceled**: Task fails due to invalid input or errors.
4. **Returning Results**: Agent responds with artifacts (e.g., a `FilePart` with a processed image’s URI or bytes) linked to the same `contextId`.
5. **Follow-Ups**: For related tasks (e.g., generating a new image based on prior results), use the same `contextId` with a new `taskId`.
6. **End**: Once completed or failed, the task is immutable; new tasks are created for further actions.

This example uses an **Image Processing Agent**. The user uploads an image with a text query (e.g., "Highlight faces in this image"). The agent processes the image, returns a modified version (e.g., with faces highlighted), and supports follow-up requests (e.g., "Now make the image grayscale").

### Key Files
1. **image_agent.py**: Defines the Image Processing Agent, which handles text and image inputs, processes images (e.g., using a library like OpenCV or a vision model), and generates artifacts (e.g., modified images).
2. **agent_executor.py**: Custom AgentExecutor that integrates A2A with a multimodal processing framework (e.g., OpenAI Agents SDK or a vision model API). It validates inputs, manages task states, and uses `TaskUpdater` to update task status and artifacts.
3. **server.py**: A2A FastAPI server using `DefaultRequestHandler` and `InMemoryTaskStore` (or SQLite) for task persistence. It handles file uploads/downloads and streams task updates.
4. **client.py**: A client script to simulate multimodal interactions: uploading an image with a text query, receiving processed results, and sending follow-up requests with the same `contextId`.
5. **conversations.db**: SQLite database for persisting task and session states across multimodal interactions (managed by `SQLiteSession`).

### How to Demo
- User sends: "Highlight faces in this image" with an image file (`input_image.png`).
- Agent creates a task, processes the image, and responds with a `completed` task containing an artifact (e.g., `processed_image_with_faces.png` via URI or bytes).
- User follows up: "Make the image grayscale" using the same `contextId` but a new `taskId`.
- Agent generates a new artifact (e.g., `grayscale_image.png`) and completes the task.

### Setup and Running
1. **Install Dependencies**:
   ```bash
   uv sync
   ```
   Installs `a2a-sdk[http-server]`, `openai-agents`, and image processing libraries (e.g., `opencv-python` or `pillow`).
2. **Run the Server**:
   ```bash
   uv run server.py
   ```
   Exposes the A2A endpoint at `http://localhost:8001`.
3. **Simulate Client Interactions**:
   - Initial query:
     ```bash
     uv run client.py --query "Highlight faces in this image" --file "input_image.png"
     ```
     Agent responds with a `completed` task and a processed image artifact.
   - Follow-up query:
     ```bash
     uv run client.py --query "Make the image grayscale" --context-id <contextId> --task-id <newTaskId>
     ```
4. **Monitor Logs**: Check task state transitions (e.g., `working` → `completed`) and artifact updates in the server logs.

### Code Highlights
In `agent_executor.py`, handle multimodal input and artifact generation:

```python
async def execute(self, context: RequestContext, event_queue: EventQueue):
    updater = TaskUpdater(event_queue, context.task_id, context.context_id)
    await updater.start_work()

    user_input = context.get_user_input()
    text_part = next((part for part in user_input.parts if part.kind == "text"), None)
    file_part = next((part for part in user_input.parts if part.kind == "file"), None)

    if not text_part or not file_part:
        await updater.update_status(
            TaskState.input_required,
            message=updater.new_agent_message([
                Part(root=TextPart(text="Please provide both a text query and an image file."))
            ])
        )
        return  # Pause task

    # Process image (e.g., highlight faces using a vision model or library)
    processed_image = await self.agent.process_image(
        text=text_part.text,
        image_bytes=file_part.file.bytes,
        mime_type=file_part.file.mimeType
    )

    # Return processed image as an artifact
    await updater.add_artifact(
        parts=[
            Part(root=FilePart(
                name="processed_image.png",
                mimeType="image/png",
                bytes=processed_image  # Base64-encoded processed image
            ))
        ],
        name="processed_image"
    )
    await updater.complete()
```

In `client.py`, send a multimodal message:

```python
import base64

# Read image and encode to base64
with open("input_image.png", "rb") as f:
    image_bytes = base64.b64encode(f.read()).decode("utf-8")

response = send_message(
    message={
        "role": "user",
        "parts": [
            {"kind": "text", "text": "Highlight faces in this image"},
            {"kind": "file", "file": {"name": "input_image.png", "mimeType": "image/png", "bytes": image_bytes}}
        ]
    },
    context_id="ctx-conversation-abc"
)
```

### Example Interaction
1. **Client Request**:
   ```json
   {
     "jsonrpc": "2.0",
     "id": "req-001",
     "method": "message/send",
     "params": {
       "message": {
         "role": "user",
         "parts": [
           {"kind": "text", "text": "Highlight faces in this image"},
           {"kind": "file", "file": {"name": "input_image.png", "mimeType": "image/png", "bytes": "<base64_image>"}
         ],
         "messageId": "msg-001"
       }
     }
   }
   ```
2. **Agent Response**:
   ```json
   {
     "jsonrpc": "2.0",
     "id": "req-001",
     "result": {
       "id": "task-001",
       "contextId": "ctx-conversation-abc",
       "status": {"state": "completed", "timestamp": "2025-08-15T16:48:00Z"},
       "artifacts": [
         {
           "artifactId": "artifact-001",
           "name": "processed_image_with_faces.png",
           "parts": [
             {
               "kind": "file",
               "file": {
                 "name": "output.png",
                 "mimeType": "image/png",
                 "uri": "https://storage.example.com/processed/task-001/output.png?token=xyz"
               }
             }
           ]
         }
       ],
       "kind": "task"
     }
   }
   ```

---

## 📖 Key Takeaway

**Remember**: Multimodality empowers agents to handle diverse data types, making them more versatile and capable of real-world tasks. By mastering file exchange in A2A, you can build agents that seamlessly integrate text, images, and more, creating dynamic and interactive workflows! 🚀

### Concepts Demonstrated
- **Multimodal Inputs**: Handle `TextPart` and `FilePart` in a single message, enabling tasks like image analysis or modification.
- **Artifact Management**: Generate and return file-based artifacts (e.g., processed images) using A2A’s artifact system.
- **Task Continuity**: Use `contextId` to link related multimodal tasks (e.g., analyzing an image, then modifying it).
- **Human-Agent Synergy**: Support clarification requests (e.g., `input-required`) for ambiguous inputs, ensuring robust interactions.

### Ideas Shown
- **File Exchange**: Upload images as base64-encoded `FilePart` and return processed files as artifacts.
- **Task Lifecycle**: Start → Process multimodal input → Return artifacts → Handle follow-ups.
- **State Persistence**: Store task states and artifacts to support multi-turn, multimodal conversations.
- **Practical Use Cases**: Image analysis, content generation, or cross-modal tasks (e.g., text-to-image modifications).

### Resources to Learn More
- [A2A Specification: File Exchange](https://a2a-protocol.org/latest/specification/#96-file-exchange-upload-and-download)
- [A2A Task Lifecycle](https://a2a-protocol.org/latest/topics/life-of-a-task/)
