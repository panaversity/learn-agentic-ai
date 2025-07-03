# 03: Exposing Resources

**Objective:** Learn how to define and expose data as "resources" that an AI agent or user can read using the MCP `resources/` methods.

While tools are for *actions*, resources are for *information*. They allow a server to provide contextual data, such as file contents, database records, or real-time information, in a standardized way.

## Key MCP Concepts

-   **Resource:** A piece of data, identified by a URI, that a client can read.
-   **`@mcp.resource()` Decorator:** The `FastMCP` decorator used to expose a Python function as a data resource. The decorator takes the resource's `uri` and `description` as arguments.
-   **Resource URI:** A unique identifier for a resource (e.g., `app:///messages/welcome` or `users://jane.doe/profile`). URIs can be static or contain template placeholders.
-   **`resources/list`:** The MCP method for a client to discover all available resources a server provides.
-   **`resources/read`:** The MCP method for a client to fetch the content of a specific resource by its URI.
-   **Dynamic vs. Templated Resources:**
    -   A **dynamic resource** (e.g., `app:///system/time`) is generated on-the-fly every time it's read.
    -   A **templated resource** (e.g., `users://{user_id}/profile`) uses placeholders in its URI. `FastMCP` automatically maps parts of the requested URI to the function's arguments.

## Implementation Plan

Inside the `my_resources_server/` subdirectory:

-   **`server.py`:**
    -   We will define several resource-providing functions, each decorated with `@mcp.resource()`:
        -   A static resource that returns a fixed string.
        -   A dynamic resource that returns the current server time as a JSON object.
        -   A templated resource for user profiles, where `user_id` is extracted from the URI.

-   **`client.py`:**
    -   The client will first call `resources/list` to see all resource templates.
    -   It will then demonstrate calling `resources/read` for each type of resource: static, dynamic, and templated, printing the content it receives.

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

## 5. Testing with Postman

For a more interactive testing experience, we've included a comprehensive Postman collection in the `postman/` directory:

- **Collection**: `MCP_Exposing_Resources.postman_collection.json`
- **Documentation**: `postman/README.md`

The Postman collection includes:
- Resource discovery requests
- Tests for all three resource types (static, dynamic, templated)
- Multiple examples of templated resources with different user IDs
- Error handling scenarios
- Comprehensive explanations of resource vs tool concepts

This provides an excellent way to experiment with MCP resources and understand how they differ from tools.
