# 09: [Batching Requests](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#sending-messages-to-the-server) - Bug in S dK

> This is not yet implemented in MCP Python SDK - see this [Github Issue](https://github.com/modelcontextprotocol/python-sdk/issues/934).

**Objective:** Understand how to send multiple JSON-RPC requests in a single HTTP call to improve network efficiency.

Imagine an AI agent needs to perform three separate actions, like checking the weather, looking up a stock price, and getting a user's profile. Without batching, it would have to make three separate round trips to the server:

1.  Client -> Server (Get Weather)
2.  Server -> Client (Weather is "Sunny")
3.  Client -> Server (Get Stock Price)
4.  Server -> Client (Stock is "$150")
5.  Client -> Server (Get Profile)
6.  Server -> Client (Profile is "Alice")

Each of these trips has network latency. Batching allows us to combine all three requests into a single trip, which is dramatically more efficient.

## Key Concepts for Students

- **JSON Array of Requests:** A batched request is simply a standard JSON array where each element is a complete, independent JSON-RPC request object.
- **Single HTTP POST:** The client sends this entire array as the body of a single `HTTP POST` request.
- **JSON Array of Responses:** A compliant server will process all the requests in the batch and then return a single JSON array containing the response for each corresponding request.
- **Order is Preserved:** The spec recommends that the server process requests in order and that the response array should match the order of the request array. This makes it easy for the client to match responses to their original requests.
- **Notifications in a Batch:** A batch can also include notifications (requests without an `id`). The server processes them but does not include a response for them in the output array.