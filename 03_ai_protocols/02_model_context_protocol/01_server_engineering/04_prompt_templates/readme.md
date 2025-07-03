# 04: Prompt Templates

**Objective:** Learn how to define and expose prompt templates, which are pre-defined, reusable prompts that a client can use to guide an LLM for common tasks.

Prompt templates allow a server to share its "expertise" by providing high-quality prompts that are optimized for specific tasks, saving the client from having to engineer them from scratch.

## Key MCP Concepts

-   **Prompt:** A structured set of messages (e.g., system, user, assistant) that can be sent to an LLM.
-   **`@mcp.prompt()` Decorator:** The `FastMCP` decorator for exposing a Python function as a prompt template.
-   **`prompts/list`:** The MCP method for a client to discover available prompt templates.
-   **`prompts/resolve`:** The MCP method for a client to "resolve" a template. The client provides the template name and arguments, and the server returns the fully-formed list of prompt messages.
-   **Function as Template:** With `FastMCP`, the function's parameters become the template's variables. The function body is responsible for returning the final, structured prompt messages.

## Implementation Plan

Inside the `my_prompts_server/` subdirectory:

-   **`server.py`:**
    -   We will define several functions decorated with `@mcp.prompt()`:
        -   A simple `summarize(text: str)` prompt that takes text and wraps it in a user message asking an LLM to summarize it.
        -   A more complex `debug_error(error_message: str, code_snippet: str)` prompt that constructs a detailed system and user message for debugging code.

-   **`client.py`:**
    -   The client will first call `prompts/list` to discover the available prompt templates.
    -   It will then call `prompts/resolve` for each template, providing sample arguments.
    -   The client will print the final, resolved list of messages it receives from the server, demonstrating how the template was filled in.

## Project Structure

```
04_prompt_templates/
└── my_prompts_server/
    ├── server.py         # The MCP server with prompt template definitions
    └── client.py     # Our simple client to get the formatted prompts
```

## 1. The Server Code (`server.py`)

This server defines two different prompt templates. One is very simple, and the other creates a more structured, conversational starting point.

## 2. The Simplified Client (`client.py`)

This client shows how to get the fully-formatted prompt messages from the server by providing the required arguments.

## 3. How to Run: A Step-by-Step Guide

You will need two separate terminals.

### **Terminal 1: Start the Server**

1.  **Navigate to the directory:**
    ```bash
    cd 03_ai_protocols/02_model_context_protocol/01_server_development/04_prompt_templates/my_prompts_server
    ```
2.  **Install libraries:** (If you haven't already)
    ```bash
    uv add httpx mcp uvicorn
    ```
3.  **Run the server:**
    ```bash
    uvicorn server:mcp_app --host 0.0.0.0 --port 8000
    ```
    The server is now running.

### **Terminal 2: Run the Client**

1.  **Navigate to the *same* directory as Terminal 1:**
    ```bash
    cd 03_ai_protocols/02_model_context_protocol/01_server_development/04_prompt_templates/my_prompts_server
    ```
2.  **Run the client:**
    ```bash
    uv run python client.py
    ```

## 4. What Happens When You Run the Client

The client will print a step-by-step explanation of its actions. This is the **Expected Output** in Terminal 2:

```
--- MCP Prompt Template Client Demonstration for Students ---

[Step 1: Discovering Prompt Templates]
We ask the server what prompt templates it has with a 'prompts/list' request.
   -> Sending prompts/list request...
   -> Success! Server has 2 prompt templates:
      - summarize: Creates a prompt asking an AI to summarize the provided text.
      - debug_error: Creates a prompt to help a user debug a code error.

[Step 2: Getting a simple text prompt]
Now, we'll get the 'summarize' prompt for a piece of text.
   -> Sending prompts/get request...
   -> Success! The server returned a list with 1 message(s):
[
  {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "Please summarize the following text in three bullet points:\n\n---\nThe quick brown fox jumps over the lazy dog.\n---"
      }
    ]
  }
]

[Step 3: Getting a multi-message conversation prompt]
Finally, let's get the 'debug_error' prompt to start a conversation.
   -> Sending prompts/get request...
   -> Success! The server returned a list with 2 message(s):
[
  {
    "role": "system",
    "content": [
      {
        "type": "text",
        "text": "You are a helpful debugging assistant, an expert in Python."
      }
    ]
  },
  {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "I encountered an error in my Python code. Can you help me?\nThe error was: TypeError: 'NoneType' object is not iterable"
      }
    ]
  }
]
```

This demonstrates how prompt templates allow you to programmatically build high-quality, structured inputs for an LLM from simple parameters.

## 5. Testing with Postman

For a more interactive testing experience, we've included a comprehensive Postman collection in the `postman/` directory:

- **Collection**: `MCP_Prompt_Templates.postman_collection.json`
- **Documentation**: `postman/README.md`

The Postman collection includes:
- Prompt template discovery requests
- Tests for simple prompt templates (single message output)
- Tests for complex prompt templates (multi-message conversations)
- Various content types (text, code, technical content)
- Error handling scenarios and edge cases
- Comprehensive explanations of ChatML format and message structures

This provides an excellent way to experiment with prompt templates and understand how they generate structured AI prompts.
