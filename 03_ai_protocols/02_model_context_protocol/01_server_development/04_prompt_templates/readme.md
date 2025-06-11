# 04: Using MCP Prompt Templates

**Objective:** Learn how to create and use **MCP Prompt Templates** to generate dynamic, structured prompts for an AI.

Prompt templates are reusable functions that construct sophisticated prompts from a few simple inputs. They are essential for standardizing interactions with an LLM and ensuring consistent, high-quality outputs. Think of them as a "mail merge" for talking to an AI.

## Key Concepts for Students

- **`@mcp.prompt()` decorator:** This decorator registers a Python function as a prompt template. Just like with tools, `FastMCP` inspects the function's signature to figure out what arguments it needs.
- **Why Use Templates?** Instead of manually typing `f"Please summarize this: {text}"` everywhere in your code, you create a central, reusable template. This is cleaner, less error-prone, and makes your prompts much easier to manage and improve over time.
- **ChatML Format:** The output of a prompt template is a list of messages in a standard format (called ChatML). This usually includes a `system` message (to set the AI's persona) and a `user` message (the actual request). This structure helps the AI understand the context and its role in the conversation.

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
