# 03: Exposing MCP Resources

**Objective:** Learn how to define and expose data as **MCP Resources**, which provide context or information to an AI agent without performing an action.

This tutorial focuses on creating both static and dynamic resources. Resources are the primary way to feed information (like file content, database records, or system status) into an AI's context.

## Key Concepts for Students

- **Resource vs. Tool:** This is a very important distinction!
    - **Resource (`resources/read`):** Is for *getting information*. Think of it like reading a file or looking up a fact. It should be "safe," meaning it doesn't change anything on the server.
    - **Tool (`tools/call`):** Is for *doing an action*. Think of it like sending an email or saving a file. It can change things on the server.
- **`@mcp.resource()` decorator:** Just like the tool decorator, this puts a "Read Me" sign on a function. It tells the server that this function can provide data for a specific URI.
- **URI (Uniform Resource Identifier):** This is just a unique name or address for a piece of data, like a web URL. We use them to ask for specific resources.
    - **Static URI:** `app:///messages/welcome` - Always points to the same thing.
    - **Templated URI:** `users://{user_id}/profile` - A pattern where you can fill in the blanks (like a user's ID) to get specific data.

## Project Structure

```
03_exposing_resources/
└── my_resources_server/
    ├── main.py         # The MCP server code with resource definitions
    └── call_mcp.py     # Our simple client to read the resources
```

## 1. The Server Code (`main.py`)

This server defines three different kinds of resources to show the flexibility of the system.

```python
# The full server code is in main.py. It defines three resources:
# 1. A static welcome message (always the same).
# 2. A dynamic message that shows the current server time.
# 3. A templated resource to fetch a user profile by their ID.
```

## 2. The Simplified Client (`call_mcp.py`)

This client shows how to first discover and then read all the different resources from our server.

```python
# The full, simplified client code is in the call_mcp.py file.
# It demonstrates the step-by-step process of listing and reading resources.
```

## 3. How to Run: A Step-by-Step Guide

This process is the same as the previous module. You will need two terminals.

### **Terminal 1: Start the Server**

1.  **Navigate to the directory:**
    ```bash
    cd 03_ai_protocols/02_model_context_protocol/01_server_development/03_exposing_resources/my_resources_server
    ```
2.  **Install libraries:** (If you haven't already from the last step)
    ```bash
    uv add httpx mcp uvicorn
    ```
3.  **Run the server:**
    ```bash
    uvicorn server:mcp_app --host 0.0.0.0 --port 8000
    ```
    The server is now running and waiting for the client.

### **Terminal 2: Run the Client**

1.  **Navigate to the *same* directory as Terminal 1:**
    ```bash
    cd 03_ai_protocols/02_model_context_protocol/01_server_development/03_exposing_resources/my_resources_server
    ```
2.  **Run the client:**
    ```bash
    uv run python client.py
    ```

## 4. What Happens When You Run the Client

The client will print a step-by-step explanation of its actions. This is the **Expected Output** in Terminal 2:

```
--- MCP Resource Client Demonstration for Students ---

[Step 1: Discovering Resources]
We ask the server what resources it has with a 'resources/list' request.
   -> Sending resources/list request...
   -> Success! Server has 3 resources:
      - app:///messages/welcome: A static welcome message.
      - app:///system/time: A dynamic JSON object with the current time.
      - users://{user_id}/profile: A template for a user's profile.

[Step 2: Reading a static resource]
Now, we'll read the 'app:///messages/welcome' resource.
   -> Sending resources/read request...
   -> Success! The server returned: 'Hello and welcome to the MCP Resource Server!'

[Step 3: Reading a dynamic resource]
Next, we'll read 'app:///system/time'. This one is generated on the fly.
   -> Sending resources/read request...
   -> Success! The server returned a JSON object:
      {"type": "json", "content": {"message": "Current server time.", "timestamp": "..."}}

[Step 4: Reading a templated resource]
Finally, we'll read 'users://jane.doe/profile' to get a specific user's data.
   -> Sending resources/read request...
   -> Success! The server returned the user profile:
      {"type": "json", "content": {"user_id": "jane.doe", "name": "Jane Doe", "role": "developer"}}
```

This example shows how you can provide an AI with different kinds of information—static, dynamic, and specific—by defining and exposing resources.
